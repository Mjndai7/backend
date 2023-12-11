from django.urls import path
from .views import (
    UserRegistrationView,
    ConsultantRegistrationView,
    NormalUserRegistrationView,
    UserLoginView,
    UserProfile,
    UserChangePassword,
    SendPasswordResetEmail,
    UserPasswordReset,
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('register/consultant/', ConsultantRegistrationView.as_view(), name='consultant-registration'),
    path('register/normal/', NormalUserRegistrationView.as_view(), name='normal-user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/', UserProfile.as_view(), name='user-profile'),
    path('change-password/', UserChangePassword.as_view(), name='user-change-password'),
    path('send-password-reset-email/', SendPasswordResetEmail.as_view(), name='send-password-reset-email'),
    path('reset-password/<str:uid>/<str:token>/', UserPasswordReset.as_view(), name='user-password-reset'),

]
