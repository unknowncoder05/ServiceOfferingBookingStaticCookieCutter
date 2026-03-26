"""SMS delivery via AWS SNS.

boto3 is imported lazily so the app starts even if the package is removed.
If AWS credentials or region are not configured the function raises immediately
with a clear message instead of an obscure boto3 error.
"""
import logging

from api.users.conf import users_settings

logger = logging.getLogger(__name__)


def send_sms_message(phone_number, message, language_code=None):
    region = users_settings.aws_region_name
    if not region:
        raise RuntimeError(
            "AWS_REGION_NAME is not configured. Cannot send SMS. "
            "Set it or switch to a different token provider."
        )

    try:
        import boto3  # noqa: PLC0415
    except ImportError:
        raise RuntimeError(
            "boto3 is not installed. Add it to requirements or switch to "
            "a different token provider."
        )

    try:
        sns = boto3.client('sns', region_name=region)
        sns.publish(PhoneNumber=phone_number, Message=message)
    except Exception:
        logger.exception("Failed to send SMS to %s", phone_number)
        raise
