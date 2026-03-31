# from django.db import models

# class Course(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     price = models.IntegerField()

#     def __str__(self):
#         return self.name

from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'