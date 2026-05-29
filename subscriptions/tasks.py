from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_subscription_confirmation_email(user_email, username, plan_name, end_date):
    send_mail(
        subject='Welcome to MJFlex!',
        message=f'Hi {username},\n\nWelcome to the MJFlex community!\n\nYour subscription plan "{plan_name}" is now active and valid until {end_date}.\n\nIf you wish to cancel anytime, visit: https://mjflex.com/cancel\n\nTerms & Conditions apply.\n\nTeam MJFlex',
        from_email='noreply@mjflex.com',
        recipient_list=[user_email],
    )