from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from django.conf import settings
from django.http import HttpResponse
import cv2
import time
from datetime import datetime, timedelta
import os
from . import FacialRecognition 
from django.contrib import messages
import subprocess
from account.models import CustomUser as User
from .models import EmployeeDetail, Attendance
from voting.models import Voter
import threading
from django.shortcuts import redirect
import unidecode
import qrcode



currentPythonFilePath = os.getcwd()
cam2='rtsp://admin:L288159E@192.168.159.115:554/cam/realmonitor?channel=1@subtype=1'
<<<<<<< HEAD
cam1=0    
=======
cam1='rtsp://admin:L220C9F2@192.168.159.100:554/cam/realmonitor?channel=1@subtype=1'     
>>>>>>> 45b7fa4cca34c31607dfb7b1421630e6892a42a4
#sử dụng .replace('\\','/') để thay đổi dấu / đg dẫn.

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
# Load face detector and recognizer
detector = FacialRecognition.FaceDetector(
    minsize=20,
    threshold=[0.6, 0.7, 0.7],
    factor=0.709,
    gpu_memory_fraction=0.6,
    detect_face_model_path=currentPythonFilePath+'/static/align'.replace('\\','/'),
    facenet_model_path=currentPythonFilePath+'/static/Models/20180402-114759.pb'.replace('\\','/')
)
recognizer = FacialRecognition.FaceRecognition(classifier_path= currentPythonFilePath+'/static/Models/facemodel.pkl'.replace('\\','/'))
# Initialize barcode reader
barcode_reader = FacialRecognition.BarcodeReader(verbose=False)
fakedetector = FacialRecognition.FakeDetector(0.2,0.2)

