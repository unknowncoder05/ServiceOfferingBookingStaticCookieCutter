import json

import requests
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from api.users.conf import users_settings


def send_whatsapp_token(phone_number, message, language_code='en_US'):
    send_whatsapp_template(phone_number.replace('+', ''), message['token'], message['token_type_verbose_name'].lower(),
                           language_code)


def send_whatsapp_template(phone_number, token, template, language_code='en_US'):
    if not users_settings.whatsapp_message_uri:
        raise Exception('"WHATSAPP_MESSAGE_URI" is not set')
    headers = {
        'Authorization': f'{users_settings.whatsapp_authorization_type} {users_settings.whatsapp_authorization_token}',
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
    res = requests.post(users_settings.whatsapp_message_uri, data=json.dumps(data), headers=headers)
    if res.status_code != 200:
        raise serializers.ValidationError({"phone_number": _("Number not valid.")})
