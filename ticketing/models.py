from django.db import models

# Create your models here.
from accounts.models import Users

from django.urls import reverse
from django.utils.crypto import get_random_string

from django.core.exceptions import ValidationError
from django.auth.models import Group
from django.forms import ModelForm

class Ticket(models.Model):
    CONSULTING_ROLES = (
        ('Client Services', 'Client Services'),
        ('Consultant', 'Consultant'),
        ('Project Manager', 'Project Manager'),
        ('Infrastructure Specialist', 'Infrastructure Specialist'),
        ('Database Administrator', 'Database Administrator'),
    )

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    ticket_id = models.CharField(max_length=8, unique=True, blank=True)
    title = models.CharField(max_length=50)
    customer_full_name = models.CharField(max_length=200)
    customer_email = models.EmailField(max_length=40)
    issue_description = models.TextField(max_length=1000)
    ticket_section = models.CharField(
        max_length=30, choices=CONSULTING_ROLES, null=True,
    )
    urgent_status = models.BooleanField(default=False)
    completed_status = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='assigned_to', null=True)
    resolved_by = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='resloved_by', null=True
    )
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    resolved_by = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    def generate_client_id(self):
        return get_random_string(8, allowed_chars='0123456789abcdefzxyv')
    
    def get_absolute_url(self):
        return reverse("ticketapp:ticket-detail", kwargs={"pk": self.pk})
    
    def save(self, *args, **kwargs):
        self.ticket_id = self.generate_client_id()
        super(Ticket, self).save(*args, **kwargs)
        
