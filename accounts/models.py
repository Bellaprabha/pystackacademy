from django.db import models
from django.contrib.auth.models import User
import random

class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()
        
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)    