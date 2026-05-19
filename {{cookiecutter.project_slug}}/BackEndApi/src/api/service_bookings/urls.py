from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.service_bookings.views import ServiceViewSet, TestimonialViewSet, BookingViewSet

router = SimpleRouter()
router.register(r'services', ServiceViewSet, basename='services')
router.register(r'testimonials', TestimonialViewSet, basename='testimonials')
router.register(r'bookings', BookingViewSet, basename='bookings')

urlpatterns = [
    path('', include(router.urls)),
]
