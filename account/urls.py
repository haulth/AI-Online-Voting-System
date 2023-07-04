from django.urls import path
from .views import *
from administrator import views

urlpatterns = [
    path('', account_login, name="account_login"),

    path('logout/', account_logout, name="account_logout"),
    path('upload_image/', upload_image, name='upload_image'),
    path('login_face/', login_face, name='login_face'),
    path('change_pass/', change_pass, name="change_pass"),

]
