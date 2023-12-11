from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Users, Consultant, NormalUser


class AccountAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url  = reverse('user-registration')
        self.consultant_register_url  = reverse('consultant-registration')
        self.normal_user_register_url = reverse('normal-user-registration')
        self.login_url = reverse('user-login')
        self.profile_url = reverse('user-profile')
        self.change_password_url = reverse('user-change-password')
        self.send_password_reset_email_url = reverse('send-password-reset-email')


    def test_user_registration(self):
        data = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'testpassword123',
            'password2': 'testpassword123',
        }

        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    
    def test_consultant_registration(self):
        user = Consultant.objects.create_user
        data = {
            'email': 'testconsultant@example.com',
            'username': 'testconsultant',
            'password': 'testpassword123',
            'password2': 'testpassword123',
            'expertise': 'Test Expertise',
            'hourly_rate': '50.00',
        }

        self.client.authenticate(user)
        response = self.client.post(self.consultant_register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    
    def test_normal_user_registration(self):
        user = NormalUser.objects.create_user
        data = {
            'email': 'testnormaluser@example.com',
            'username': 'testnormaluser',
            'password': 'testpassword123',
            'password2': 'testpassword123',
            'additional_info': 'Test Additional Info',
        }
        self.client.authenticate(user)
        response = self.client.post(self.normal_user_register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    
    def test_user_login(self):
        user = Users.objects.create_user
        data = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'testpassword123',
        }
        self.client.authenticate(user)
        response = self.client.get(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_profile(self):
        user = Users.objects.create_user
        data = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'testpassword123',
        }
        self.client.authenticate(user)
        response = self.client.get(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_change_password(self):
        user = Users.objects.create_user
        data = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'testpassword123',
        }   
        self.client.authenticate(user)
        data = {
            'password': 'password123',
            'password2': 'newtestpassword123',
        }
        response = self.client.get(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def test_send_password_reset_email(self):
        user = Users.objects.create_user
        data = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'testpassword123',
        }  
        self.client.authenticate(user)
        data = {
            'email': 'testuser@example.com',
        }
        response = self.client.get(self.send_password_reset_email_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    


        
        

    
   
    
    

   
    




