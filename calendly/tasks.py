from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_confirmation_email(user_email, details):
    # Email sending logic
    send_mail(
        'Your Appointment Confirmation',
        f'Here are the details of your appointment: {details}',
        'from@example.com',
        [user_email],
        fail_silently=False,
    )

@shared_task
def send_reminder_email(user_email, details):
    # Email sending logic for reminders
    send_mail(
        'Appointment Reminder',
        f'Just a reminder about your upcoming appointment: {details}',
        'from@example.com',
        [user_email],
        fail_silently=False,
    )
