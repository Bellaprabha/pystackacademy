from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail

from courses.models import Enrollment
from .tokens import email_token_generator


# ✅ REGISTER WITH EMAIL LINK
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not username or not email or not password:
            messages.error(request, "All fields are required")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False  # 🚨 VERY IMPORTANT
        )

        # 🔥 Generate token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_token_generator.make_token(user)

        # 🔥 Create verification link
        link = request.build_absolute_uri(
            reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
        )

        # 🔥 Send email
        send_mail(
            'Verify your account',
            f'Click this link to verify your account:\n{link}',
            'your_email@gmail.com',
            [email],
            fail_silently=False,
        )

        messages.success(request, "Check your email to verify your account")
        return redirect('login')

    return render(request, 'accounts/register.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')   
        password = request.POST.get('password')

        if not username:
            messages.error(request, "Username is required")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
        )

        messages.success(request, "User created successfully")
        return redirect('login')

    return render(request, 'accounts/register.html')

# ✅ VERIFY EMAIL
def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user and email_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account verified! Please login")
        return redirect('login')
    else:
        return render(request, 'accounts/verify_failed.html')


# ✅ LOGIN
def login_view(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                error = "Please verify your email first!"
            else:
                login(request, user)
                return redirect('/courses/')
        else:
            error = "Invalid username or password"

    return render(request, 'accounts/login.html', {'error': error})


@login_required(login_url='/login/')
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user)
    return render(request, 'accounts/my_courses.html', {'enrollments': enrollments})


def logout_view(request):
    logout(request)
    return redirect('/')

# from django.contrib.auth.forms import UserCreationForm
# from django.shortcuts import render, redirect

# # ✅ Import Enrollment (new)
# from courses.models import Enrollment
# from django.contrib.auth import authenticate, login
# from django.contrib.auth import logout
# from django.contrib.auth.decorators import login_required

# # ✅ Register
# def register_view(request):
#     form = UserCreationForm()

#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('/login/')

#     return render(request, 'accounts/register.html', {'form': form})


# # ✅ Login
# # def login_view(request):
# #     return render(request, 'accounts/login.html')
# def login_view(request):
#     error = None

#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             return redirect('/courses/')
#         else:
#             error = "Invalid username or password.if you don't have account Please register if you don't have an account."

#     return render(request, 'accounts/login.html', {'error': error})

# @login_required(login_url='/login/')
# def my_courses(request):
#     enrollments = Enrollment.objects.filter(user=request.user)
#     return render(request, 'accounts/my_courses.html', {'enrollments': enrollments})

# def logout_view(request):
#     logout(request)
#     return redirect('/')