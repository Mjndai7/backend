from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserAccount, Profile, BillingInformation, KYC

@receiver(post_save, sender=UserAccount)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=UserAccount)
def create_user_billing_info(sender, instance, created, **kwargs):
    if created:
        BillingInformation.objects.create(user=instance)

@receiver(post_save, sender=UserAccount)
def create_user_kyc(sender, instance, created, **kwargs):
    if created:
        KYC.objects.create(user=instance)
