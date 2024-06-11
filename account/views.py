import base64
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, reverse
from .email_backend import EmailBackend
from django.contrib import messages
from django.contrib.auth import login, logout
import cv2
import os
from administrator.utils import *
import numpy as np
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash


@login_required
def change_pass(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']     
        user = request.user       
        # Kiểm tra mật khẩu hiện tại
        if user.check_password(current_password):
            # Thay đổi mật khẩu mới
            user.set_password(new_password)
            user.save()
            # Cập nhật session auth
            update_session_auth_hash(request, user)
            # Đăng xuất người dùng
            messages.success(request, 'Đổi mật khẩu thành công. Vui lòng đăng nhập lại.')
            logout_url = reverse('account_logout')
            return redirect(logout_url)
        else:
            messages.error(request, 'Mật khẩu hiện tại không chính xác.')
            return redirect('bio.html')

    return render(request, 'bio.html')

def login_face(request):
    return render(request, 'voting/login_face.html')

def upload_image(request):
    if request.method == 'POST':
        image_base64 = request.POST.get('image')
        print (image_base64)
        image_data = base64.b64decode(image_base64.split(',')[-1])
        print (image_data)
        #lưu ảnh vào thư mục hiện tại + static/images
        path= os.path.join(currentPythonFilePath, 'static/images')
        #tạo tên file ảnh
        image_name= 'demo.jpg'
        #ghi file ảnh
        with open(os.path.join(path, image_name), 'wb') as f:
            f.write(image_data)
        #đọc file ảnh
        img = cv2.imread(os.path.join(path, image_name))
        #show ảnh
        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


        return HttpResponse('Ảnh đã được nhận và lưu trữ thành công.')

    # Phản hồi mặc định nếu không có yêu cầu POST
    return HttpResponseBadRequest('Yêu cầu không hợp lệ.')

def account_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("adminDashboard"))
        else:
            return redirect(reverse("voterDashboard"))

    context = {}
    if request.method == 'POST':
        if request.POST.get('email') and request.POST.get('password'):
            user = EmailBackend.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
            if user is not None:
                login(request, user)
                if user.user_type == '1':
                    return redirect(reverse("adminDashboard"))
                else:
                    return redirect(reverse("voterDashboard"))
            else:
                messages.error(request, "Thông tin không hợp lệ")
                return redirect("/")
        
        elif 'image_data' in request.POST:
            try:
                # Decode the base64 image data
                image_data = request.POST['image_data']
                image_data = image_data.split(';base64,')[-1]
                image_data = base64.b64decode(image_data)

                # Convert the image data to a NumPy array
                nparr = np.frombuffer(image_data, np.uint8)
                # Decode the image array
                rgb = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                # Detect faces in the frame
                faces, _ = detector.get_faces(rgb)
                faces_found = faces.shape[0]

                if faces_found > 1:
                    messages.error(request, "Nhiều khuôn mặt được phát hiện")
                    return HttpResponse('fail')

                elif faces_found > 0:
                    # Get the first face
                    face = faces[0]
                    x1, y1, x2, y2 = face[:4]

                    # Get face image
                    face_img = rgb[int(y1):int(y2), int(x1):int(x2), :]

                    # Get face embeddings
                    embeddings = detector.get_embeddings(face_img)

                    # Recognize face
                    id, prob = recognizer.recognize_face(embeddings)
                    print(f"Recognized ID: {id}, Probability: {prob}")
                    if id == 'unknown':
                        messages.error(request, "Hãy cân chỉnh khuôn mặt của bạn và thực hiện lại")
                        return HttpResponse('fail')

                    try:
                        user = User.objects.get(id=id)
                        login(request, user)
                        if user.user_type == '1':
                            return redirect(reverse("adminDashboard"))
                        else:
                            return redirect(reverse("voterDashboard"))
                    except User.DoesNotExist:
                        messages.error(request, "Khuôn mặt chưa được đăng ký")
                        return HttpResponse('fail')

                else:
                    messages.error(request, "Khuôn mặt chưa được đăng ký")
                    return HttpResponse('fail')

            except Exception as e:
                messages.error(request, f"Đã xảy ra lỗi: {str(e)}")
                return HttpResponse('fail')

    return render(request, "voting/login.html", context)



def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Cảm ơn bạn đã ghé thăm chúng tôi!")
    else:
        messages.error(
            request, "Bạn cần phải đăng nhập.")

    return redirect(reverse("account_login"))
