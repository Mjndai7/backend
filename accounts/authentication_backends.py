from django.contrib.auth.backends import BaseBackend
from .models import Users, Consultant, Client

class CustomUserModelBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        for user_model in [Users, Consultant, Client]:
            user = user_model.objects.filter(email=email).first()
            if user and user.check_password(password):
                return user
        return None
