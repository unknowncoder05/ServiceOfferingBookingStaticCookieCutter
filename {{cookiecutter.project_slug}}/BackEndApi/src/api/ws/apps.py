"""WebSocket app configuration."""
from django.apps import AppConfig


class WebSocketConfig(AppConfig):
    name = 'api.ws'
    verbose_name = 'WebSocket'
