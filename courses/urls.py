from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('my-courses/', views.my_courses, name='my_courses'),

    path('content/<int:id>/', views.course_content, name='course_content'), 
    path('<int:id>/', views.course_detail, name='course_detail'),            

    # path('verify-otp/<int:id>/', views.verify_otp, name='verify_otp'),
    path('api/my-courses/', views.my_courses_api),
]