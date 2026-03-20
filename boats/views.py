from django.shortcuts import render
from django.http import HttpResponse
from .models import Boat, BoatCategory

def homepage(request):
    featured_boats = Boat.objects.filter(is_approved=True, is_available=True).order_by('-created_at')[:6]
    print("BOATS FOUND:", featured_boats.count())
    categories = BoatCategory.objects.all()
    return render(request, 'boats/home.html', {
        'featured_boats': featured_boats,
        'categories': categories,
    })
def boat_list(request):
    return HttpResponse('Boat list coming soon')
def boat_detail(request, boat_id):
    return HttpResponse(f'Boat detail for boats coming soon')
def boat_create(request):
    return HttpResponse('Boat create form coming soon')
def boat_edit(request, boat_id):
    return HttpResponse(f'Boat edit form for boats coming soon')
def boat_delete(request, boat_id):
    return HttpResponse(f'Boat delete confirmation for boats coming soon')
def wishlist(request):
    return HttpResponse('Wishlist coming soon')
