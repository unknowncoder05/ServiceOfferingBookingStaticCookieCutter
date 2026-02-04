"""
Item URL configuration.

Registers the ItemViewSet with a router for RESTful URL patterns.
"""
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.items.views import ItemViewSet


router = SimpleRouter()
router.register(r'items', ItemViewSet, basename='items')

urlpatterns = [
    path('', include(router.urls)),
]
