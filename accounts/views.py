from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import (
    UserRegistrationSerializer,
    ConsultantRegistrationSerializer,
    ClientRegistrationSerializer,
    ConsultantContactInformationSerializer,
    ClientContactInformationSerializer,
    BillingInformationSerializer,
    ClientBillingInformationSerializer,
    ConsultantProfileSerializer,
    ClientProfileSerializer,
    KYCSerializer,
    LoginSerializer,
    UserProfileSerializer,
    UserChangePasswordSerializer,
    SendPasswordResetEmailSerializer,
    UserPasswordResetSerializer,
)

from django.contrib.auth import authenticate
from .renderers import UserRenderers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

User = get_user_model()



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    renderer_classes = [UserRenderers]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'token':token,'msg':'Registration Success.'}, status=status.HTTP_201_CREATED)

class ConsultantRegistrationView(APIView):
    renderer_classes = [UserRenderers]

    def post(self, request, format=None):
        serializer = ConsultantRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'token':token,'msg':'Registration Success.'}, status=status.HTTP_201_CREATED)

class ClientRegistrationView(APIView):
    renderer_classes = [UserRenderers]

    def post(self, request, format=None):
        serializer = ClientRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'token':token,'msg':'Registration Success.'}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                token = get_tokens_for_user(user)
                return Response({"token": token, "msg": "Login successful"}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserProfile(APIView):
    renderer_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserChangePassword(APIView):
    renderer_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data = request.data, context={'user':request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Changed.'}, status=status.HTTP_200_OK)
    
class SendPasswordResetEmail(APIView):

    renderer_classes = [UserRenderers]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Sending Password Reset Email.'}, status=status.HTTP_200_OK)
    

class UserPasswordReset(APIView):
    renderer_classes = [UserRenderers]
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Reset Done.'}, status=status.HTTP_200_OK)



class ConsultantContactInformationView(APIView):
      renderer_classes = [UserRenderers]
      permission_classes = [IsAuthenticated]

      def get(self, request):
        contact_info = ConsultantContactInformationSerializer.objects.get(user=request.user)
        serializer = ConsultantContactInformationSerializer(contact_info)
        return Response(serializer.data)

      def put(self, request):
        contact_info = ConsultantContactInformationSerializer.objects.get(user=request.user)
        serializer = ConsultantContactInformationSerializer(contact_info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientContactInformationView(APIView):
    renderer_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        billing_info = ClientContactInformationSerializer.objects.get(user=request.user)  # Assuming a one-to-one relationship with User model
        serializer = ClientContactInformationSerializer(billing_info)
        return Response(serializer.data)

    def put(self, request):
        billing_info = ClientContactInformationSerializer.objects.get(user=request.user)
        serializer = ClientContactInformationSerializer(billing_info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class  ClientProfileView(APIView):
    renderer_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client_profile = ClientProfileSerializer.objects.get(user=request.user)
        serializer = ClientProfileSerializer(client_profile)
        return Response(serializer.data)

    def put(self, request):
        client_profile = ClientProfileSerializer.objects.get(user=request.user)
        serializer = ClientProfileSerializer(client_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class  ConsultantProfileView(APIView):
    renderer_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client_profile = ConsultantProfileSerializer.objects.get(user=request.user)
        serializer = ConsultantProfileSerializer(client_profile)
        return Response(serializer.data)

    def put(self, request):
        client_profile = ConsultantProfileSerializer.objects.get(user=request.user)
        serializer = ConsultantProfileSerializer(client_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class  KYCView(APIView):
    renderer_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]


    def get(self, request):
        client_profile = KYCSerializer.objects.get(user=request.user)
        serializer = KYCSerializer(client_profile)
        return Response(serializer.data)

    def put(self, request):
        client_profile = KYCSerializer.objects.get(user=request.user)
        serializer = KYCSerializer(client_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BillingInformationView(APIView):
      renderer_classes = [UserRenderers]
      permission_classes = [IsAuthenticated]



      def get(self, request):
        contact_info = BillingInformationSerializer.objects.get(user=request.user)
        serializer = BillingInformationSerializer(contact_info)
        return Response(serializer.data)

      def put(self, request):
        contact_info = BillingInformationSerializer.objects.get(user=request.user)
        serializer = BillingInformationSerializer(contact_info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientBillingInformationView(APIView):
    renderer_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]



    def get(self, request):
        billing_info = ClientBillingInformationSerializer.objects.get(user=request.user)  # Assuming a one-to-one relationship with User model
        serializer = ClientBillingInformationSerializer(billing_info)
        return Response(serializer.data)

    def put(self, request):
        billing_info = ClientBillingInformationSerializer.objects.get(user=request.user)
        serializer = ClientBillingInformationSerializer(billing_info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)