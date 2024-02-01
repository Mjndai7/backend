from django.contrib.auth.backends import BaseBackend
from .models import Users, Consultant, Client

class CustomAuthenticationBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        for user_model in [Users, Consultant, Client]:
            try:
                user = user_model.objects.get(email=email)
                if user.check_password(password):
                    return user
            except user_model.DoesNotExist:
                continue
        return None
