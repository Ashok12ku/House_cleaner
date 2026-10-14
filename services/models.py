# services/models.py
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Service(models.Model):
    SERVICE_TYPES = [
        ('home', 'Home Cleaning'),
        ('office', 'Office Cleaning'),
        ('carpet', 'Carpet Cleaning'),
        ('sofa', 'Sofa Cleaning'),
        ('deep', 'Deep Cleaning'),
    ]

    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.CharField(max_length=50, help_text="Example: 2 hours")
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = Review.objects.filter(service=self)
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 2)
        return 0
    
    def review_count(self):
        """Count total reviews"""
        return Review.objects.filter(service=self).count()


class ServiceProviderProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provider_profile')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    experience = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    profile_pic = models.ImageField(upload_to='provider_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    total_bookings = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} (Provider)"
    
    def update_rating(self):
        """Auto-update provider rating from reviews"""
        from bookings.models import Review
        reviews = Review.objects.filter(booking__service__serviceproviderprofile=self)
        if reviews.exists():
            self.rating = round(sum([r.rating for r in reviews]) / reviews.count(), 2)
            self.save()


class Review(models.Model):
    RATING_CHOICES = [
        (1, '⭐ Poor'),
        (2, '⭐⭐ Fair'),
        (3, '⭐⭐⭐ Good'),
        (4, '⭐⭐⭐⭐ Very Good'),
        (5, '⭐⭐⭐⭐⭐ Excellent'),
    ]
    
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='review')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.username} - {self.service.name} ({self.rating}⭐)"
