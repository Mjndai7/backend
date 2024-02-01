from django.urls import path
from .views import (
    UserCreateView, 
    UserUpdateView, 
    CustomObtainAuthTokenView, 
    UserProfileView, 
    UserChangePasswordView, 
    SendPasswordResetEmailView, 
    UserPasswordResetView, 
    BillingInformationView, 
    KYCView,
    LogoutView
)

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('update/', UserUpdateView.as_view(), name='user-update'),
    path('login/', CustomObtainAuthTokenView.as_view(), name='user-login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', UserChangePasswordView.as_view(), name='change-password'),
    path('send-reset-email/', SendPasswordResetEmailView.as_view(), name='send-reset-email'),
    path('reset-password/<uidb64>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('billing-info/', BillingInformationView.as_view(), name='billing-info'),
    path('kyc/', KYCView.as_view(), name='user-kyc'),
    path('logout/', LogoutView.as_view(), name='user-logout'),
]
