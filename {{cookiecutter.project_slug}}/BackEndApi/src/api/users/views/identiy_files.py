# Model Views for users

from rest_framework import mixins
# Permissions
from rest_framework import permissions
# Rest framework
from rest_framework.viewsets import GenericViewSet

# Models
from api.users.models import IdentityFiles
from api.users.permissions import IsAdminPermission, CanCrudPermission
# Serializers
# Utils
from api.users.serializers.identity_files import IdentityFileSerializer
from api.utils.pagination import StartEndPagination


class IdentityFilesViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                           mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    """
    User ViewSet based on role
    """
    serializer_class = IdentityFileSerializer
    pagination_class = StartEndPagination
    permission_classes = [IsAdminPermission | CanCrudPermission | permissions.DjangoModelPermissions]
    model = IdentityFiles

    def get_queryset(self):
        return IdentityFiles.objects.filter(user=self.request.user)
