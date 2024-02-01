from django.conf import settings
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Profile

from rest_framework.authtoken.views import ObtainAuthToken

from .serializers import (
    UserRegisterSerializer, 
    LoginAuthTokenSerializer, 
    UserUpdateSerializer, 
    ProfileSerializer, 
    UserChangePasswordSerializer, 
    UserPasswordResetSerializer, 
    BillingInformationSerializer, 
    KYCSerializer,
    SendPasswordResetEmailSerializer
)

class UserCreateView(CreateAPIView):
    serializer_class = UserRegisterSerializer

class UserUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user

class CustomObtainAuthTokenView(ObtainAuthToken):
    serializer_class = LoginAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            token = response.data.get('token')

            response.set_cookie(
                settings.AUTH_COOKIE,
                token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve the user's UserAccount instance
        user_account = request.user.username

        # Retrieve the user's UserProfile instance
        try:
            user_profile = Profile.objects.get(user=user_account)
        except Profile.DoesNotExist:
            return Response({"error": "UserProfile does not exist."}, status=404)

        # Serialize the user's profile data
        serializer = ProfileSerializer(user_profile)

        # Prepare the response data including UserAccount and UserProfile data
        response_data = {
            "user_data": {
                "email": user_account.email,
                "first_name": user_account.first_name,
                "last_name": user_account.last_name,
                "username": user_account.username,
                "role": user_account.role
            },
            "profile_data": serializer.data
        }

        return Response(response_data)



class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UserChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendPasswordResetEmailView(APIView):
    serializer_class = SendPasswordResetEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPasswordResetView(APIView):
    serializer_class = UserPasswordResetSerializer

    def post(self, request, uidb64, token):
        serializer = self.serializer_class(data=request.data, context={'uid': uidb64, 'token': token})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BillingInformationView(RetrieveUpdateAPIView):
    serializer_class = BillingInformationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.billing_info

class KYCView(RetrieveUpdateAPIView):
    serializer_class = KYCSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.kyc

class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie(settings.AUTH_COOKIE)
        return response
