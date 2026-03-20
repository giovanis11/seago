from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path("create/<int:boat_id>/", views.review_create, name="review_create"),
    path("<int:pk>/delete/", views.review_delete, name="review_delete"),
]