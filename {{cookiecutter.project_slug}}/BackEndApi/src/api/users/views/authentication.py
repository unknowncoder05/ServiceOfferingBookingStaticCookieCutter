"""
Authentication Views
"""
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
# Persmissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
# Rest Framework
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Serializers
from api.users.serializers import *
from api.users.service.email_service import EmailService


def django_user_jwt(user):
    refresh = RefreshToken.for_user(user)
    return dict(
        refresh=str(refresh),
        access=str(refresh.access_token),
    )


def post_cookie_set(view, request, refresh=False):
    # you need to instantiate the serializer with the request data
    request_data = request.data
    refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE']) or None
    if refresh and refresh_token:
        request_data['refresh'] = refresh_token
    serializer = view.get_serializer(data=request.data)
    # you must call .is_valid() before accessing validated_data
    serializer.is_valid(raise_exception=True)

    # get access and refresh tokens to do what you like with
    access_token = serializer.validated_data.get("access", None)
    refresh_token = serializer.validated_data.get("refresh", None)

    # build your response and set cookie
    if access_token is None:
        return Response({"Error": "Something went wrong"}, status=400)
    response_data = {"access": access_token}
    if not refresh:
        response_data["refresh"] = refresh_token
    response = Response(response_data, status=200)
    response.set_cookie(
        key=settings.SIMPLE_JWT['ACCESS_TOKEN_COOKIE'],
        value=access_token,
        expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        secure=settings.SIMPLE_JWT['ACCESS_TOKEN_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['ACCESS_TOKEN_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['ACCESS_TOKEN_COOKIE_SAMESITE']
    )
    if not refresh:
        response.set_cookie(
            key=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE'],
            value=refresh_token,
            expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            secure=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_SAMESITE']
        )
    return response


def post_cookie_unset(view, request):
    response = Response(status=204)
    response.delete_cookie(settings.SIMPLE_JWT['ACCESS_TOKEN_COOKIE'])
    response.delete_cookie(settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE'])
    return response


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        return post_cookie_set(self, request)


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        return post_cookie_set(self, request, refresh=True)


class AuthViewSet(GenericViewSet):
    """
    Class handling authentication endpoints
    """
    serializer_class = LoginSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny],
            name='sign-up', url_path='sign-up')
    def sign_up(self, request):
        """
        Register a new user with email and password
        """
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for the new user
        jwt_tokens = django_user_jwt(user)
        return Response({
            'user': SignUpSerializer(user).data,
            **jwt_tokens
        })

    @action(detail=False, methods=['post'], permission_classes=[AllowAny],
            name='login', url_path='login')
    def login(self, request):
        """
        Login with email and password
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate JWT tokens
        jwt_tokens = django_user_jwt(user)
        return Response(jwt_tokens)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny],
            name='sign_out', url_path='sign-out')
    def sign_out(self, request):
        return post_cookie_unset(self, request)
