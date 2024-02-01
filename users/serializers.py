from django.contrib.auth import authenticate, get_user_model
from .models import UserAccount, BillingInformation, KYC, Profile
from django.contrib.auth import get_user_model

from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .utils import Util  # Assuming this is your utility for sending emails

from django.utils.translation import gettext as _
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import serializers
User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8}
        }  

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

class LoginAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=255, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with the provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user

        return attrs
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['first_name', 'last_name', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': False}
        }

    def update(self, instance, validated_data):
        # Update the user instance
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)

        # Update the password if it's provided
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)

        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)  # Include role

    class Meta:
        model = Profile
        fields = ['__all__']


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Old password is not correct"))
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get('email')
        user = UserAccount.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.uid))
            token = PasswordResetTokenGenerator().make_token(user)
            link = f'http://localhost:3000/auth/password-change/{uid}/{token}'
            body = 'Click the Following Link to Reset Your Password ' + link
            data = {
                'subject': 'Reset Your Password',
                'body': body,
                'to_email': user.email
            }
            Util.send_email(data)
            return attrs
        raise serializers.ValidationError("You are not a Registered User")
 

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    def validate_password(self, value):
        # Custom validation logic for the password
        # Example: Check the length of the password
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

    def save(self, **kwargs):
        uid = self.context.get('uid')
        token = self.context.get('token')
        uid = smart_str(urlsafe_base64_decode(uid))
        user = UserAccount.objects.filter(uid=uid).first()

        if user and PasswordResetTokenGenerator().check_token(user, token):
            user.set_password(self.validated_data['password'])
            user.save()
        else:
            raise serializers.ValidationError("Token is not valid or expired")

class BillingInformationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = BillingInformation
        fields = [
            'user',
            'card_holder_name',
            'card_last_four_digits',
            'expiry_month',
            'expiry_year',
            'billing_address',
            'city',
            'postal_code',
            'country'
        ]

class KYCSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = KYC
        fields = ['user', 'kra_pin', 'id_pin_number']