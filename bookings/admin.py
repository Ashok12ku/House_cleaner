from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'date', 'status')  # ✅ fixed
    list_filter = ('status', 'date')  # ✅ fixed
    search_fields = ('user__username', 'service__name', 'address')
    list_editable = ('status',)
    
