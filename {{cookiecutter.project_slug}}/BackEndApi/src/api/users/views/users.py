# Model Views for users
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, filters
# Permissions
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
# Rest framework
from rest_framework.viewsets import GenericViewSet

# Models
from api.users.models import User
from api.users.permissions import IsAdminPermission, CanCrudPermission, CanWithdrawalPermission
# Serializers
from api.users.serializers import UserSerializer, CheckEmailOrPhone
# Utils
from api.users.service.user_wallet import UserWalletService
from api.utils.pagination import StartEndPagination


class UsersViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    User ViewSet based on role
    """
    model = User
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = StartEndPagination
    permission_classes = [
        IsAdminPermission | CanCrudPermission | CanWithdrawalPermission | permissions.DjangoModelPermissions]

    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = self.permission_classes
        if self.action == 'check':
            permission_classes = [AllowAny, ]
        return [permission() for permission in permission_classes]

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        queryset = self.filter_queryset(self.get_queryset())
        param_in_url = self.kwargs[lookup_url_kwarg]
        if param_in_url == "me":
            param_in_url = self.request.user.pk
        filter_kwargs = {self.lookup_field: param_in_url}

        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=False, methods=['get'])
    def permissions(self, request):
        data = request.user.user_permissions.all()
        return Response(data)

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def check(self, requests):
        data = requests.data
        CheckEmailOrPhone(data=data).is_valid(raise_exception=True)
        return Response({"complete": True})
