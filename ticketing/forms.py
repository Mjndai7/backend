from django import forms
from django.contrib.auth.models import User
from .models import Ticket

from django.contrib.auth import get_user_model

User = get_user_model()

class TicketForm(forms.ModelForm):
    title = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control'}
    ))
    customer_first_name = forms.CharField(
        max_length=200, widget=forms.TextInput(
            attrs={'class': 'form-control'}
    ))
    customer_last_name = forms.CharField(
        max_length=200, widget=forms.TextInput(
            attrs={'class': 'form-control'}
    ))
    customer_phone_number = forms.CharField(
        max_length=20, widget=forms.TextInput(
            attrs={'class': 'form-control'}
    ))
    issue_description = forms.CharField(
        max_length=100, widget=forms.Textarea(
            attrs={'class': 'form-control'}
    ))
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        required=False,
        empty_label='Select User', 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
   

    class Meta:
        model = Ticket
        exclude = ('user', 'ticket_id', 'created_date',
                   'resolved_by', 'resolved_date')



class TicketUpdateForm(forms.ModelForm):

    CONSULTING_ROLES = (
        ('Client', 'Client'),
        ('Consultant', 'Consultant'),
        ('Admin', 'Admin'),
        ('Infrastructure Specialist', 'Infrastructure Specialist'),
        ('Database Administrator', 'Database Administrator'),
    )

    title = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control'}
    ))
    customer_first_name = forms.CharField(
        max_length=200, widget=forms.TextInput(
            attrs={'class': 'form-control'}
     ))
    customer_last_name = forms.CharField(
        max_length=200, widget=forms.TextInput(
            attrs={'class': 'form-control'}
    ))
    customer_phone_number = forms.CharField(
        max_length=20, widget=forms.TextInput(
            attrs={'class': 'form-control'}
    ))
    issue_description = forms.CharField(
        max_length=100, widget=forms.Textarea(
            attrs={'class': 'form-control'}
    ))
    ticket_section = forms.ChoiceField(
        choices=CONSULTING_ROLES, widget=forms.Select(
            attrs={'class': 'form-control'}
    ))

    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        required=False,
        empty_label='Select User', 
        widget=forms.Select(attrs={'class': 'form-control'})
    )   
    class Meta:
        model = Ticket
        exclude = ('user', 'ticket_id', 'created_date',
                   'resolved_by', 'resolved_date')
