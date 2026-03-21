from django.urls import path
from . import views

app_name = 'boats'
urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('boats/', views.boat_list, name='boat_list'),
    path('boats/create/', views.boat_create, name='boat_create'),
    path('boats/<int:pk>/', views.boat_detail, name='boat_detail'),
    path('boats/<int:pk>/edit/', views.boat_edit, name='boat_edit'),
    path('boats/<int:pk>/delete/', views.boat_delete, name='boat_delete'),
    path('boats/<int:pk>/wishlist/', views.wishlist, name='wishlist'),
    path('owner/listings/', views.my_listings, name='my_listings'),
]