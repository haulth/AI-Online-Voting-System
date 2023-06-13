from django.db import models
from django.conf import settings

class EmployeeDetail(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    emcode=models.CharField(max_length=50)
    address=models.CharField(max_length=50)
    department=models.CharField(max_length=50)
    gender=models.CharField(max_length=10)
    def __str__(self): 
        return self.user.username
    
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

