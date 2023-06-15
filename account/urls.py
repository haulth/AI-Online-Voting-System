from django.urls import path
from .views import *
from administrator import views

urlpatterns = [
    path('', account_login, name="account_login"),
    path('register/', account_register, name="account_register"),
    path('logout/', account_logout, name="account_logout"),
    path('upload_images/', upload_images, name="upload_images"),
    path('create_folder/', create_folder, name='create_folder'),
    path('ad_train/', ad_train, name='ad_train'),
    path('face_detection/', views.face_detection, name='face_detection'),
]
