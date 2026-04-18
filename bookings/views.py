from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from datetime import date
from decimal import Decimal
from .models import Booking
from boats.models import Boat


@login_required
def booking_list(request):
    bookings = Booking.objects.filter(renter=request.user).order_by('-created_at')
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})

def booking_detail(request, pk):
    return HttpResponse(f'Booking detail for booking {pk} coming soon')

@login_required
def booking_create(request, boat_id):
    boat = get_object_or_404(Boat, pk=boat_id, is_approved=True, is_available=True)
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        guests = int(request.POST.get('guests', 1))

        try:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
        except ValueError:
            messages.error(request, 'Invalid dates.')
            return redirect('boats:boat_detail', pk=boat_id)

        if start >= end:
            messages.error(request, 'End date must be after start date.')
            return redirect('boats:boat_detail', pk=boat_id)

        if start < date.today():
            messages.error(request, 'Start date cannot be in the past.')
            return redirect('boats:boat_detail', pk=boat_id)

        if guests > boat.capacity:
            messages.error(request, f'This boat fits max {boat.capacity} guests.')
            return redirect('boats:boat_detail', pk=boat_id)

        conflict = Booking.objects.filter(
            boat=boat,
            status__in=['pending', 'confirmed'],
            start_date__lt=end,
            end_date__gt=start,
        ).exists()

        if conflict:
            messages.error(request, 'These dates are already booked.')
            return redirect('boats:boat_detail', pk=boat_id)

        days = (end - start).days
        total = Decimal(str(boat.price_per_day)) * days

        request.session['cart'] = {
            'boat_id': boat_id,
            'start_date': start_date,
            'end_date': end_date,
            'guests': guests,
            'days': days,
            'total_price': str(total),
        }
        return redirect('bookings:booking_cart')

    return redirect('boats:boat_detail', pk=boat_id)

@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, renter=request.user)
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled.')
    return redirect('bookings:booking_list')

@login_required
def booking_confirm(request):
    cart = request.session.get('cart')
    if not cart:
        return redirect('boats:boat_list')

    boat = get_object_or_404(Boat, pk=cart['boat_id'])

    if request.method == 'POST':
        Booking.objects.create(
            renter=request.user,
            boat=boat,
            start_date=cart['start_date'],
            end_date=cart['end_date'],
            guests=cart['guests'],
            total_price=cart['total_price'],
            status='pending',
        )
        del request.session['cart']
        messages.success(request, 'Booking request submitted from your cart. The owner will review it.')
        return redirect('bookings:booking_list')

    return render(request, 'bookings/booking_confirm.html', {
        'cart': cart,
        'boat': boat,
    })


@login_required
def booking_cart_remove(request):
    if request.method == 'POST':
        request.session.pop('cart', None)
        messages.success(request, 'Booking cart cleared.')
    return redirect('boats:boat_list')


@login_required
def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk, boat__owner=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['confirmed', 'cancelled']:
            booking.status = new_status
            booking.save()
            messages.success(request, f'Booking {new_status}.')
    return redirect('accounts:dashboard')
