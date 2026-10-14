from django.urls import path
from . import views

urlpatterns = [
   path('', views.bookings_home, name='bookings_home'),
    path('create/<int:service_id>/', views.create_booking, name='create_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('invoice/', views.download_invoice, name='download_invoice'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('search/', views.search_services, name='search_services'),
    path('admin/bookings/', views.manage_bookings, name='manage_bookings'),
    path('<int:booking_id>/review/', views.add_review, name='add_review'),
    path('<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('wishlist/toggle/<int:service_id>/', views.toggle_wishlist, name='toggle_wishlist'),
]
