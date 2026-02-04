# Model Views for users

from rest_framework import mixins
# Permissions
from rest_framework import permissions
# Rest framework
from rest_framework.viewsets import GenericViewSet

# Models
from api.users.models import Bank, BankAccountType
from api.users.permissions import IsAdminPermission, CanCrudPermission
# Serializers
# Utils
from api.users.serializers.bank_information import BankSerializer, BankAccountTypeSerializer


class BankViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    User ViewSet based on role
    """
    serializer_class = BankSerializer
    permission_classes = [IsAdminPermission | CanCrudPermission | permissions.DjangoModelPermissions]
    queryset = Bank.objects.filter(deleted=False)
    pagination_class = None
    model = Bank


class BankAccountTypeViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    User ViewSet based on role
    """
    serializer_class = BankAccountTypeSerializer
    permission_classes = [IsAdminPermission | CanCrudPermission | permissions.DjangoModelPermissions]
    queryset = BankAccountType.objects.filter(deleted=False)
    pagination_class = None
    model = BankAccountType
