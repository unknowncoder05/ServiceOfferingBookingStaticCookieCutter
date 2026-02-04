from rest_framework import serializers

from api.investments.models import Investment, Nft


class NftSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='investment.project.id')
    name = serializers.CharField(source='investment.project.name')

    class Meta:
        model = Nft
        fields = ("id", "name", "token", "metadata")
