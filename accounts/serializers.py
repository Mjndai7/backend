# serializers.py
from django.conf import settings
from .models import Users, Consultant, NormalUser
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import serializers
from .utils import Util
from django.contrib.auth import get_user_model


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Users
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password doesn't match")
        return data
    
    def create(self, validated_data):
        return Users.objects.create_user(**validated_data)

class ConsultantRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Consultant
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password doesn't match")
        return data

    def create(self, validated_data):
        return Consultant.objects.create_user(**validated_data)

class NormalUserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = NormalUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password doesn't match")
        return data

    def create(self, validated_data):
        return NormalUser.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = Users
        fields = ['email', 'password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['uid', 'email', 'username']

class UserChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)

    class Meta:
        model = Users
        fields = ['password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password doesn't match")
        
        user.set_password(password)
        user.save()
        return attrs

class SendPasswordResetEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = Users
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if Users.objects.filter(email=email).exists():
            user = Users.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.uid))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:3000/auth/password-change/'+uid+'/'+token
            # Send email
            body = 'Click the Following Link to Reset Your Password '+ link
            data = {
                'subject': 'Reset Your Password',
                'body': body,
                'to_email': user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise ValidationError("You are not a Registered User")

class UserPasswordResetSerializer(serializers.ModelSerializer):
    try:
        password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
        password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
        class Meta:
            model = Users
            fields = ['password', 'password2']

        def validate(self, attrs):
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')

            if password != password2:
                raise serializers.ValidationError("Password doesn't match")
            uid = smart_str(urlsafe_base64_decode(uid))
            user = Users.objects.get(uid=uid)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationError("Token is not valid or expired")
            
            user.set_password(password)
            user.save()
            return attrs 
    
    except DjangoUnicodeDecodeError:
        PasswordResetTokenGenerator().check_token(user, token)
        raise ValidationError('Token is not valid or expired')   