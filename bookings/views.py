from django.shortcuts import render
from django.http import HttpResponse


def booking_list(request):
    return HttpResponse('Booking list coming soon')
def booking_detail(request, pk):
    return HttpResponse(f'Booking detail for booking {pk} coming soon')
def booking_create(request, boat_id):
    return HttpResponse(f'Booking create form for boat {boat_id} coming soon')
def booking_cancel(request, pk):
    return HttpResponse(f'Booking cancel confirmation for booking {pk} coming soon')
def booking_confirm(request, pk):
    return HttpResponse(f'Booking confirm page for booking {pk} coming soon')
def booking_update(request, pk):
    return HttpResponse(f'Booking update form for booking {pk} coming soon')