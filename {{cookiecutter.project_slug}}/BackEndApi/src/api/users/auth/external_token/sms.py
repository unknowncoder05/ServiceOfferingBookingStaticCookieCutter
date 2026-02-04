import boto3
from django.conf import settings


def send_sms_message(phone_number, message, language_code=None):
    sns = boto3.client('sns', region_name=settings.AWS_REGION_NAME)
    sns.publish(PhoneNumber=phone_number, Message=message)
