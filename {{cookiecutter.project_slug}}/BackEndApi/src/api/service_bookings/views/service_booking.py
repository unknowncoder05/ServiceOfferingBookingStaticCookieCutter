from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response

from api.service_bookings.models import Service, Testimonial, Booking
from api.service_bookings.serializers import (
    ServiceSerializer,
    TestimonialSerializer,
    BookingCreateSerializer,
    BookingAdminSerializer,
)


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.filter(is_active=True)
    serializer_class = TestimonialSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('service').all()
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'partial_update', 'update']:
            return BookingAdminSerializer
        return BookingCreateSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        booking.status = Booking.Status.CONFIRMED
        booking.reviewed_by = request.user
        booking.save(update_fields=['status', 'reviewed_by', 'updated_at'])
        return Response(BookingAdminSerializer(booking).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reject(self, request, pk=None):
        booking = self.get_object()
        booking.status = Booking.Status.REJECTED
        booking.reviewed_by = request.user
        booking.save(update_fields=['status', 'reviewed_by', 'updated_at'])
        return Response(BookingAdminSerializer(booking).data)
