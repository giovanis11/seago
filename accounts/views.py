from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import logout, login, authenticate
from .forms import RegisterForm, LoginForm
from django.contrib import messages



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password = password)
            if user is not None:
                login(request,user)
                return redirect('boats:homepage')
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect ('boats:homepage')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('boats:homepage')
def profile_view(request):
    return HttpResponse('Profile page coming soon')
def dashboard_view(request):
    return HttpResponse('Dashboard page coming soon')