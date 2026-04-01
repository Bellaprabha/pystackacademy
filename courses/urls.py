from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:id>/', views.course_detail, name='course_detail'),
    path('verify-otp/<int:id>/', views.verify_otp, name='verify_otp'),
]