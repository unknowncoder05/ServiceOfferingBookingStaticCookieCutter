from rest_framework import serializers

from api.users.models import BankInformation, Bank, BankAccountType
from api.utils.date import validate_image


class BankInformationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    bank = serializers.PrimaryKeyRelatedField(required=True, queryset=Bank.objects.filter(deleted=False))
    account_type = serializers.PrimaryKeyRelatedField(required=True,
                                                      queryset=BankAccountType.objects.filter(deleted=False))

    def create(self, validated_data):
        validate_image(validated_data.get('file'))
        return super(BankInformationSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validate_image(validated_data.get('file'))
        return super(BankInformationSerializer, self).update(instance, validated_data)

    class Meta:
        model = BankInformation
        exclude = ('deleted',)


class BankAccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccountType
        exclude = ('deleted', 'created', "modified")


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        exclude = ('deleted', 'created', "modified")
