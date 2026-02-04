import os
import time

from django.conf import settings


def set_authentication_cookies_to_response(username, response, tokens):
    try:
        if os.environ.get("DJANGO_SETTINGS_MODULE") != 'config.settings.local':
            response.set_cookie('REFRESH_TOKEN', tokens['AuthenticationResult']['RefreshToken'], httponly=True,
                                domain=settings.SESSION_COOKIE_DOMAIN, )
            response.set_cookie('USERNAME', username, httponly=True,
                                domain=settings.SESSION_COOKIE_DOMAIN)
            response.set_cookie('TOKEN', tokens['AuthenticationResult']['IdToken'], httponly=True,
                                domain=settings.SESSION_COOKIE_DOMAIN)
            response.set_cookie('EXPIRY', time.time() + tokens['AuthenticationResult']['ExpiresIn'],
                                domain=settings.SESSION_COOKIE_DOMAIN)
            response.set_cookie('ACCESS_TOKEN', tokens['AuthenticationResult']['AccessToken'],
                                max_age=tokens['AuthenticationResult']['ExpiresIn'], httponly=True,
                                domain=settings.SESSION_COOKIE_DOMAIN)
        else:
            response.set_cookie('REFRESH_TOKEN', tokens['AuthenticationResult']['RefreshToken'], httponly=True)
            response.set_cookie('USERNAME', username, httponly=True)
            response.set_cookie('TOKEN', tokens['AuthenticationResult']['IdToken'], httponly=True)
            response.set_cookie('EXPIRY', time.time() + tokens['AuthenticationResult']['ExpiresIn'])
            response.set_cookie('ACCESS_TOKEN', tokens['AuthenticationResult']['AccessToken'],
                                max_age=tokens['AuthenticationResult']['ExpiresIn'], httponly=True)
        return
    except Exception as e:
        print("GOT ERROR:", e)
        print(username, response, tokens)
