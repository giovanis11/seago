from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Boat, BoatCategory, WishList, BoatImage
from .forms import BoatForm
from django.db.models import Q


def homepage(request):
    featured_boats = Boat.objects.filter(is_approved=True, is_available=True).order_by('-created_at')[:6]
    random_boats = Boat.objects.filter(is_approved=True, is_available=True).order_by('?')[:6]
    categories = BoatCategory.objects.all()
    return render(request, 'boats/home.html', {
        'featured_boats': featured_boats,
        'random_boats': random_boats,
        'categories': categories,
    })


def boat_list(request):
    boats = Boat.objects.filter(is_approved=True, is_available=True)

    q = request.GET.get('q')
    boat_type = request.GET.get('boat_type')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    capacity = request.GET.get('capacity')

    if q:
        boats = boats.filter(
            Q(name__icontains=q) | Q(location__icontains=q)
        )
    if boat_type:
        boats = boats.filter(boat_type=boat_type)
    if category:
        boats = boats.filter(category__id=category)
    if min_price:
        boats = boats.filter(price_per_day__gte=min_price)
    if max_price:
        boats = boats.filter(price_per_day__lte=max_price)
    if capacity:
        boats = boats.filter(capacity__gte=capacity)

    categories = BoatCategory.objects.all()

    return render(request, 'boats/boat_list.html', {
        'boats': boats,
        'categories': categories,
        'boat_types': Boat.BOAT_TYPE_CHOICES,
        'current_q': q or '',
        'current_type': boat_type or '',
        'current_category': category or '',
        'current_min_price': min_price or '',
        'current_max_price': max_price or '',
        'current_capacity': capacity or '',
    })


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


@login_required
def boat_create(request):
    if not request.user.is_owner:
        return redirect('accounts:become_host')
    form = BoatForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        boat = form.save(commit=False)
        boat.owner = request.user
        boat.is_approved = True
        boat.save()
        images = request.FILES.getlist('images')
        cover_index = int(request.POST.get('cover_index', 0))
        for i, img in enumerate(images):
            BoatImage.objects.create(
                boat=boat,
                image=img,
                is_cover=(i == cover_index)
            )
        messages.success(request, 'Listing added successfully!')
        return redirect('boats:my_listings')
    return render(request, 'boats/boat_form.html', {'form': form, 'action': 'Add'})


@login_required
def boat_edit(request, pk):
    boat = get_object_or_404(Boat, pk=pk, owner=request.user)
    form = BoatForm(request.POST or None, request.FILES or None, instance=boat)
    if form.is_valid():
        form.save()
        cover_id = request.POST.get('cover_image_id')
        if cover_id:
            boat.images.update(is_cover=False)
            BoatImage.objects.filter(id=cover_id, boat=boat).update(is_cover=True)
        images = request.FILES.getlist('images')
        cover_index = int(request.POST.get('cover_index', 0))
        for i, img in enumerate(images):
            BoatImage.objects.create(
                boat=boat,
                image=img,
                is_cover=(i == cover_index)
            )
        messages.success(request, 'Listing updated.')
        return redirect('boats:my_listings')
    return render(request, 'boats/boat_form.html', {'form': form, 'action': 'Edit', 'boat': boat})


@login_required
def boat_delete(request, pk):
    boat = get_object_or_404(Boat, pk=pk, owner=request.user)
    if request.method == 'POST':
        boat.delete()
        messages.success(request, 'Listing deleted.')
        return redirect('boats:my_listings')
    return render(request, 'boats/boat_confirm_delete.html', {'boat': boat})


@login_required
def wishlist(request, pk):
    return HttpResponse('Wishlist coming soon')


@login_required
def my_listings(request):
    boats = Boat.objects.filter(owner=request.user)
    return render(request, 'boats/my_listings.html', {'boats': boats})
