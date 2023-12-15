from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async

from channels.layers import get_channel_layer

from .serializers import (
    ChatRoomSerializer,
    PrivateChatRoomSerializer,
    MessageSerializer,
    PrivateMessageSerializer,
)
from .models import ChatRoom, PrivateChatRoom, Message, PrivateMessage
from accounts.models import Users

class ChatRoomView(APIView):
    def get(self, request, user_email):
        chat_rooms = ChatRoom.objects.filter(users__email=user_email)
        serializer = ChatRoomSerializer(
            chat_rooms, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ChatRoomSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessagesView(ListAPIView):
    serializer_class = MessageSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return Message.objects.filter(room__uid=room_id).order_by('-timestamp')

class DirectChatInitiateView(APIView):
    async def post(self, request):
        user1 = request.user
        user2_email = request.data.get('user2_email', None)
        if not user2_email:
            return Response({"error": "user2_email is required."}, status=status.HTTP_400_BAD_REQUEST)

        user2 = await database_sync_to_async(Users.objects.get)(email=user2_email)

        # Check if a room already exists between user1 and user2
        room = await database_sync_to_async(PrivateChatRoom.objects.filter)(
            Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
        )

        if room.exists():
            room = room.first()
        else:
            room = await database_sync_to_async(PrivateChatRoom.objects.create)(user1=user1, user2=user2)

        # Join the chat room
        room.join(user1)
        room.join(user2)

        # Send notification to frontend that chat has been initiated
        channel_layer = get_channel_layer()
        await database_sync_to_async(channel_layer.group_send)(
            f"chat_{room.uid}",
            {
                "type": "chat.initiate",
                "message": {"action": "initiate", "roomId": str(room.uid)},
            },
        )

        serializer = PrivateChatRoomSerializer(room, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class PrivateMessagesView(ListAPIView):
    serializer_class = PrivateMessageSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return PrivateMessage.objects.filter(privateroom__uid=room_id).order_by('-timestamp')