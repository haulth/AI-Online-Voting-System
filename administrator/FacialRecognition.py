from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from imutils.video import VideoStream
from typing import List, Tuple
import argparse
from . import facenet

import pickle
#from django.conf.urls.static import static
from . import detect_face 
import numpy as np
import cv2
from sklearn.svm import SVC
from pyzbar.pyzbar import decode
import dlib
import os
import math

currentPythonFilePath = os.getcwd()
# Tải pre-trained facial landmark predictor của dlib
class FakeDetector:
    def __init__(self, left_eye_threshold: float = 0.2, right_eye_threshold: float = 0.2):
        self.right_eye_threshold = right_eye_threshold
        self.left_eye_threshold = left_eye_threshold
        self.face_detector = FaceDetector(
                                            minsize=20,
                                            threshold=[0.6, 0.7, 0.7],
                                            factor=0.709,
                                            gpu_memory_fraction=0.6,
                                            detect_face_model_path=currentPythonFilePath+'/static/align'.replace('\\','/'),
                                            facenet_model_path=currentPythonFilePath+'/static/Models/20180402-114759.pb'.replace('\\','/')
                                        )
        self.landmark_predictor = dlib.shape_predictor("./static/Models/shape_predictor_68_face_landmarks.dat")

    @staticmethod
    def rect_to_bb(rect):
        x = rect.left()
        y = rect.top()
        w = rect.right() - x
        h = rect.bottom() - y
        return x, y, w, h

    @staticmethod
    def calculate_ear(eye_points):
        eye_width = np.linalg.norm(eye_points[0] - eye_points[3])
        eye_height1 = np.linalg.norm(eye_points[1] - eye_points[5])
        eye_height2 = np.linalg.norm(eye_points[2] - eye_points[4])
        ear = (eye_height1 + eye_height2) / (2.0 * eye_width)
        return ear
    
    # Hàm tính góc xoay của khuôn mặt
    def calculate_face_rotation_angle(face_landmarks):
        # Lấy các điểm mắt
        left_eye = face_landmarks.part(36)
        right_eye = face_landmarks.part(45)

        # Tính toán góc giữa hai điểm mắt
        dx = right_eye.x - left_eye.x
        dy = right_eye.y - left_eye.y

        # Chuyển đổi sang góc radian
        angle_rad = math.atan2(dy, dx)

        # Chuyển đổi sang độ
        angle_deg = math.degrees(angle_rad)

        return angle_deg

    # Hàm xác định hướng xoay của khuôn mặt
    def determine_face_rotation(angle):
        threshold = 10  # Ngưỡng tùy chỉnh

        if angle < -threshold:
            return "left"
        elif angle > threshold:
            return "right"
        else:
            return "nothing"
    def bbox_to_rect(x, y, w, h):
        return dlib.rectangle(int(x), int(y), int(w), int(h))
        
    def detect_blink(self, frame, x1, y1, w1, h1, leftthreshold, rightthreshold):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        eye_points = []
        blink_detected = False
        face_rect = self.bbox_to_rect(x1, y1, w1, h1)
        landmarks = self.landmark_predictor(gray, face_rect)

        landmarks = np.array([[p.x, p.y] for p in landmarks.parts()], dtype=np.int32)

        left_eye_ear = self.calculate_ear(landmarks[36:42])
        right_eye_ear = self.calculate_ear(landmarks[42:48])

        eye_points.append({
            'left_eye_ear': landmarks[36:42],
            'right_eye_ear': landmarks[42:48]
        })

        if left_eye_ear < leftthreshold or right_eye_ear < rightthreshold:
            blink_detected = True

        return  eye_points, blink_detected

class FaceDetector:
    def __init__(self, minsize: int, threshold: List[float], factor: float, gpu_memory_fraction: float, detect_face_model_path: str, facenet_model_path: str):
        self.minsize = minsize
        self.INPUT_IMAGE_SIZE=160
        self.threshold = threshold
        self.factor = factor
        facenet.load_model(facenet_model_path)
        self.gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
        self.sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=self.gpu_options, log_device_placement=False))
        self.pnet, self.rnet, self.onet = self.create_mtcnn(detect_face_model_path)
        self.images_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
        self.embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")
        self.phase_train_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("phase_train:0")
        self.embedding_size = self.embeddings.get_shape()[1]

    def create_mtcnn(self, detect_face_model_path: str) -> Tuple:
        with tf.Graph().as_default():
            gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.6)
            sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
            with sess.as_default():
                return detect_face.create_mtcnn(sess, detect_face_model_path)

    def get_faces(self, frame: np.ndarray) -> List:
        return detect_face.detect_face(frame, self.minsize, self.pnet, self.rnet, self.onet, self.threshold, self.factor)

    def get_embeddings(self, face: np.ndarray) -> np.ndarray:
        scaled = cv2.resize(face, (self.INPUT_IMAGE_SIZE, self.INPUT_IMAGE_SIZE), interpolation=cv2.INTER_CUBIC)
        scaled = facenet.prewhiten(scaled)
        scaled_reshape = scaled.reshape(-1, self.INPUT_IMAGE_SIZE, self.INPUT_IMAGE_SIZE, 3)
        feed_dict = {self.images_placeholder: scaled_reshape, self.phase_train_placeholder: False}
        return self.sess.run(self.embeddings, feed_dict=feed_dict)


