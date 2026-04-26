from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random


# ✅ ROLE MODEL (instead of CustomUser)
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('student', 'Student'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return self.user.username


# ✅ OTP MODEL
class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)