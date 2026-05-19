from rest_framework import serializers

from api.service_bookings.models import Service, Testimonial, Booking


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'duration', 'price_label']


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'quote', 'author_name', 'author_role']


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'full_name', 'email', 'service', 'date', 'time', 'notes',
            'transaction_code', 'verification_file', 'status', 'created_at',
        ]
        read_only_fields = ['status', 'created_at']


class BookingAdminSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'full_name', 'email', 'service', 'service_name', 'date', 'time', 'notes',
            'transaction_code', 'verification_file', 'status', 'created_at', 'updated_at',
        ]
