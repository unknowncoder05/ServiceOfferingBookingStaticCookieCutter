from pytz import timezone as pztimezone
from django.conf import settings
from rest_framework.exceptions import ValidationError


def proper_date(date):
    settings_time_zone = pztimezone(settings.TIME_ZONE)
    return date.astimezone(settings_time_zone).strftime('%d %B, %Y %I:%M %p')


def validate_image(image):
    if image:
        file_size = image.size
        if file_size > settings.MAX_IMAGE_SIZE * 1024:
            raise ValidationError(f'The size of file must be less than {settings.MAX_IMAGE_SIZE} kb')
