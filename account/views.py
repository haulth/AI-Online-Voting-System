import base64
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect, reverse
from .email_backend import EmailBackend
from django.contrib import messages
from .forms import CustomUserForm
from voting.forms import VoterForm
from django.contrib.auth import login, logout
import cv2
import os
from administrator.utils import *
import numpy as np
# Create your views here.

def login_face(request):
    return render(request, 'voting/login_face.html')

def upload_image(request):
    print('oke2')
    if request.method == 'POST':
        print('oke1')
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
        print('oke')
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
            user = EmailBackend.authenticate(request, username=request.POST.get(
                'email'), password=request.POST.get('password'))
            if user != None:
                login(request, user)
                if user.user_type == '1':
                    return redirect(reverse("adminDashboard"))
                else:
                    return redirect(reverse("voterDashboard"))
            else:
                messages.error(request, "Thông tin không hợp lệ")
            
                #return redirect("/")
        elif request.method == 'POST' and 'image_data' in request.POST:
            # Decode the base64 image data
            image_data = request.POST['image_data']
            image_data = image_data.split(';base64,')[-1]
            image_data = base64.b64decode(image_data)
             # Convert the image data to a NumPy array
            nparr = np.frombuffer(image_data, np.uint8)
            # Decode the image array
            rgb = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # Read barcodes from the image
            #barcodes, imgbarcode = barcode_reader.read_barcodes(rgb)      
            # Detect faces in the frame
            faces, _= detector.get_faces(rgb)
            faces_found= faces.shape[0]
            if faces_found > 1:
                    messages.error(request, "Nhiều khuôn mặt được phát hiện")
                    print("Multiple faces detected")
                    return HttpResponse('fail')
                    return redirect("/")
            elif faces_found > 0:
                # Get the first face
                face = faces[0]
                x1, y1, x2, y2 = face[:4]

                # Get face image
                face_img = rgb[int(y1):int(y2), int(x1):int(x2), :]
                #lưu ảnh vào thư mục static

                # Get face embeddings
                embeddings = detector.get_embeddings(face_img)

                # Recognize face
                id, prob = recognizer.recognize_face(embeddings)
                if id == 'unknown':
                    messages.error(request, "Hãy cân chỉnh khuôn mặt của bạn và thực hiện lại")
                    return HttpResponse('fail')
                    return redirect("/")
                user = User.objects.get(id=id)
                login(request, user)
                return HttpResponse('success')
                if user.user_type == '1':
                    return redirect(reverse("adminDashboard"))
                else:
                    return redirect(reverse("voterDashboard"))
            else:
                messages.error(request, "Khuôn mặt chưa được đăng ký")
                return HttpResponse('fail')
                return redirect("/")

            # Return a JSON response indicating a successful upload
            return JsonResponse({'message': 'Image uploaded successfully'})

    return render(request, "voting/login.html", context)

# def account_register(request):
#     userForm = CustomUserForm(request.POST or None)
#     voterForm = VoterForm(request.POST or None)
    
#     context = {
#         'form1': userForm,
#         'form2': voterForm
#     }
    
#     if request.method == 'POST':
#         if userForm.is_valid() and voterForm.is_valid():
#             user = userForm.save(commit=False)
#             voter = voterForm.save(commit=False)
#             voter.admin = user
#             user.save()
#             voter.save()
#             user_id = user.id
#             context['user_id'] = user_id  # Thêm user_id vào context
            
#             return JsonResponse({'success': True, 'user_id': user_id})
#         else:
#             return JsonResponse({'success': False, 'errors': userForm.errors})
    
#     return render(request, "ad_reg.html", context)

# def create_folder(request):
#     folder_name = request.GET.get('name')
#     folder_path = os.path.join('./static/data/', folder_name)
#     if not os.path.exists(folder_path):
#         os.makedirs(folder_path)
#         print(folder_name)
#     return render(request, 'upload.html',{'folder_name': folder_name})
    
# def upload_images(request):
#     if request.method == 'POST':
#         folder_name = request.POST.get('folder_name')
#         folder_path = os.path.join('./static/data/', folder_name)
        
#         # Lưu hình ảnh vào thư mục
#         images = request.FILES.getlist('images[]')
#         for i, image_file in enumerate(images):
#             with open(os.path.join(folder_path, image_file.name), 'wb') as f:
#                 f.write(image_file.read())
        
#         messages.success(request, 'Đăng ký tài khoản thành công.')
#         return redirect('account_register')



def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Cảm ơn bạn đã ghé thăm chúng tôi!")
    else:
        messages.error(
            request, "Bạn cần phải đăng nhập.")

    return redirect(reverse("account_login"))
