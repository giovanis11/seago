from django.shortcuts import render
from django.http import HttpResponse


def login_view(request):
    return HttpResponse('Login page coming soon')
def register_view(request):
    return HttpResponse('Registration page coming soon')
def logout_view(request):
    return HttpResponse('Logout page coming soon')
def profile_view(request):
    return HttpResponse('Profile page coming soon')
def dashboard_view(request):
    return HttpResponse('Dashboard page coming soon')