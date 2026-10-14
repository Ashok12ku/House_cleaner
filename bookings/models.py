from django.db import models
from services.models import Service
from django.conf import settings

# Create your models here.
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, help_text="Special instructions or notes")
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
   
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.service.name}"
    
    def can_cancel(self):
        """Check if booking can be cancelled (24 hours before booking date)"""
        from datetime import datetime, timedelta
        if self.status in ['cancelled', 'completed']:
            return False
        booking_datetime = datetime.combine(self.date, self.time)
        hours_until = (booking_datetime - datetime.now()).total_seconds() / 3600
        return hours_until >= 24
    
    def can_reschedule(self):
        """Check if booking can be rescheduled"""
        return self.status in ['pending', 'confirmed'] and self.can_cancel()


class Wishlist(models.Model):
    """Store user favorite services for quick rebook"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'service')
    
    def __str__(self):
        return f"{self.user.username} - {self.service.name}"