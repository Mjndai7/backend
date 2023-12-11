# models.py
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import uuid
from .booked_consultations import BookedConsultation

class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, password2=None, **kwargs):
        if not email:
            raise ValueError("Users must have a valid email address")
        
        if self.filter(email=email).exists():
            raise ValueError("A user with this email address already exists.")
        
        if password != password2:
            raise ValueError("Password confirmation doesn't match the password")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email,
            password=password,
            username=username,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class Users(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=255, unique=True)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin

class Consultant(Users):
    expertise = models.CharField(max_length=255)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    bio = models.TextField(blank=True)
    availability = models.BooleanField(default=True)
    certifications = models.TextField(blank=True)
    languages_spoken = models.TextField(blank=True)

    def __str__(self):
        return self.email

class NormalUser(Users):
    additional_info = models.TextField()
    booked_consultations = models.ManyToManyField(Consultant, through=BookedConsultation)
    interests = models.TextField(blank=True)
    preferred_language = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.email
