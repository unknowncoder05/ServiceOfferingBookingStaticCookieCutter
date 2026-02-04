# chat/routing.py
from django.urls import re_path

from api.ws.consumers import *

websocket_urlpatterns = [
    re_path(r'api/v1/ws/$', WSConsumer.as_asgi()),
]
