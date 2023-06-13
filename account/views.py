from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from .email_backend import EmailBackend
from django.contrib import messages
from .forms import CustomUserForm
from voting.forms import VoterForm
from django.contrib.auth import login, logout

import os
# Create your views here.


def account_login(request):
    
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("adminDashboard"))
        else:
            return redirect(reverse("voterDashboard"))

    context = {}
    if request.method == 'POST':
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
            return redirect("/")

    return render(request, "voting/login.html", context)

def account_register(request):
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    
    context = {
        'form1': userForm,
        'form2': voterForm
    }
    
    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            user_id = user.id
            context['user_id'] = user_id  # Thêm user_id vào context
            
            return JsonResponse({'success': True, 'user_id': user_id})
        else:
            return JsonResponse({'success': False, 'errors': userForm.errors})
    
    return render(request, "ad_reg.html", context)

def create_folder(request):
    folder_name = request.GET.get('name')
    folder_path = os.path.join('./static/data/', folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(folder_name)
    return render(request, 'upload.html',{'folder_name': folder_name})
    
def upload_images(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        folder_path = os.path.join('./static/data/', folder_name)
        
        # Lưu hình ảnh vào thư mục
        images = request.FILES.getlist('images[]')
        for i, image_file in enumerate(images):
            with open(os.path.join(folder_path, image_file.name), 'wb') as f:
                f.write(image_file.read())
        
        messages.success(request, 'Đăng ký tài khoản thành công.')
        return redirect('account_register')



def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Cảm ơn bạn đã ghé thăm chúng tôi!")
    else:
        messages.error(
            request, "Bạn cần phải đăng nhập.")

    return redirect(reverse("account_login"))
