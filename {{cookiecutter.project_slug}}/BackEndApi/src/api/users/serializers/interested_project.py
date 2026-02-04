from rest_framework import serializers

from api.users.models.interested import InterestedIn


class InterestedProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = InterestedIn
        fields = '__all__'
