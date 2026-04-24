from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from boats.models import Boat, BoatCategory


@override_settings(
    ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"],
    SECURE_SSL_REDIRECT=False,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)
class RegisterViewTests(TestCase):
    def test_register_creates_user_and_logs_them_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newcaptain",
                "email": "captain@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            follow=True,
        )

        user = get_user_model().objects.get(username="newcaptain")

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("boats:homepage"))
        self.assertEqual(user.email, "captain@example.com")
        self.assertEqual(str(self.client.session.get("_auth_user_id")), str(user.pk))

    def test_register_rejects_duplicate_email(self):
        get_user_model().objects.create_user(
            username="existinguser",
            email="captain@example.com",
            password="StrongPass123!",
        )

        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "seconduser",
                "email": "CAPTAIN@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An account with this email already exists.")
        self.assertFalse(
            get_user_model().objects.filter(username="seconduser").exists()
        )


@override_settings(
    ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"],
    SECURE_SSL_REDIRECT=False,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)
class AdminPanelTests(TestCase):
    def setUp(self):
        self.superuser = get_user_model().objects.create_superuser(
            username="captainadmin",
            email="admin@example.com",
            password="StrongPass123!",
        )
        self.member = get_user_model().objects.create_user(
            username="member",
            email="member@example.com",
            password="StrongPass123!",
        )
        self.owner = get_user_model().objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
            is_owner=True,
        )
        self.category = BoatCategory.objects.create(name="Luxury")
        self.boat = Boat.objects.create(
            owner=self.owner,
            category=self.category,
            name="Admin Test Boat",
            location="Athens",
            description="Boat managed from the admin panel.",
            capacity=8,
            boat_type="yacht",
            price_per_day="500.00",
            features="WiFi",
            is_approved=False,
            is_available=True,
            luxury_subcategory="private_charter",
        )

    def test_superuser_can_open_custom_admin_dashboard(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse("accounts:admin_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin panel")
        self.assertContains(response, "Manage users, owners, listings, bookings, and categories")

    def test_regular_user_cannot_access_custom_admin_dashboard(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse("accounts:admin_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_superuser_can_approve_listing_from_custom_admin_panel(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("accounts:admin_listing_toggle_approval", args=[self.boat.pk]),
            follow=True,
        )

        self.boat.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.boat.is_approved)
        self.assertContains(response, "approved")

    def test_superuser_can_toggle_owner_role_from_custom_admin_panel(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("accounts:admin_user_toggle_owner", args=[self.member.pk]),
            follow=True,
        )

        self.member.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.member.is_owner)
        self.assertContains(response, "is now an owner")
