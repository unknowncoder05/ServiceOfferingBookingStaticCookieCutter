# User serializers

# Django
from django.conf import settings
# Rest Framework
from rest_framework import serializers

# Models
from api.users.models import User
from api.users.serializers.identity_files import IdentityFileSerializer
from api.users.service.levels_service import LevelsSearch
from api.users.service.user_wallet import UserWalletService


class UserSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(format=settings.MAIN_DATE_FORMAT, required=False)
    identity_files = IdentityFileSerializer(many=True, required=False, source='identityfiles_set', read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    phone_number = serializers.CharField(required=False)
    github_username = serializers.CharField(read_only=True)
    github_connected = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'public_name', 'email', 'username', 'first_name', 'middle_name', 'last_name', 'identity_number',
            'dob', 'phone_number', 'public', 'profile_image', 'terms_and_conditions', 'document_type', 'identity_files',
            'is_verified', 'github_username', 'github_connected',
        ]

    def get_github_connected(self, obj):
        return bool(obj.github_id)

    def update(self, instance, validated_data):
        # isOwner = self.context.get('request').user.id == instance.id
        return super(UserSerializer, self).update(instance, validated_data)


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'public_name', 'profile_image']
