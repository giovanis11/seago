from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users_view, name='admin_users'),
    path('admin-panel/users/<int:user_id>/toggle-owner/', views.admin_user_toggle_owner_view, name='admin_user_toggle_owner'),
    path('admin-panel/users/<int:user_id>/toggle-active/', views.admin_user_toggle_active_view, name='admin_user_toggle_active'),
    path('admin-panel/listings/', views.admin_listings_view, name='admin_listings'),
    path('admin-panel/listings/<int:boat_id>/toggle-approval/', views.admin_listing_toggle_approval_view, name='admin_listing_toggle_approval'),
    path('admin-panel/listings/<int:boat_id>/toggle-availability/', views.admin_listing_toggle_availability_view, name='admin_listing_toggle_availability'),
    path('admin-panel/listings/<int:boat_id>/delete/', views.admin_listing_delete_view, name='admin_listing_delete'),
    path('admin-panel/categories/', views.admin_categories_view, name='admin_categories'),
    path('admin-panel/categories/create/', views.admin_category_create_view, name='admin_category_create'),
    path('admin-panel/categories/<int:category_id>/update/', views.admin_category_update_view, name='admin_category_update'),
    path('admin-panel/categories/<int:category_id>/delete/', views.admin_category_delete_view, name='admin_category_delete'),
    path('admin-panel/bookings/', views.admin_bookings_view, name='admin_bookings'),
    path('admin-panel/bookings/<int:booking_id>/update/', views.admin_booking_update_view, name='admin_booking_update'),
    path('become-host', views.become_host_view, name='become_host'),
    path('become-host/confirm', views.become_host_confirm_view, name='become_host_confirm')
]
