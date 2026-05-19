from django.contrib import admin

from api.service_bookings.models import Service, Testimonial, Booking


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'price_label', 'is_active', 'position')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'author_role', 'is_active', 'position')
    list_filter = ('is_active',)
    search_fields = ('author_name', 'quote')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'service', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'service')
    search_fields = ('full_name', 'email', 'transaction_code')
