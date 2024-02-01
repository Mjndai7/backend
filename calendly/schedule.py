from datetime import datetime, timedelta
from .tasks import send_confirmation_email, send_reminder_email

# After booking confirmation
send_confirmation_email.delay(user_email, appointment_details)

# For a reminder, 24 hours before the appointment
reminder_time = appointment_time - timedelta(hours=24)
send_reminder_email.apply_async((user_email, appointment_details), eta=reminder_time)
