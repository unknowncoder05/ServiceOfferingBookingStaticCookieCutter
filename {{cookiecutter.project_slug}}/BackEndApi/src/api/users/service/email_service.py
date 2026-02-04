from django.conf import settings
from django.core.mail import EmailMessage


class EmailService:
    @staticmethod
    def send_email_sign_up(email: str, name: str):
        print("send_email_sign_up")
        from_email: str = settings.EMAIL_NO_REPLY
        msg = EmailMessage(from_email=from_email, to=[email])
        msg.template_id = "d-105b11d4bf98476aa41e6fed7361da55"
        msg.dynamic_template_data = {"first_name": name}
        msg.send(fail_silently=False)

    @staticmethod
    def send_email_valid_phone_number(email: str):
        print("send_email_valid_phone_number")
        from_email: str = settings.EMAIL_NO_REPLY
        msg = EmailMessage(from_email=from_email, to=[email])
        msg.template_id = "d-094e48eaf77f4ad4af4147d3eaf795b9"
        msg.dynamic_template_data = {"subject": 'Validated Phone Number'}
        msg.send(fail_silently=False)

    @staticmethod
    def send_email_close_project(email: []):
        print("send_email_close_project")
        from_email: str = settings.EMAIL_NO_REPLY
        msg = EmailMessage(from_email=from_email, to=[email])
        msg.template_id = "d-835a8e6128ec4f909eb12b55fb67845c"
        msg.send(fail_silently=False)

    @staticmethod
    def send_email_project_update(email: list, project_name: str):
        print("send_email_project_update", email)
        emails = [e for e in email if e]
        from_email: str = settings.EMAIL_NO_REPLY
        msg = EmailMessage(from_email=from_email, to=[emails])
        msg.template_id = "d-6ba862ddd42b451289380917d803febc"
        msg.send(fail_silently=False)
