from django.urls import path
from .views import *
from administrator import views

urlpatterns = [
    path('', account_login, name="account_login"),

    path('logout/', account_logout, name="account_logout"),


]
