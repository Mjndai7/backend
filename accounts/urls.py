from django.urls import path
from . import views

urlpatterns = [
    path('register/user/', views.UserRegistrationView.as_view(), name='user_registration'),
    path('register/consultant/', views.ConsultantRegistrationView.as_view(), name='consultant_registration'),
    path('register/client/', views.ClientRegistrationView.as_view(), name='client_registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('user/profile/', views.UserProfile.as_view(), name='user_profile'),
    path('change-password/', views.UserChangePassword.as_view(), name='change_password'),
    path('send-password-reset-email/', views.SendPasswordResetEmail.as_view(), name='send_password_reset_email'),
    path('password-reset/<str:uid>/<str:token>/', views.UserPasswordReset.as_view(), name='password_reset'),
    path('consultant/contact-information/', views.ConsultantContactInformationView.as_view(), name='consultant_contact_information'),
    path('client/contact-information/', views.ClientContactInformationView.as_view(), name='client_contact_information'),
    path('client/profile/', views.ClientProfileView.as_view(), name='client_profile'),
    path('consultant/profile/', views.ConsultantProfileView.as_view(), name='consultant_profile'),
    path('kyc/', views.KYCView.as_view(), name='kyc'),
    path('billing-information/', views.BillingInformationView.as_view(), name='billing_information'),
    path('client/billing-information/', views.ClientBillingInformationView.as_view(), name='client_billing_information'),
]
