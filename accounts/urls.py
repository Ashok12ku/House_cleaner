from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('provider-dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
]
