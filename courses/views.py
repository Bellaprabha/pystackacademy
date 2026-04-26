from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment

# DRF (JWT)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# 📚 Course List
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})


# 📄 Course Detail (Clean version - ONLY ONE)
@login_required(login_url='/login/')
def course_detail(request, id):
    course = get_object_or_404(Course, id=id)
    return render(request, 'courses/course_detail.html', {'course': course})


# 🎓 My Courses
@login_required(login_url='/login/')
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user)
    return render(request, 'courses/my_courses.html', {'enrollments': enrollments})


# 🔒 Course Content (Access Control)
@login_required
def course_content(request, id):
    course = get_object_or_404(Course, id=id)

    # Check if user purchased course
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        return redirect('/courses/')

    return render(request, 'courses/content.html', {'course': course})


# 🔐 JWT Protected API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_courses_api(request):
    enrollments = Enrollment.objects.filter(user=request.user)
    data = []

    for e in enrollments:
        data.append({
            "course": e.course.title,
            "duration": e.course.duration
        })

    return Response(data)