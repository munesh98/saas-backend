from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_verification_email(email, username, token):
    verification_link = f'http://127.0.0.1:8000/api/accounts/verify-email/?token={token}'
    send_mail(
        subject='Verify your MJFlex account',
        message=f'Hi {username},\n\nPlease verify your email by clicking the link below:\n\n{verification_link}\n\nThis link expires in 24 hours.\n\nTeam MJFlex',
        from_email='noreply@mjflex.com',
        recipient_list=[email],
    )


@shared_task
def send_password_reset_email(email, username, token):
    reset_link = f'http://127.0.0.1:8000/api/password-update/?token={token}'
    send_mail(
        subject='Reset your MJFlex password',
        message=f'Hi {username},\n\nClick the link below to reset your password:\n\n{reset_link}\n\nThis link expires in 24 hours.\n\nIf you did not request this, ignore this email.\n\nTeam MJFlex',
        from_email='noreply@mjflex.com',
        recipient_list=[email],
    )