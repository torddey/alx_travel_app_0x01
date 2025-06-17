from django.contrib import admin
from .models import Listing, Booking

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'host', 'city', 'country', 'price_per_night', 'property_type', 'is_available', 'created_at']
    list_filter = ['property_type', 'is_available', 'city', 'country', 'created_at']
    search_fields = ['title', 'description', 'address', 'city', 'state', 'country']
    list_editable = ['is_available']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'host')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'country', 'zip_code')
        }),
        ('Property Details', {
            'fields': ('property_type', 'bedrooms', 'bathrooms', 'max_guests', 'price_per_night')
        }),
        ('Media & Amenities', {
            'fields': ('amenities', 'images')
        }),
        ('Status', {
            'fields': ('is_available',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'guest', 'check_in_date', 'check_out_date', 'number_of_guests', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'check_in_date', 'check_out_date', 'created_at']
    search_fields = ['listing__title', 'guest__username', 'guest__email']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('listing', 'guest', 'status')
        }),
        ('Dates & Guests', {
            'fields': ('check_in_date', 'check_out_date', 'number_of_guests')
        }),
        ('Financial', {
            'fields': ('total_price',)
        }),
        ('Additional Information', {
            'fields': ('special_requests',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
