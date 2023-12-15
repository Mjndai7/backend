from rest_framework import serializers
from .models import ChatRoom, PrivateChatRoom, Message, PrivateMessage
from accounts.models import Users

class ChatRoomSerializer(serializers.ModelSerializer):
    members = serializers.ListField(write_only=True)

    def create(self, validated_data):
        members_data = validated_data.pop('members')
        chat_room = ChatRoom.objects.create(**validated_data)
        chat_room.users.set(members_data)
        return chat_room

    class Meta:
        model = ChatRoom
        fields = '__all__'

class PrivateChatRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrivateChatRoom
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    userName = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Message
        fields = '__all__'

class PrivateMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrivateMessage
        fields = '__all__'