class FaceRecognition:
    def __init__(self, classifier_path: str):
        with open(classifier_path, 'rb') as file:
            self.model, self.class_names = pickle.load(file)
        print("Custom Classifier, Successfully loaded")

    def recognize_face(self, embeddings: np.ndarray, threshold: float = 0.7) -> Tuple[str, float]:
        predictions = self.model.predict_proba(embeddings)
        best_class_indices = np.argmax(predictions, axis=1)
        best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]
        best_name = self.class_names[best_class_indices[0]] if best_class_probabilities[0] > threshold else "unknown"
        return best_name, float(best_class_probabilities[0])

class BarcodeReader:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def read_barcodes(self, frame: np.ndarray) -> List[str]:
        # draw bounding box around barcode and display barcode type and data to terminal
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #lật ảnh
        frame = cv2.flip(frame, 1)
        decoded_objs = decode(frame)
        barcodes = []
        x_list = []
        y_list = []
        w_list = []
        h_list = []
        
        for obj in decoded_objs:
            barcodes.append(obj.data.decode('utf-8'))
            # Draw bounding box around barcode
            obj_x, obj_y, obj_w, obj_h = obj.rect
            x_list.append(obj_x)
            y_list.append(obj_y)
            w_list.append(obj_w)
            h_list.append(obj_h)
        
        return barcodes, x_list, y_list, w_list, h_list

def main(args):
    # Load face detector and recognizer
    detector = FaceDetector(
    minsize=args["minsize"],
    threshold=args["threshold"],
    factor=args["factor"],
    gpu_memory_fraction=args["gpu_memory_fraction"],
    detect_face_model_path=args["detect_face_model_path"],
    facenet_model_path=args["facenet_model_path"]
    )
    recognizer = FaceRecognition(classifier_path=args["classifier_path"])
    # Initialize barcode reader
    barcode_reader = BarcodeReader(verbose=args["verbose"])

    # Start video stream
    print("[INFO] Starting video stream...")
    vs = VideoStream(src=args["video_path"]).start()

    # Loop over frames from the video stream
    while True:
        # Read the next frame from the video stream
        frame = vs.read()

        # If the frame is None, then we have reached the end of the stream
        if frame is None:
            break
        # Chuyển đổi frame sang định dạng grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces in the frame
        faces, _= detector.get_faces(rgb)

        # Loop over detected faces
        
        for face in faces:
            try:
                print (face[:4])
                # Get face coordinates
                x1, y1, x2, y2 = face[:4]

                # Get face image
                face_img = rgb[int(y1):int(y2), int(x1):int(x2), :]

                # Get face embeddings
                embeddings = detector.get_embeddings(face_img)

                # Recognize face
                name, prob = recognizer.recognize_face(embeddings)

                # Draw face bounding box and name
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, "{} {:.2f}".format(name, prob), (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            except:
                pass

        # Read barcodes from the frame
        barcodes = barcode_reader.read_barcodes(frame)

        # Show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # If the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    # Stop the video stream and close all windows
    vs.stop()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--minsize', type=int, default=20, help='Minimum size of face to detect')
    parser.add_argument('--threshold', type=list, default=[0.6, 0.7, 0.7], help='Threshold for the MTCNN model')
    parser.add_argument('--factor', type=float, default=0.709, help='Scale factor for the MTCNN model')
    parser.add_argument('--gpu_memory_fraction', type=float, default=0.6, help='GPU memory fraction to allocate')
    parser.add_argument('--detect_face_model_path', type=str, default='./src/align',
    help='Path to the MTCNN face detection model')
    parser.add_argument('--facenet_model_path', type=str, default='./static/Models/20180402-114759.pb',
    help='Path to the facenet model')
    parser.add_argument('--classifier_path', type=str, default='./static/Models/facemodel.pkl',
    help='Path to the classifier model')
    parser.add_argument('--video_path', type=str, default=0, help='Path to the input video')
    parser.add_argument('--verbose', type=bool, default=True, help='Enable verbose mode')
    main(vars(parser.parse_args()))
