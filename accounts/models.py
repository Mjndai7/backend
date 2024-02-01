# models.py
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import uuid
class MyUserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None, password2=None, **kwargs):
        if not email:
            raise ValueError("Users must have a valid email address")
        
        if self.filter(email=email).exists():
            raise ValueError("A user with this email address already exists.")
        
        if password != password2:
            raise ValueError("Password confirmation doesn't match the password")

        # Remove 'category' from kwargs if it exists and store it separately
        category = kwargs.pop('category', None)

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            **kwargs
        )

        # Only set 'category' if it is part of kwargs and the user model has 'category' field
        if category is not None and hasattr(user, 'category'):
            user.category = category

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, username, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            username=username,

        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class CheckEmail(AbstractBaseUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email

class Users(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class Consultant(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )

    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=255, default="consultant")
    category = models.CharField(max_length=255, choices=[("individual", "Individual"), ("organisation", "Organisation")])
    verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at =  models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email


    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
    
    def update_consultant(self, first_name, last_name, email, password, username):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.set_password(password)  # Use set_password for secure password updates
        self.save()  


class Client(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )

    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=255, default="client")
    verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


    def update_client(self, username, email, first_name, last_name, password):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.set_password(password)
        self.save()
           
class ConsultantContactInformation(models.Model):
    user = models.OneToOneField(Consultant, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return self.address
    
    def update_consultant_contact_information(self, phone_number, address, city, country, postal_code):
        self.phone_number = phone_number
        self.address = address
        self.city = city
        self.country = country
        self.postal_code = postal_code
        self.save()

class ClientContactInformation(models.Model):
    user = models.OneToOneField(Client, on_delete=models.CASCADE) 
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return self.address

    def update_client_contact_information(self, phone_number, address, city, country, postal_code):
        self.phone_number = phone_number
        self.address = address
        self.city = city
        self.country = country
        self.postal_code = postal_code
        self.save()

class ConsultantBillingInformation(models.Model):
    user = models.OneToOneField(Consultant, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    expiry_month = models.IntegerField()
    expiry_year = models.IntegerField()
    cvv = models.IntegerField()

    def __str__(self):
        return f"{self.card_number} ({self.expiry_month}/{self.expiry_year})"

    def update_billing_info(self, card_number, expiry_month, expiry_year, cvv):
        self.card_number = card_number
        self.expiry_month = expiry_month
        self.expiry_year = expiry_year
        self.cvv = cvv
        self.save()
    
class ClientBillingInformation(models.Model):
    user = models.OneToOneField(Client, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    expiry_month = models.IntegerField()
    expiry_year = models.IntegerField()
    cvv = models.IntegerField()

    def __str__(self):
        return f"{self.card_number} ({self.expiry_month}/{self.expiry_year})"

    def update_billing_info(self, card_number, expiry_month, expiry_year, cvv):
        self.card_number = card_number
        self.expiry_month = expiry_month
        self.expiry_year = expiry_year
        self.cvv = cvv
        self.save()

class ConsultantProfile(models.Model):
    consultant = models.OneToOneField(Consultant, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    portfolio_website_link = models.URLField(blank=True)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
    def __str__(self):
        return self.consultant.email

    def update_profile(self, title, description, hourly_rate, portfolio_website_link):
        self.title = title
        self.description = description
        self.hourly_rate = hourly_rate
        self.portfolio_website_link = portfolio_website_link
        self.save()

class ClientProfile(models.Model):
    user = models.OneToOneField(Client, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=255, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True)                                                                                                                                                                                                                                                                                                                        
    project_description = models.TextField(blank=True)

    def __str__(self):
        return self.user.email

    def update_client_profile(self, company_name, industry, budget, project_description):
        self.company_name = company_name
        self.industry = industry
        self.budget = budget
        self.project_description = project_description
        self.save()

class KYC(models.Model):
    user = models.OneToOneField(Consultant, on_delete=models.CASCADE)
    kra_pin = models.CharField(max_length=20)
    id_pin_number = models.CharField(max_length=10)

    def __str__(self):
        return f"KYC for {self.user.email}"

    def update_kyc(self, kra_pin, id_pin_number):
        self.kra_pin = kra_pin
        self.id_pin_number = id_pin_number
        self.save()

