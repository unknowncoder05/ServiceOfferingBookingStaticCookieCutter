# rest_api/asgi.py
import os

import django
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import api.ws.routing
from api.ws.middleware import JWTAuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": asgi_app,
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(
            api.ws.routing.websocket_urlpatterns
        )
    ),
})
