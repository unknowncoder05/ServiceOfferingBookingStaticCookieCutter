# Model Views for users

from rest_framework import mixins
# Permissions
from rest_framework import permissions
# Rest framework
from rest_framework.viewsets import GenericViewSet

# Models
from api.users.models import BankInformation
from api.users.permissions import IsAdminPermission, CanCrudPermission
# Serializers
# Utils
from api.users.serializers.bank_information import BankInformationSerializer


class BankInformationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                             mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    """
    User ViewSet based on role
    """
    serializer_class = BankInformationSerializer
    pagination_class = None
    permission_classes = [IsAdminPermission | CanCrudPermission | permissions.DjangoModelPermissions]
    model = BankInformation

    def get_queryset(self):
        return BankInformation.objects.filter(user=self.request.user)
