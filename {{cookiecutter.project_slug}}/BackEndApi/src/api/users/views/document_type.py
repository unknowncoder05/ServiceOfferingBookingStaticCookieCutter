# Model Views for users

from rest_framework import mixins
# Permissions
from rest_framework import permissions
# Rest framework
from rest_framework.viewsets import GenericViewSet

# Models
from api.users.models import DocumentType
from api.users.permissions import IsAdminPermission, CanCrudPermission
# Serializers
# Utils
from api.users.serializers.identity_files import DocumentsTypeSerializer
from api.utils.pagination import StartEndPagination


class DocumentTypeViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    User ViewSet based on role
    """
    serializer_class = DocumentsTypeSerializer
    pagination_class = StartEndPagination
    permission_classes = [IsAdminPermission | CanCrudPermission | permissions.DjangoModelPermissions]
    queryset = DocumentType.objects.filter(is_active=True, deleted=False)
    model = DocumentType
