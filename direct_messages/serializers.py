# serializers.py

from rest_framework import serializers
from .models import Message, ChatRoom
from user.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'sender', 'recipient', 'sent_at', 'read_at']

class ChatRoomSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    recipient = UserSerializer()
    class Meta:
        model = ChatRoom
        fields = ['id', 'sender', 'recipient', 'created_at']
