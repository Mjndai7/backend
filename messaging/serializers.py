from rest_framework import serializers
from .models import ChatRoom, PrivateChatRoom, Message, PrivateMessage
from accounts.models import Users

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['uid', 'email', 'username']  # Add other fields as needed

class ChatRoomSerializer(serializers.ModelSerializer):
    users = UsersSerializer(many=True)

    class Meta:
        model = ChatRoom
        fields = ['token', 'users', 'type', 'created_at', 'updated_at', 'name', 'username', 'email', 'uid',]

class PrivateChatRoomSerializer(serializers.ModelSerializer):
    users = UsersSerializer(many=True)
    user1 = UsersSerializer()
    user2 = UsersSerializer()

    class Meta:
        model = PrivateChatRoom
        fields = ['name', 'users', 'user1', 'user2', 'uid']

class MessageSerializer(serializers.ModelSerializer):
    user = UsersSerializer()

    class Meta:
        model = Message
        fields = ['user', 'room', 'message', 'timestamp', 'uid']

class PrivateMessageSerializer(serializers.ModelSerializer):
    private_sender = UsersSerializer()
    private_receiver = UsersSerializer()

    class Meta:
        model = PrivateMessage
        fields = ['private_sender', 'private_receiver', 'privateroom', 'message', 'timestamp', 'uid']
