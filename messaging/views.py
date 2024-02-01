from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import permissions

from .models import ChatRoom, PrivateChatRoom, Message, PrivateMessage
from users.models import UserAccount
from .serializers import (
    ChatRoomSerializer,
    PrivateChatRoomSerializer,
    MessageSerializer,
    PrivateMessageSerializer,
)

class ChatRoomView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        # Assuming you want to get chat rooms owned by the currently logged-in user
        # You can access the user using request.user
        email = request.user.email
        chat_rooms = ChatRoom.objects.filter(users__email=email)

        chat_rooms = ChatRoom.objects.filter(email=email)
        serializer = ChatRoomSerializer(chat_rooms, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class MessageView(APIView):
    permission_classes = (permissions.AllowAny,)


    def post(self, request, *args, **kwargs):
        user = request.user
        room_name = request.data.get('name')
        message_text = request.data.get('message')

        try:
            room = ChatRoom.objects.get(name=room_name)
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is in the room
        if user not in room.users.all():
            return Response({'error': 'User not in the room'}, status=status.HTTP_403_FORBIDDEN)

        # Create a new message
        message = Message(user=user, room=room, message=message_text)
        message.save()

        serializer = MessageSerializer(message)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        room_name = self.kwargs['room_name']

        try:
            room = ChatRoom.objects.get(name=room_name)
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is in the room
        if request.user not in room.users.all():
            return Response({'error': 'User not in the room'}, status=status.HTTP_403_FORBIDDEN)

        messages = Message.objects.filter(room=room).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DirectChatRoomView(APIView):
    permission_classes = [permissions.AllowAny,]


    def get(self, request, pk):
        current_user = request.user

        try:
            other_user = UserAccount.objects.get(pk=pk)
        except UserAccount.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Use get_or_create to simplify the code
        room, created = PrivateChatRoom.objects.get_or_create(user1=current_user, user2=other_user)

        # Join the current user to the room
        room.join(current_user)

        # Serialize the chat room
        serializer = PrivateChatRoomSerializer(room)

        # Get the chat messages
        chat_messages = PrivateMessage.objects.filter(privateroom=room)
        message_serializer = PrivateMessageSerializer(chat_messages, many=True)

        response_data = {
            "chat_room": serializer.data,
            "chat_messages": message_serializer.data,
            "user": PrivateChatRoomSerializer(current_user).data,  # Serialize the authenticated user
        }

        return Response(response_data, status=status.HTTP_200_OK)


class PrivateMessagesView(APIView):
    permission_classes = (permissions.AllowAny,)


    def post(self, request, *args, **kwargs):
        user = request.user
        room_uid = self.kwargs['room_uid']
        message_text = request.data.get('message')

        try:
            room = PrivateChatRoom.objects.get(uid=room_uid)
        except PrivateChatRoom.DoesNotExist:
            return Response({'error': 'Private chat room not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is in the private chat room
        if user not in room.users.all():
            return Response({'error': 'User not in the private chat room'}, status=status.HTTP_403_FORBIDDEN)

        # Create a new private message
        private_message = PrivateMessage(private_sender=user, privateroom=room, message=message_text)
        private_message.save()

        serializer = PrivateMessageSerializer(private_message)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        room_uid = self.kwargs['room_uid']

        try:
            room = PrivateChatRoom.objects.get(uid=room_uid)
        except PrivateChatRoom.DoesNotExist:
            return Response({'error': 'Private chat room not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is in the private chat room
        if request.user not in room.users.all():
            return Response({'error': 'User not in the private chat room'}, status=status.HTTP_403_FORBIDDEN)

        private_messages = PrivateMessage.objects.filter(privateroom=room).order_by('timestamp')
        serializer = PrivateMessageSerializer(private_messages, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)