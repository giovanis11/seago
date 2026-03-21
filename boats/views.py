from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Boat, BoatCategory, WishList
from django.contrib.auth.decorators import login_required

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

def boat_detail(request, pk):
    boat = get_object_or_404(Boat, pk=pk, is_approved=True)
    images = boat.images.all()
    reviews = boat.reviews.all()
    recommended = Boat.objects.filter(
        is_approved=True,
        is_available=True,
        category=boat.category
    ).exclude(pk=pk)[:4]
    
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = WishList.objects.filter(user=request.user, boat=boat).exists()
    
    return render(request, 'boats/boat_detail.html', {
        'boat': boat,
        'images': images,
        'reviews': reviews,
        'recommended': recommended,
        'in_wishlist': in_wishlist,
    })

def boat_create(request):
    return HttpResponse('Boat create form coming soon')
def boat_edit(request, boat_id):
    return HttpResponse(f'Boat edit form for boats coming soon')
def boat_delete(request, boat_id):
    return HttpResponse(f'Boat delete confirmation for boats coming soon')
def wishlist(request):
    return HttpResponse('Wishlist coming soon')

@login_required
def my_listings(request):
    boats = Boat.objects.filter(owner=request.user)
    return render(request, 'boats/my_listings.html', {'boats': boats})