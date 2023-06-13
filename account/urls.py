from django.urls import path
from . import views


urlpatterns = [
    path('', views.account_login, name="account_login"),
    path('register/', views.account_register, name="account_register"),
    path('logout/', views.account_logout, name="account_logout"),
    path('upload_images/', views.upload_images, name="upload_images"),
    path('create_folder/', views.create_folder, name='create_folder')
]
