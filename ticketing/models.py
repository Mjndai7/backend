from django.db import models

# Create your models here.
from django.contrib.auth.models import User

from django.urls import reverse
from django.utils.crypto import get_random_string

from django.core.exceptions import ValidationError
from django.forms import PasswordInput
from django.conf import settings

class Ticket(models.Model):
    CONSULTING_ROLES = (
        ('Client', 'Client'),
        ('Consultant', 'Consultant'),
        ('Admin', 'Admin'),
        ('Infrastructure Specialist', 'Infrastructure Specialist'),
        ('Database Administrator', 'Database Administrator'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )

    ticket_id = models.CharField(max_length=8, unique=True, blank=True)
    title = models.CharField(max_length=50)
    customer_first_name = models.CharField(max_length=200)
    customer_last_name = models.CharField(max_length=200)
    customer_phone_number = models.CharField(max_length=20)
    customer_email = models.EmailField(max_length=40)
    issue_description = models.TextField(max_length=1000)
    ticket_section = models.CharField(
        max_length=30, choices=CONSULTING_ROLES, null=True, blank=True
    )
    urgent_status = models.BooleanField(default=False)
    completed_status = models.BooleanField(default=False)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='assigned_tickets', 
        null=True, 
        blank=True
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='resolved_tickets', 
        null=True, 
        blank=True
    )
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    resolved_by = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def generate_client_id(self):
        return get_random_string(8, allowed_chars='0123456789abcdefzxyv')

    def get_absolute_url(self):
        return reverse("ticketing:ticket-detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = self.generate_client_id()
        super(Ticket, self).save(*args, **kwargs)

class Comment(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    text = models.CharField(max_length=500)
    created_date = models.DateTimeField(null=True, auto_now_add=True)

class EmailDetails(models.Model):
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=254)

    def __str__(self):
        return self.email
    

        
