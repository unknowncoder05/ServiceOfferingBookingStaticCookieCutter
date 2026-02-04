from rest_framework import serializers

from api.users.models import IdentityFiles, DocumentType
from api.utils.date import validate_image


class IdentityFileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def create(self, validated_data):
        validate_image(validated_data['file'])
        return super(IdentityFileSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validate_image(validated_data['file'])
        return super(IdentityFileSerializer, self).update(instance, validated_data)

    class Meta:
        model = IdentityFiles
        exclude = ('deleted',)


class DocumentsTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        exclude = ('deleted', 'created', "modified")
