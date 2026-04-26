from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=200, default="Python Course")
    description = models.TextField(default="Course Description")
    # price = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration = models.CharField(max_length=50, default="3 Months")
    image = models.ImageField(upload_to='courses/', null=True, blank=True)

    def __str__(self):
        return self.title


# Enrollment Model 
class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, null=True, blank=True)   # 🔥 OTP
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.course.title}"