from django.db import models
from django.contrib.auth import get_user_model
import uuid
import datetime

User = get_user_model()

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendly_profile')
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    availability = models.TextField(help_text="User's general availability")
    timezone = models.CharField(max_length=100, default='UTC', help_text="User's timezone")

    def __str__(self):
        return self.user.email

class CalendarSlot(models.Model):
    class SlotStatus(models.TextChoices):
        AVAILABLE = 'Available', 'Available'
        BOOKED = 'Booked', 'Booked'
        CANCELLED = 'Cancelled', 'Cancelled'
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    belongs_to = models.ForeignKey(User, related_name='created_slots', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(help_text="Start time for the slot.")
    end_time = models.DateTimeField(help_text="End time for the slot")
    duration = models.DurationField(help_text="Duration of the slot")
    status = models.CharField(max_length=10, choices=SlotStatus.choices, default=SlotStatus.AVAILABLE)
    recurring = models.BooleanField(default=False, help_text="Is this a recurring event?")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Slot by {self.belongs_to.email} from {self.start_time} to {self.end_time}"

class SlotBooking(models.Model):
    slot = models.OneToOneField(CalendarSlot, related_name='booking_details', on_delete=models.CASCADE)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booked_by = models.ForeignKey(User, related_name='booked_slots', on_delete=models.CASCADE, null=True, help_text="User who booked the slot.")
    booked_at = models.DateTimeField(auto_now_add=True, help_text='Date and time of booking')
    description = models.TextField(max_length=1012, null=True, help_text="Additional info about the booking")
    cancellation_reason = models.TextField(null=True, blank=True, help_text="Reason for cancellation")

    class Meta:
        ordering = ['-booked_at']

    def __str__(self):
        return f"Slot booked by {self.booked_by.email} for {self.slot.start_time} to {self.slot.end_time}"
