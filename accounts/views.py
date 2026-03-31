from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def register_view(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    return render(request, 'accounts/login.html')