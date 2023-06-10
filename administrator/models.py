from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from account.models import CustomUser


class Attendance(models.Model):
    #user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    userid = models.CharField(max_length=10)
    date = models.DateField(auto_now_add=True)
    time_in = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.user.last_name + " " + self.user.first_name + " " + str(self.date)
    
    #hàm xóa toàn bộ dữ liệu trong bảng
    def delete_all(self):
        Attendance.objects.all().delete()