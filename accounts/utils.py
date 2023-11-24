from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .models import User



def send_email_verification_code(email, verification_code):
    subject = 'Verify Your Email Address'
    message = f'Your email verification code is: {verification_code}'
    from_email = 'noreply@example.com'
    recipient_list = [email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


