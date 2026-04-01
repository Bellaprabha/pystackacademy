import random
from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment
from django.contrib.auth.decorators import login_required

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})


def course_detail(request, id):
    course = get_object_or_404(Course, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')

        otp = str(random.randint(100000, 999999))

        enrollment = Enrollment.objects.create(
            name=name,
            phone=phone,
            course=course,
            otp=otp
        )

        print("OTP:", otp)  # 🔥 for testing

        return redirect(f'/verify-otp/{enrollment.id}/')

    return render(request, 'courses/course_detail.html', {'course': course})



@login_required(login_url='/login/')
def course_detail(request, id):
    course = get_object_or_404(Course, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')

        Enrollment.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            course=course
        )

        return redirect('/success/')

    return render(request, 'courses/course_detail.html', {'course': course})



def verify_otp(request, id):
    enrollment = get_object_or_404(Enrollment, id=id)

    if request.method == 'POST':
        user_otp = request.POST.get('otp')

        if user_otp == enrollment.otp:
            enrollment.is_verified = True
            enrollment.save()
            return redirect('/success/')
        else:
            return render(request, 'courses/verify_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'courses/verify_otp.html')