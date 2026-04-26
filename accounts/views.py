import random
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from courses.models import Enrollment
from .models import EmailOTP
from django.conf import settings


# ✅ REGISTER (OTP BASED)
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not username or not email or not password:
            messages.error(request, "All fields required")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        # Create user (inactive)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
        )

        # 🔥 Generate OTP
        otp = str(random.randint(100000, 999999))

        EmailOTP.objects.create(user=user, otp=otp)

        # 🔥 Send OTP
        send_mail(
            'Your OTP Code',
            f'Your OTP is: {otp}',
            'your_email@gmail.com',
            [email],
            fail_silently=True,  # avoid crash
        )

        # store user in session
        # request.session['user_id'] = user.id
        request.session['otp_user'] = user.username

        return redirect('verify_otp')

    return render(request, 'accounts/register.html')


from django.contrib.auth import get_user_model
User = get_user_model()

def verify_otp(request):
    username = request.session.get('otp_user')

    if not username:
        return redirect('register')

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('register')

    if request.method == "POST":
        otp = request.POST.get('otp')

        # email_otp = EmailOTP.objects.get(user=user)
        email_otp = EmailOTP.objects.filter(user=user).first()

        if not email_otp:
            return render(request, 'accounts/verify_otp.html', {
                'error': 'OTP not found'
        })

        if email_otp.otp == otp:
            user.is_active = True
            user.save()

            # साफ session
            del request.session['otp_user']

            return redirect('login')
        else:
            return render(request, 'accounts/verify_otp.html', {
                'error': 'Invalid OTP'
            })

    return render(request, 'accounts/verify_otp.html')

def resend_otp(request):
    username = request.GET.get('username')

    user = User.objects.get(username=username)
    email_otp, created = EmailOTP.objects.get_or_create(user=user)

    # 🔁 Generate new OTP
    email_otp.generate_otp()

    # 📧 Send again
    send_mail(
        'Your New OTP Code',
        f'Your new OTP is {email_otp.otp}',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )

    return render(request, 'accounts/verify_otp.html', {
        'message': 'New OTP sent successfully!',
        'username': username
    })

# ✅ LOGIN
def login_view(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                error = "Verify your account first!"
            else:
                login(request, user)
                return redirect('/courses/')
        else:
            error = "Invalid credentials"

    return render(request, 'accounts/login.html', {'error': error})


# ✅ LOGOUT
def logout_view(request):
    logout(request)
    return redirect('/')


# ✅ MY COURSES
@login_required(login_url='/accounts/login/')
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user)
    return render(request, 'accounts/my_courses.html', {'enrollments': enrollments})