from django.db import models
from django.conf import settings

from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)
import uuid
class UserAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, role, password=None):
        # Your existing code for validation

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=self.normalize_email(email),
            role=role  # Include the role
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, first_name, username, last_name, email, password=None):
        user = self.create_user(
            first_name,
            username,
            last_name,
            email,
            role='admin',  # Assuming 'admin' role for superuser
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
    
class CheckEmail(AbstractBaseUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email



class UserAccount(AbstractBaseUser, PermissionsMixin):
    class UserRole(models.TextChoices):
        CONSULTANT = 'consultant', 'Consultant'
        CLIENT = 'client', 'Client'
        ADMIN = 'admin', 'Admin'

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)



    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.CLIENT
    )
         
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'role']


    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser

    def is_consultant(self):
        return self.role == self.UserRole.CONSULTANT

    def is_client(self):
        return self.role == self.UserRole.CLIENT


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    # Common fields
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    # Consultant-specific fields
    title = models.CharField(max_length=255, blank=True)
    bio = models.TextField(max_length=500,blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    portfolio_website_link = models.URLField(blank=True)

    # Client-specific fields
    company_name = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=255, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    project_description = models.TextField(blank=True)


    def __str__(self):
        return f'Profile for {self.user.username}'
    def __str__(self):
        return self.email

    @property
    def is_consultant(self):
        return self.user.role == 'consultant'

    @property
    def is_client(self):
        return self.user.role == 'client'


class BillingInformation(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='billing_info'
    )
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card_holder_name = models.CharField(max_length=100, blank=True)
    card_last_four_digits = models.CharField(max_length=4, blank=True)
    expiry_month = models.IntegerField(blank=True, null=True)
    expiry_year = models.IntegerField(blank=True, null=True)
    billing_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)



    def __str__(self):
        return f'Billing Information for {self.user.username}'


class KYC(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='kyc'
    )
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kra_pin =  models.CharField(max_length=20)
    id_pin_number = models.CharField(max_length=20)

    

    def __str__(self):
        return f"KYC for {self.user.email}"
    