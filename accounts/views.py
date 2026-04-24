from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from bookings.models import Booking
from boats.models import Boat, BoatCategory, WishList
from reviews.models import Review

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import User


def superuser_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have access to this area.")
        return view_func(request, *args, **kwargs)

    return wrapped_view


def admin_panel_context(active_tab, **extra):
    context = {"admin_active_tab": active_tab}
    context.update(extra)
    return context


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("boats:homepage")
            messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("boats:homepage")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("boats:homepage")


@login_required
def profile_view(request):
    if request.method == "POST":
        if "remove_avatar" in request.POST:
            request.user.avatar.delete()
            request.user.avatar = None
            request.user.save()
            messages.success(request, "Profile photo removed.")
            return redirect("accounts:profile")
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})


@login_required
def dashboard_view(request):
    user = request.user
    if user.is_superuser:
        return redirect("accounts:admin_dashboard")
    if user.is_owner:
        my_boats = Boat.objects.filter(owner=user)
        incoming_bookings = Booking.objects.filter(boat__owner=user).order_by("-created_at")
        context = {
            "my_boats": my_boats,
            "incoming_bookings": incoming_bookings,
            "add_listing_url": "/boats/create/",
        }
        return render(request, "accounts/dashboard_owner.html", context)

    my_bookings = Booking.objects.filter(renter=user).order_by("-created_at")
    wishlist = WishList.objects.filter(user=user)
    context = {
        "my_bookings": my_bookings,
        "wishlist": wishlist,
        "browse_boats_url": "/boats/",
    }
    return render(request, "accounts/dashboard_renter.html", context)


def become_host_view(request):
    return render(request, "accounts/become_host.html")


@login_required
def become_host_confirm_view(request):
    request.user.is_owner = True
    request.user.save()
    return redirect("boats:boat_create")


@superuser_required
def admin_dashboard_view(request):
    context = admin_panel_context(
        "overview",
        stats=[
            {"label": "Users", "value": User.objects.count(), "icon": "bi-people"},
            {
                "label": "Owners",
                "value": User.objects.filter(is_owner=True, is_superuser=False).count(),
                "icon": "bi-person-badge",
            },
            {"label": "Listings", "value": Boat.objects.count(), "icon": "bi-water"},
            {
                "label": "Pending listings",
                "value": Boat.objects.filter(is_approved=False).count(),
                "icon": "bi-hourglass-split",
            },
            {"label": "Bookings", "value": Booking.objects.count(), "icon": "bi-calendar2-check"},
            {"label": "Reviews", "value": Review.objects.count(), "icon": "bi-star"},
        ],
        recent_users=User.objects.order_by("-date_joined")[:6],
        recent_boats=Boat.objects.select_related("owner", "category").order_by("-created_at")[:6],
        recent_bookings=Booking.objects.select_related("boat", "boat__owner", "renter").order_by("-created_at")[:6],
        recent_reviews=Review.objects.select_related("user", "boat").order_by("-created_at")[:6],
    )
    return render(request, "accounts/dashboard_admin.html", context)


@superuser_required
def admin_users_view(request):
    q = request.GET.get("q", "").strip()
    role = request.GET.get("role", "").strip()

    users = User.objects.annotate(
        listing_count=Count("boats", distinct=True),
        booking_count=Count("bookings", distinct=True),
    ).order_by("-date_joined")

    if q:
        users = users.filter(
            Q(username__icontains=q)
            | Q(email__icontains=q)
            | Q(phone__icontains=q)
        )

    if role == "owners":
        users = users.filter(is_owner=True, is_superuser=False)
    elif role == "members":
        users = users.filter(is_owner=False, is_superuser=False)
    elif role == "admins":
        users = users.filter(is_superuser=True)
    elif role == "inactive":
        users = users.filter(is_active=False)

    return render(
        request,
        "accounts/admin_users.html",
        admin_panel_context(
            "users",
            users=users,
            current_q=q,
            current_role=role,
        ),
    )


