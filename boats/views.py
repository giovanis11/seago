import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.views.decorators.http import require_POST

from .models import Boat, BoatCategory, WishList, BoatImage
from .forms import BoatForm


logger = logging.getLogger(__name__)


def safe_file_url(file_field):
    try:
        if file_field and getattr(file_field, "name", ""):
            return file_field.url
    except Exception:
        return None
    return None


def boat_form_context(form, action, boat=None):
    luxury_category = BoatCategory.objects.filter(name__iexact="Luxury").first()
    context = {
        "form": form,
        "action": action,
        "luxury_category_id": luxury_category.id if luxury_category else "",
    }
    if boat is not None:
        context["boat"] = boat
    return context


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
    luxury_subcategory = request.GET.get('luxury_subcategory')
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
    if luxury_subcategory:
        boats = boats.filter(luxury_subcategory=luxury_subcategory)
    if min_price:
        boats = boats.filter(price_per_day__gte=min_price)
    if max_price:
        boats = boats.filter(price_per_day__lte=max_price)
    if capacity:
        boats = boats.filter(capacity__gte=capacity)

    categories = BoatCategory.objects.all()
    luxury_category = categories.filter(name__iexact="Luxury").first()

    return render(request, 'boats/boat_list.html', {
        'boats': boats,
        'categories': categories,
        'boat_types': Boat.BOAT_TYPE_CHOICES,
        'luxury_subcategories': Boat.LUXURY_SUBCATEGORY_CHOICES,
        'luxury_category_id': luxury_category.id if luxury_category else "",
        'current_q': q or '',
        'current_type': boat_type or '',
        'current_category': category or '',
        'current_luxury_subcategory': luxury_subcategory or '',
        'current_min_price': min_price or '',
        'current_max_price': max_price or '',
        'current_capacity': capacity or '',
    })


def boat_detail(request, pk):
    boat = get_object_or_404(
        Boat.objects.select_related("owner", "category").prefetch_related(
            "images",
            "reviews__user",
        ),
        pk=pk,
        is_approved=True,
    )
    images = list(boat.images.all())
    reviews = list(boat.reviews.select_related("user").all())
    recommended = list(
        Boat.objects.select_related("owner")
        .prefetch_related("images")
        .filter(
        is_approved=True,
        is_available=True,
        category=boat.category
        )
        .exclude(pk=pk)[:4]
    )

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = WishList.objects.filter(user=request.user, boat=boat).exists()

    gallery_images = []
    for image in images:
        image_url = safe_file_url(image.image)
        if image_url:
            gallery_images.append(
                {
                    "url": image_url,
                    "is_cover": image.is_cover,
                }
            )

    cover_image_url = next(
        (image["url"] for image in gallery_images if image["is_cover"]),
        gallery_images[0]["url"] if gallery_images else None,
    )

    owner_avatar_url = safe_file_url(boat.owner.avatar)
    features_list = [item.strip() for item in boat.features.replace(",", " ").split() if item.strip()]

    review_cards = []
    for review in reviews:
        review_cards.append(
            {
                "user": review.user,
                "avatar_url": safe_file_url(review.user.avatar),
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at,
            }
        )

    recommended_cards = []
    for rec_boat in recommended:
        rec_images = []
        for image in rec_boat.images.all():
            image_url = safe_file_url(image.image)
            if image_url:
                rec_images.append({"url": image_url, "is_cover": image.is_cover})
        rec_cover_url = next(
            (image["url"] for image in rec_images if image["is_cover"]),
            rec_images[0]["url"] if rec_images else None,
        )
        recommended_cards.append(
            {
                "boat": rec_boat,
                "cover_url": rec_cover_url,
            }
        )

    return render(request, 'boats/boat_detail.html', {
        'boat': boat,
        'gallery_images': gallery_images,
        'gallery_count': len(gallery_images),
        'cover_image_url': cover_image_url,
        'owner_avatar_url': owner_avatar_url,
        'features_list': features_list,
        'reviews': review_cards,
        'recommended': recommended_cards,
        'in_wishlist': in_wishlist,
    })


@login_required
def boat_create(request):
    if not request.user.is_owner:
        return redirect('accounts:become_host')
    form = BoatForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        try:
            with transaction.atomic():
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
        except Exception as exc:
            logger.exception("Listing creation failed during boat/image save.")
            messages.error(
                request,
                f"We couldn't save this listing right now: {exc.__class__.__name__}: {str(exc)[:180]}",
            )
        else:
            messages.success(request, 'Listing added successfully!')
            return redirect('boats:my_listings')
    return render(request, 'boats/boat_form.html', boat_form_context(form, 'Add'))


@login_required
def boat_edit(request, pk):
    boat = get_object_or_404(Boat, pk=pk, owner=request.user)
    form = BoatForm(request.POST or None, request.FILES or None, instance=boat)
    if form.is_valid():
        try:
            with transaction.atomic():
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
        except Exception as exc:
            logger.exception("Listing update failed during boat/image save.")
            messages.error(
                request,
                f"We couldn't update this listing right now: {exc.__class__.__name__}: {str(exc)[:180]}",
            )
        else:
            messages.success(request, 'Listing updated.')
            return redirect('boats:my_listings')
    return render(
        request,
        'boats/boat_form.html',
        boat_form_context(form, 'Edit', boat=boat),
    )


@login_required
def boat_delete(request, pk):
    boat = get_object_or_404(Boat, pk=pk, owner=request.user)
    if request.method == 'POST':
        boat.delete()
        messages.success(request, 'Listing deleted.')
        return redirect('boats:my_listings')
    return render(request, 'boats/boat_confirm_delete.html', {'boat': boat})


@login_required
@require_POST
def wishlist(request, pk):
    boat = get_object_or_404(Boat, pk=pk, is_approved=True)
    wishlist_item, created = WishList.objects.get_or_create(user=request.user, boat=boat)

    if created:
        messages.success(request, "Boat saved to your wishlist.")
    else:
        wishlist_item.delete()
        messages.success(request, "Boat removed from your wishlist.")

    return redirect('boats:boat_detail', pk=pk)


@login_required
def my_listings(request):
    boats = Boat.objects.filter(owner=request.user)
    return render(request, 'boats/my_listings.html', {'boats': boats})
