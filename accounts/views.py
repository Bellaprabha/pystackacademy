from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

# ✅ Import Enrollment (new)
from courses.models import Enrollment
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

# ✅ Register
def register_view(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')

    return render(request, 'accounts/register.html', {'form': form})


# ✅ Login
# def login_view(request):
#     return render(request, 'accounts/login.html')
def login_view(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/courses/')
        else:
            error = "Invalid username or password.if you don't have account Please register if you don't have an account."

    return render(request, 'accounts/login.html', {'error': error})

@login_required(login_url='/login/')
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user)
    return render(request, 'accounts/my_courses.html', {'enrollments': enrollments})

def logout_view(request):
    logout(request)
    return redirect('/')