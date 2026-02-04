"""WebSocket authentication middleware."""
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from api.users.models import User


@database_sync_to_async
def get_user_from_token(token_string):
    """Get user from JWT token."""
    try:
        # Validate the token
        access_token = AccessToken(token_string)
        user_id = access_token['user_id']

        # Get the user
        user = User.objects.get(id=user_id)
        return user
    except (TokenError, InvalidToken, User.DoesNotExist):
        return None


class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware for WebSocket connections.

    Allows unauthenticated connections initially.
    Authentication is handled via message after connection is established.
    """

    async def __call__(self, scope, receive, send):
        # Start with anonymous user - authentication happens via message
        scope['user'] = AnonymousUser()
        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """Helper function to apply JWT authentication middleware."""
    return JWTAuthMiddleware(inner)