#hàm mở camera và nhận diện khuôn mặt
def face_recognition(request):
    # Create named window
    cv2.namedWindow('Nhan Dien Khuon Mat')
    cap = cv2.VideoCapture(cam1)
    cap.set(cv2.CAP_PROP_FPS, 30)
    fresh = FreshestFrame(cap)
    if not cap.isOpened():
        return HttpResponse("Khong the mo camera")
    while True:
        try:
            ret, frame = fresh.read()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Read barcodes from the image
            barcodes, imgbarcode = barcode_reader.read_barcodes(rgb)      
            # Detect faces in the frame
            faces, _= detector.get_faces(rgb)
            for face in faces:
                x1, y1, x2, y2 = face[:4]

                # Get face image
                face_img = rgb[int(y1):int(y2), int(x1):int(x2), :]
                #lưu ảnh vào thư mục static
                

                # Get face embeddings
                embeddings = detector.get_embeddings(face_img)

                # Recognize face
                name, prob = recognizer.recognize_face(embeddings)
                cv2.imwrite(currentPythonFilePath+'/static/'+name+'.jpg'.replace('\\','/'),face_img)
                cv2.rectangle(imgbarcode, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(imgbarcode, "{} {:.2f}".format(name, prob), (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            cv2.imshow('Nhan Dien Khuon Mat', imgbarcode)
        except Exception as e:
            continue

        # Check if window is closed
        if cv2.getWindowProperty('Nhan Dien Khuon Mat', cv2.WND_PROP_VISIBLE) < 1:

            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return HttpResponse(name,barcodes)



#hàm date range
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)+1):
        yield start_date + timedelta(n)

def to_date_dmy(date):
    return datetime.strptime(date, '%d/%m/%Y')

def to_date_ymd(date):
    return datetime.strptime(date, '%Y-%m-%d')

def to_date_time(date):
    return datetime.strptime(date, '%d/%m/%Y %H:%M:%S')

def to_time(time):
    return datetime.strptime(time, '%H:%M:%S').time()

def calc_time(delta):
    return delta.total_seconds() / 3600

#hàm lấy ảnh từ video cách mỗi 10s 1 lần và lưu vào thư mục static, đọc video từ dường dẫn
     
def get_frame(request,path_video):
    # Create named window
    cv2.namedWindow('Lay Anh Tu Video')
    cap = cv2.VideoCapture(path_video)
    if not cap.isOpened():
        return HttpResponse("Không thể đọc video")
    count = 0
    while True:
        try:
            ret, frame = cap.read()
            #xác định thời gian hiện tại của video
            currentframe = cap.get(cv2.CAP_PROP_POS_MSEC)
        except Exception as e:
            continue

        # Check if window is closed
        if cv2.getWindowProperty('Lay Anh Tu Video', cv2.WND_PROP_VISIBLE) < 1:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return HttpResponse(count)

def face_detection(request):
    
    folder_name = request.GET.get('name')
    folder_path = os.path.join('./static/data/', folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        # messages.success(request, 'Tạo thư mục thành công')
    cv2.namedWindow('Phat Hien Khuon Mat')
    cap = cv2.VideoCapture(cam1)
    cap.set(cv2.CAP_PROP_FPS, 30)
    fresh = FreshestFrame(cap)
    if not cap.isOpened():
        return HttpResponse("Khong the mo camera")
    count = 0
    start = True
    folder_path = os.path.join(currentPythonFilePath, 'static', 'data', folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    while True:
        if count >= 10:
            messages.success(request, 'Có dữ liệu mới được thêm vào.')
            break
        try:
            ret, frame = fresh.read()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Detect faces in the frame
            faces, _ = detector.get_faces(rgb)

            for face in faces:
                faces_found= faces.shape[0]
                if start == True:
                    time.sleep(5)
                    start= False
                if faces_found > 1:
                        cv2.putText(rgb, "Chi Mot Khuon Mat", (0, 100), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                    1, (255, 255, 255), thickness=1, lineType=2)
                elif faces_found > 0:
                    x1, y1, x2, y2 = face[:4]
                    count += 1
                    # # Get face image
                    # face_img = rgb[int(y1):int(y2), int(x1):int(x2), :]
                    image_path = os.path.join(folder_path, folder_name +'_'+ str(count) + '.jpg')
                    cv2.imwrite(image_path, frame)
                    #draw bbox
                    show = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.imshow('Phat Hien Khuon Mat', show)
                    
        except Exception as e:
            continue

        # Check if window is closed
        if cv2.getWindowProperty('Phat Hien Khuon Mat', cv2.WND_PROP_VISIBLE) < 1:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    messages.success(request, 'Đăng ký tài khoản thành công.')
    return HttpResponse('success')
class FreshestFrame(threading.Thread):
	def __init__(self, capture, name='FreshestFrame'):
		self.capture = capture
		assert self.capture.isOpened()

		# this lets the read() method block until there's a new frame
		self.cond = threading.Condition()

		# this allows us to stop the thread gracefully
		self.running = False

		# keeping the newest frame around
		self.frame = None

		# passing a sequence number allows read() to NOT block
		# if the currently available one is exactly the one you ask for
		self.latestnum = 0

		# this is just for demo purposes		
		self.callback = None
		
		super().__init__(name=name)
		self.start()

	def start(self):
		self.running = True
		super().start()

	def release(self, timeout=None):
		self.running = False
		self.join(timeout=timeout)
		self.capture.release()

	def run(self):
		counter = 0
		while self.running:
			# block for fresh frame
			(rv, img) = self.capture.read()
			assert rv
			counter += 1

			# publish the frame
			with self.cond: # lock the condition for this operation
				self.frame = img if rv else None
				self.latestnum = counter
				self.cond.notify_all()

			if self.callback:
				self.callback(img)

	def read(self, wait=True, seqnumber=None, timeout=None):
		# with no arguments (wait=True), it always blocks for a fresh frame
		# with wait=False it returns the current frame immediately (polling)
		# with a seqnumber, it blocks until that frame is available (or no wait at all)
		# with timeout argument, may return an earlier frame;
		#   may even be (0,None) if nothing received yet

		with self.cond:
			if wait:
				if seqnumber is None:
					seqnumber = self.latestnum+1
				if seqnumber < 1:
					seqnumber = 1
				
				rv = self.cond.wait_for(lambda: self.latestnum >= seqnumber, timeout=timeout)
				if not rv:
					return (self.latestnum, self.frame)

			return (self.latestnum, self.frame)
def callback(img):
	cv2.imshow("realtime", img)
def train(request):
    currentPythonFilePath = os.getcwd().replace('\\','/')
    print('Current Python File Path: ', currentPythonFilePath)
    print('data augmentation')
    cmdAug= 'python "{}"/administrator/Data_Augmentation.py'.format(currentPythonFilePath)

    resultAug = subprocess.run(cmdAug, stdout=subprocess.PIPE, shell=True)

    print(resultAug.stdout)
    print('align dataset')
    
    cmdAlign = 'python "{}"/administrator/align_dataset_mtcnn.py "{}"/static/data_process/raw/ "{}"/static/data_process/process/ "{}"/static/align --image_size 160 --margin 32 --random_order --gpu_memory_fraction 0.25'.format(currentPythonFilePath, currentPythonFilePath, currentPythonFilePath, currentPythonFilePath)

    resultAlign = subprocess.run(cmdAlign, stdout=subprocess.PIPE, shell=True)

    print(resultAlign.stdout)

    print('train classifier')

    cmdClass = 'python "{}"/administrator/classifier.py TRAIN "{}"/static/data_process/process "{}"/static/Models/20180402-114759.pb "{}"/static/Models/facemodel.pkl --batch_size 1000'.format(currentPythonFilePath, currentPythonFilePath, currentPythonFilePath, currentPythonFilePath)

    resultClass = subprocess.run(cmdClass, stdout=subprocess.PIPE, shell=True)

    # Print the output of the subprocess
    print(resultClass.stdout)
    train_datetime = datetime.now()

# Định dạng ngày tháng năm theo định dạng Việt Nam (dd/mm/yyyy)
    date_str = train_datetime.strftime("%d/%m/%Y")

    # Định dạng giờ theo định dạng 24 giờ (HH:MM)
    time_str = train_datetime.strftime("%H:%M")

    voters = Voter.objects.all()
    #count voter
    count = 0
    for voter in voters:
        count += 1


    # Ghi thông tin vào file
    with open('train_time.txt', 'a',encoding='utf-8') as file:
        file.write(f'Huấn luyện vào ngày: {date_str} {time_str} Có {count} người được đào tạo\n')
    # Return a success response
    messages.success(request, 'Train dữ liệu thành công.')
    return HttpResponse('success')

def create_qrcode(text):
    # Tạo đối tượng QR code
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # Thêm dữ liệu vào QR code
    qr.add_data(text)
    qr.make(fit=True)

    # Tạo ảnh QR code từ đối tượng QR code
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Lưu ảnh QR code thành file tại thư mục 'static/images/qrcode'
    save_path = os.path.join('static/images/qrcode', f'{text}.png')
    save_path = save_path.replace('\\', '/')  # Thay thế ký tự '\' bằng '/'
    file_path = os.path.join(settings.BASE_DIR, 'qrcode_path.txt')

    qr_image.save(save_path)

    return save_path

# The class Camera_feed_identified initializes a video feed and recognizes employees in the feed using
# a dictionary of employee codes and names.
    
class Camera_feed_identified():
    def __init__(self):
        self.video = cv2.VideoCapture(cam1)
        self.video.set(cv2.CAP_PROP_FPS, 30)
        self.is_running = True
        self.fresh =FreshestFrame(self.video)
        (self.grabbed, self.frame) = self.fresh.read()
        self.recognized_records = {}
        self.expiration_time = 24 * 60  
        ids = User.objects.all()
        print(ids)
        self.voters_dict = {}
        for id in ids:
            self.voters_dict[id.get_id()] = id.get_full_name()
        #threading dung de chay song song voi chuong trinh chinh
        self.th = threading.Thread(target=self.update, args=())
        self.th.setDaemon(True)
        self.th.start()

    def release(self, timeout=None):
        self.running = False
        self.join(timeout=timeout)
        self.fresh.release()

    def get_name(self, id):
        return self.voters_dict.get(id)
    
    def remove_diacritics(self, text):
        text = unidecode.unidecode(text)
        return text

    def stop(self):
        
        self.is_running = False
        self.video.release()

    def get_frame(self):
        try:
            image = self.frame
            #chuyển về màu RGB
            _, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()
        except:
            pass
    
    def perform_attendance(self,id, name):
        #kiểm tra xem đã điểm danh chưa
        attendances = Attendance.objects.filter(userid=id, date=datetime.now().date())
        print(attendances.count()  )
        if attendances.count()==0:           
            attendance = Attendance.objects.create(
                userid=id,
                date=datetime.now().date(),
                time_in=datetime.now().time(),
            )
            attendance.save()
            return name
        else:
            return "Da diem danh"

    def check_duplicate_attendance(self, code):
        current_time = time.time()

        if code in self.recognized_records:
            last_detection_time = self.recognized_records[code]
            time_since_last_detection = current_time - last_detection_time   
            # Kiểm tra xem đã qua 3 phút hay chưa
            if time_since_last_detection < self.expiration_time:
                return True  # Đã xác định điểm danh trùng lặp
        self.recognized_records[code] = current_time
        return False  # Chưa xác định điểm danh trùng lặp
    
    def update(self):    
        # start= True
        count = 0
        while self.is_running:
            try:
                grabbed, frame = self.video.read()
                if not grabbed:
                    break
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Đọc mã vạch từ hình ảnh
                barcodes, x, y, w, h = barcode_reader.read_barcodes(rgb)
                
                if barcodes:
                    # Lấy mã vạch cuối cùng
                    code = barcodes[-1]

                    # Lấy tên từ mã vạch
                    name = self.get_name(int(code))
                    if name is not None:
                        # Kiểm tra và xử lý điểm danh trùng lặp
                        if self.check_duplicate_attendance(code)==False:                 
                            name=self.perform_attendance(code,name)
                        
                        name = self.remove_diacritics(name)
                        cv2.putText(frame, name, (x[-1], y[-1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        cv2.rectangle(frame, (x[-1], y[-1]), (x[-1] + w[-1], y[-1] + h[-1]), (0, 255, 0), 2)
                    else:
                        name = 'Khong co trong he thong'
                        cv2.putText(frame, name, (x[-1], y[-1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        cv2.rectangle(frame, (x[-1], y[-1]), (x[-1] + w[-1], y[-1] + h[-1]), (0, 255, 0), 2)
                
                # Phát hiện khuôn mặt trong khung
                faces, _ = detector.get_faces(rgb)
                # if start:
                #     time.sleep(2)
                #     start = False
                for face in faces:
                    x1, y1, x2, y2 = face[:4]
                    
                    # cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    
                    # eye_points , is_blink = fakedetector.detect_blink(rgb, x1, y1, x2, y2, 0.2, 0.3)
                    # if is_blink:
                    #     count += 1
                    #     cv2.putText(frame, "Nham mat: "+str(count), (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    # if count == 3:
                        # Lấy ảnh khuôn mặt
                    face_img = rgb[int(y1):int(y2), int(x1):int(x2), :]
                    
                    # Lấy embedding của khuôn mặt
                    embeddings = detector.get_embeddings(face_img)
                    
                    # Nhận dạng khuôn mặt
                    id, prob = recognizer.recognize_face(embeddings)
                    
                    if id != 'unknown':
                        name = self.get_name(int(id))
                        if name is not None:       
                            if self.check_duplicate_attendance(id)==False:
                                name=self.perform_attendance(id,name)                               
                            else:                            
                                cv2.putText(frame, "Ban da check in roi", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                                name = 'Da diem danh'
                            # Bỏ qua điểm danh nếu đã được thực hiện trong khoảng thời gian quy định
                            name = self.remove_diacritics(name)
                            count = 0
                        else:
                            name = 'Khong xac dinh'
                    else:
                        name = 'Khong xac dinh'
                    
                    # Vẽ hình chữ nhật và tên
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    if name == 'Khong xac dinh':
                        name = 'Khong co trong he thong'
                        cv2.putText(frame, "{}".format(name), (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    else:
                        cv2.putText(frame, "{} {:.2f}".format(name, prob), (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


                self.frame = frame
                self.grabbed = grabbed
            
            except Exception as e:
                print(e)
                try:
                    grabbed, frame = self.video.read()
                    self.frame = frame
                    self.grabbed = grabbed
                except:
                    pass
            
        
            

def Gender_frame(camera):
    while camera.is_running:
        try:
            frame = camera.get_frame()        
            yield (b'--frame\r\n'
                 b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        except GeneratorExit: 
            break
            
        except:
            pass
