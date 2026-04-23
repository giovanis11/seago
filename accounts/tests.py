from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"],
    SECURE_SSL_REDIRECT=False,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
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