@require_POST
@superuser_required
def admin_user_toggle_owner_view(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    if target_user.is_superuser:
        messages.warning(request, "Superuser roles are managed in the secured Django admin.")
        return redirect("accounts:admin_users")

    target_user.is_owner = not target_user.is_owner
    target_user.save(update_fields=["is_owner"])
    messages.success(
        request,
        f"{target_user.username} is now {'an owner' if target_user.is_owner else 'a regular user'}.",
    )
    return redirect("accounts:admin_users")


@require_POST
@superuser_required
def admin_user_toggle_active_view(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    if target_user == request.user:
        messages.warning(request, "You cannot deactivate your own superuser account here.")
        return redirect("accounts:admin_users")

    if target_user.is_superuser:
        messages.warning(request, "Superuser access is managed in the secured Django admin.")
        return redirect("accounts:admin_users")

    target_user.is_active = not target_user.is_active
    target_user.save(update_fields=["is_active"])
    messages.success(
        request,
        f"{target_user.username} has been {'activated' if target_user.is_active else 'deactivated'}.",
    )
    return redirect("accounts:admin_users")


@superuser_required
def admin_listings_view(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    boats = Boat.objects.select_related("owner", "category").order_by("-created_at")

    if q:
        boats = boats.filter(
            Q(name__icontains=q)
            | Q(location__icontains=q)
            | Q(owner__username__icontains=q)
            | Q(category__name__icontains=q)
        )

    if status == "pending":
        boats = boats.filter(is_approved=False)
    elif status == "live":
        boats = boats.filter(is_approved=True, is_available=True)
    elif status == "unavailable":
        boats = boats.filter(is_available=False)
    elif status == "luxury":
        boats = boats.filter(category__name__iexact="Luxury")

    return render(
        request,
        "accounts/admin_listings.html",
        admin_panel_context(
            "listings",
            boats=boats,
            current_q=q,
            current_status=status,
        ),
    )


@require_POST
@superuser_required
def admin_listing_toggle_approval_view(request, boat_id):
    boat = get_object_or_404(Boat, pk=boat_id)
    boat.is_approved = not boat.is_approved
    boat.save(update_fields=["is_approved"])
    messages.success(
        request,
        f"{boat.name} is now {'approved' if boat.is_approved else 'pending approval'}.",
    )
    return redirect("accounts:admin_listings")


@require_POST
@superuser_required
def admin_listing_toggle_availability_view(request, boat_id):
    boat = get_object_or_404(Boat, pk=boat_id)
    boat.is_available = not boat.is_available
    boat.save(update_fields=["is_available"])
    messages.success(
        request,
        f"{boat.name} is now marked {'available' if boat.is_available else 'unavailable'}.",
    )
    return redirect("accounts:admin_listings")


@require_POST
@superuser_required
def admin_listing_delete_view(request, boat_id):
    boat = get_object_or_404(Boat, pk=boat_id)
    boat_name = boat.name
    boat.delete()
    messages.success(request, f"{boat_name} was deleted.")
    return redirect("accounts:admin_listings")


@superuser_required
def admin_categories_view(request):
    categories = BoatCategory.objects.annotate(boat_total=Count("boats")).order_by("name")
    return render(
        request,
        "accounts/admin_categories.html",
        admin_panel_context("categories", categories=categories),
    )


@require_POST
@superuser_required
def admin_category_create_view(request):
    name = request.POST.get("name", "").strip()
    description = request.POST.get("description", "").strip()

    if not name:
        messages.error(request, "Category name is required.")
        return redirect("accounts:admin_categories")

    if BoatCategory.objects.filter(name__iexact=name).exists():
        messages.warning(request, "A category with that name already exists.")
        return redirect("accounts:admin_categories")

    BoatCategory.objects.create(name=name, description=description)
    messages.success(request, f"{name} category created.")
    return redirect("accounts:admin_categories")


@require_POST
@superuser_required
def admin_category_update_view(request, category_id):
    category = get_object_or_404(BoatCategory, pk=category_id)
    name = request.POST.get("name", "").strip()
    description = request.POST.get("description", "").strip()

    if not name:
        messages.error(request, "Category name is required.")
        return redirect("accounts:admin_categories")

    duplicate = BoatCategory.objects.filter(name__iexact=name).exclude(pk=category.pk)
    if duplicate.exists():
        messages.warning(request, "Another category already uses that name.")
        return redirect("accounts:admin_categories")

    category.name = name
    category.description = description
    category.save(update_fields=["name", "description"])
    messages.success(request, f"{category.name} category updated.")
    return redirect("accounts:admin_categories")


@require_POST
@superuser_required
def admin_category_delete_view(request, category_id):
    category = get_object_or_404(BoatCategory, pk=category_id)
    category_name = category.name
    category.delete()
    messages.success(request, f"{category_name} category deleted.")
    return redirect("accounts:admin_categories")


@superuser_required
def admin_bookings_view(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    bookings = Booking.objects.select_related("boat", "boat__owner", "renter").order_by("-created_at")

    if q:
        bookings = bookings.filter(
            Q(boat__name__icontains=q)
            | Q(renter__username__icontains=q)
            | Q(boat__owner__username__icontains=q)
        )

    if status:
        bookings = bookings.filter(status=status)

    return render(
        request,
        "accounts/admin_bookings.html",
        admin_panel_context(
            "bookings",
            bookings=bookings,
            status_choices=Booking.STATUS_CHOICES,
            current_q=q,
            current_status=status,
        ),
    )


@require_POST
@superuser_required
def admin_booking_update_view(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    new_status = request.POST.get("status", "").strip()
    valid_statuses = {choice[0] for choice in Booking.STATUS_CHOICES}

    if new_status not in valid_statuses:
        messages.error(request, "Invalid booking status.")
        return redirect("accounts:admin_bookings")

    booking.status = new_status
    booking.save(update_fields=["status"])
    messages.success(request, f"Booking #{booking.pk} marked as {booking.get_status_display().lower()}.")
    return redirect("accounts:admin_bookings")
