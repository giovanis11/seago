from pyexpat import model

from django.db import models
from django.conf import settings

# Create your models here.

class BoatCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Boat(models.Model):
    BOAT_TYPE_CHOICES = [
        ('sailboat', 'Sailboat'),
        ('motorboat', 'Motorboat'),
        ('yacht', 'Yacht'),
        ('catamaran', 'Catamaran'),
    ]
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='boats')
    category = models.ForeignKey(BoatCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='boats')
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    capacity = models.PositiveIntegerField()
    boat_type = models.CharField(max_length=20, choices=BOAT_TYPE_CHOICES)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_approved = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class BoatImage(models.Model):
    boat = models.ForeignKey(Boat, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='boat_images/')
    is_cover = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.boat.name}"
    
class WishList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    boat = models.ForeignKey(Boat, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'boat')
    def __str__(self):
        return f"{self.user.username} - {self.boat.name}"