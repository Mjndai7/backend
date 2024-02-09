from rest_framework import serializers
from .models import User, Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'date_joined']
        extra_kwargs = {'password': {'write_only': True}, 'role': {'required': True}}
        read_only_fields = ['id', 'email', 'is_staff', 'is_active', 'date_joined', 'role']

class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)  # Include the avatar field

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['owner']
