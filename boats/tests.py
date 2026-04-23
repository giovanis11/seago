from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Boat, BoatCategory, WishList


@override_settings(
    ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"],
    SECURE_SSL_REDIRECT=False,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
)
class WishlistTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="wishlistuser",
            email="wishlist@example.com",
            password="StrongPass123!",
        )
        self.owner = get_user_model().objects.create_user(
            username="boatowner",
            email="owner@example.com",
            password="StrongPass123!",
            is_owner=True,
        )
        self.category = BoatCategory.objects.create(name="Luxury")
        self.boat = Boat.objects.create(
            owner=self.owner,
            category=self.category,
            name="Wishlist Boat",
            location="Athens",
            description="A boat to save.",
            capacity=6,
            boat_type="yacht",
            price_per_day="250.00",
            features="WiFi",
            is_approved=True,
            is_available=True,
            luxury_subcategory="private_charter",
        )

    def test_logged_in_user_can_add_boat_to_wishlist(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("boats:wishlist", args=[self.boat.pk]), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(WishList.objects.filter(user=self.user, boat=self.boat).exists())
        self.assertContains(response, "Boat saved to your wishlist.")

    def test_second_wishlist_post_removes_saved_boat(self):
        WishList.objects.create(user=self.user, boat=self.boat)
        self.client.force_login(self.user)

        response = self.client.post(reverse("boats:wishlist", args=[self.boat.pk]), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(WishList.objects.filter(user=self.user, boat=self.boat).exists())
        self.assertContains(response, "Boat removed from your wishlist.")
