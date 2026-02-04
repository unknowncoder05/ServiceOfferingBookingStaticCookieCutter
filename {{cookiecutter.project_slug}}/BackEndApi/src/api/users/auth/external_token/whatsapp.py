import json

import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


def send_whatsapp_token(phone_number, message, language_code='en_US'):
    send_whatsapp_template(phone_number.replace('+', ''), message['token'], message['token_type_verbose_name'].lower(),
                           language_code)


def send_whatsapp_template(phone_number, token, template, language_code='en_US'):
    if not settings.WHATSAPP_MESSAGE_URI:
        raise Exception('"WHATSAPP_MESSAGE_URI" is not set')
    headers = {
        'Authorization': f'{settings.WHATSAPP_AUTHORIZATION_TYPE} {settings.WHATSAPP_AUTHORIZATION_TOKEN}',
        'Content-Type': 'application/json',
    }
    components = [{
                'type': 'body',
                'parameters': [
                    {
                        'type': 'text',
                        'text': token
                    },
                ]
            }]
    if template == "sign_in":
        template = "sign_in_spanish"
        components.append({
                'type': 'button',
                'sub_type': 'url',  # Make sure to set the sub_type to 'url'
                'index': 0,  # Index of the button that requires the URL parameter
                'parameters': [
                    {
                        'type': 'text',
                        'text': token
                    }
                ]
            })
    elif template == "validate_account":
        template = "validate_account_spanish"
    data = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': phone_number,
        'type': 'template',
        'template': {
            'name': template,
            'components': components,
            'language': {'code': language_code},
        }
    }
    res = requests.post(settings.WHATSAPP_MESSAGE_URI, data=json.dumps(data), headers=headers)
    if res.status_code != 200:
        raise serializers.ValidationError({"phone_number": _("Number not valid.")})
