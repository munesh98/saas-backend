from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone 
from .models import Subscription
from datetime import timedelta

@shared_task
def send_subscription_confirmation_email(user_email, username, plan_name, end_date):
    send_mail(
        subject='Welcome to MJFlex!',
        message=f'Hi {username},\n\nWelcome to the MJFlex community!\n\nYour subscription plan "{plan_name}" is now active and valid until {end_date}.\n\nIf you wish to cancel anytime, visit: https://mjflex.com/cancel\n\nTerms & Conditions apply.\n\nTeam MJFlex',
        from_email='noreply@mjflex.com',
        recipient_list=[user_email],
    )

@shared_task
def auto_expire_subscriptions():
    today = timezone.now().date()
    subscriptions = Subscription.objects.filter(status='ACTIVE', end_date__lte=today)
    
    for subscription in subscriptions:
        if subscription.is_cancelled:
            subscription.status = 'CANCELLED'
            subscription.save()
        elif not subscription.auto_renew:
            subscription.status = 'EXPIRED'
            subscription.save()
        # if auto_renew=True, skip — auto renewal task handles it




@shared_task
def send_renewal_reminder_emails():
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    subscriptions = Subscription.objects.filter(
        end_date=tomorrow,
        auto_renew=True,
        is_cancelled=False,
        status='ACTIVE'
    )
    for subscription in subscriptions:
        send_mail(
            subject='Your MJFlex subscription renews tomorrow!',
            message=f'Hi {subscription.user.username},\n\nThis is a reminder that your "{subscription.plan.name}" plan renews tomorrow.\n\nRenewal amount: {subscription.plan.price}\n\nIf you wish to cancel, visit: https://mjflex.com/cancel\n\nTerms & Conditions apply.\n\nTeam MJFlex',
            from_email='noreply@mjflex.com',
            recipient_list=[subscription.user.email],
        )


@shared_task
def auto_renewal_subscriptions():
    today = timezone.now().date()
    subscriptions = Subscription.objects.filter(
        end_date=today,
        auto_renew=True,
        is_cancelled=False,
        status='ACTIVE'
    )
    for subscription in subscriptions:
        subscription.end_date = today + timedelta(days=subscription.plan.duration_days)
        subscription.save()
        send_mail(
            subject='Your MJFlex subscription is renewed',
            message=f'Hi {subscription.user.username},\n\nThis is a renewal of "{subscription.plan.name}" plan is successfull now, active and valid until {subscription.end_date}\n\nRenewal amount: {subscription.plan.price} is paid.\n\nIf you wish to cancel, visit: https://mjflex.com/cancel\n\nTerms & Conditions apply.\n\nTeam MJFlex',
            from_email='noreply@mjflex.com',
            recipient_list=[subscription.user.email],
        )