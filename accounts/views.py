from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import logout, login, authenticate
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User
from .forms import ProfileForm



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

@login_required
def profile_view(request):
    if request.method == 'POST':
        if 'remove_avatar' in request.POST:
            request.user.avatar.delete()
            request.user.avatar = None
            request.user.save()
            messages.success(request, 'Profile photo removed.')
            return redirect('accounts:profile')
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def dashboard_view(request):
    user = request.user
    if user.is_superuser:
        from boats.models import Boat
        from bookings.models import Booking
        context = {
            'total_users': User.objects.count(),
            'total_boats': Boat.objects.count(),
            'pending_boats': Boat.objects.filter(is_approved=False).count(),
            'total_bookings': Booking.objects.count(),
        }
        return render(request, 'accounts/dashboard_admin.html', context)
    elif user.is_owner:
        from boats.models import Boat
        from bookings.models import Booking
        my_boats = Boat.objects.filter(owner=user)
        incoming_bookings = Booking.objects.filter(boat__owner=user).order_by('-created_at')
        context = {
            'my_boats': my_boats,
            'incoming_bookings': incoming_bookings,
            'add_listing_url': '/boats/create/',
        }
        return render(request, 'accounts/dashboard_owner.html', context)
    else:
        from bookings.models import Booking
        from boats.models import WishList
        my_bookings = Booking.objects.filter(renter=user).order_by('-created_at')
        wishlist = WishList.objects.filter(user=user)
        context = {
            'my_bookings': my_bookings,
            'wishlist': wishlist,
            'browse_boats_url': '/boats/',
        }
        return render(request, 'accounts/dashboard_renter.html', context)

def become_host_view(request):
    return render(request, 'accounts/become_host.html')

@login_required
def become_host_confirm_view(request):
    request.user.is_owner = True
    request.user.save()
    return redirect('boats:boat_create')
