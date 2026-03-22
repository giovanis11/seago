from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    boat = models.ForeignKey('boats.Boat', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'boat')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review {self.id} - {self.boat.name} by {self.user.username}"