from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserChangePasswordSerializer,
    SendPasswordResetEmailSerializer,
    UserPasswordResetSerializer,
    ConsultantRegistrationSerializer,
    NormalUserRegistrationSerializer,
)
from django.contrib.auth import authenticate
from .renderers import UserRenderers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError



User = get_user_model()

def get_tokens_for_user(user):
    try:
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return tokens
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                user_data = UserProfileSerializer(user).data
                tokens = get_tokens_for_user(user)
                return Response({'user': user_data, 'tokens': tokens}, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({'error': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        raise exceptions.MethodNotAllowed('GET')
    
class ConsultantRegistrationView(generics.CreateAPIView):
    serializer_class = ConsultantRegistrationSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 201:
            user = response.data
            user_data = UserProfileSerializer(user).data
            tokens = get_tokens_for_user(user)  # Get tokens for the registered consultant
            return Response({'user': user_data, 'tokens': tokens}, status=status.HTTP_201_CREATED)
        return response

    
    def get(self, request, format=None):
        raise exceptions.MethodNotAllowed('GET')

class NormalUserRegistrationView(generics.CreateAPIView):
    serializer_class = NormalUserRegistrationSerializer
    queryset = User.objects.all()


    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 201:
            user = response.data
            user_data = UserProfileSerializer(user).data
            tokens = get_tokens_for_user(user)  # Get tokens for the registered normal user
            return Response({'user': user_data, 'tokens': tokens}, status=status.HTTP_201_CREATED)
        return response
    
    def get(self, request, format=None):
        raise exceptions.MethodNotAllowed('GET')
    

class UserLoginView(APIView):
    renderer_classes = [UserRenderers]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token':token,'msg':'Login successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
        
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
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Changed.'}, status=status.HTTP_200_OK)

class SendPasswordResetEmail(generics.CreateAPIView):

    renderer_classes = [UserRenderers]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Sending Password Reset Email.'}, status=status.HTTP_200_OK)
    
class UserPasswordReset(APIView):
    serializer_class = UserPasswordResetSerializer

    def post(self, request, uid, token, format=None):
        serializer = self.serializer_class(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Add this line if your serializer is responsible for saving the data
        return Response({'msg': 'Password Reset Done.'}, status=status.HTTP_200_OK)