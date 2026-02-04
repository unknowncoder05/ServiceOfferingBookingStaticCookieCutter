"""Main URLs module."""

# Django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

# Views
from api.utils.views import health_check, keep_alive

urlpatterns = [
    # Django Admin
    path(settings.ADMIN_URL, admin.site.urls),

    # Health check endpoint (no auth required)
    re_path(settings.API_URI + '/health/', health_check, name='health-check'),

    # Keep-alive endpoint (no auth required)
    re_path(settings.API_URI + '/keep-alive/', keep_alive, name='keep-alive'),

    # API routes
    re_path(settings.API_URI + '/', include('api.users.urls')),
    re_path(settings.API_URI + '/', include('api.items.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
