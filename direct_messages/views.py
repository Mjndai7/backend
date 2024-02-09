from django.shortcuts import render, redirect
from rest_framework.views import APIView

# Create your views here.
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.views.generic import CreateView, RedirectView
from .services import MessagingService
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from .models import Message, ChatRoom

from rest_framework import generics, status
from .forms import MessageForm
from .serializers import MessageSerializer, ChatRoomSerializer
from django.contrib import messages

class MessageFormSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=1000)

class MessageDetailView(generics.RetrieveAPIView):
    serializer_class = ChatRoomSerializer
    queryset = ChatRoom.objects.all()

    def get_object(self):
        chat_id = self.kwargs.get('pk')
        chatroom = ChatRoom.objects.get(pk=chat_id)
        return chatroom

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get(self, request, *args, **kwargs):
        chatroom = self.get_object()

        # Fetch message based on chatroom
        message = Message.objects.filter(
            sender=chatroom.sender,
            recipient=chatroom.recipient
        ).first()

        if not message:
            message = Message.objects.filter(
                sender=chatroom.sender,
                recipient=chatroom.recipient
            ).first()

        # Mark message as read (you can use MessagingService().mark_as_read(message) if needed)

        user = self.request.user

         # Retrieve the list of current conversations for the user
        current_conversations = MessagingService().get_conversations(user=request.user)

        # Determine the active recipient based on the user and message
        if user == message.sender:
            chatroom.recipient = message.recipient
        else:
            chatroom.recipient = message.sender

        # Fetch active conversation for message/chat tab
        running_conversations = MessagingService().get_active_conversations(user, chatroom.recipient)

        # Serialize data
        chatroom_serializer = ChatRoomSerializer(chatroom)
        message_serializer = MessageSerializer(message)

        response_data = {
            'active_conversation': message_serializer.data,
            'conversations': chatroom_serializer.data,
            'current_conversations': MessageSerializer(current_conversations, many=True).data,
            'running_conversations': MessageSerializer(running_conversations, many=True).data
        }

        return Response(response_data, status=status.HTTP_200_OK)


    def post(self, request, pk):
        chatroom = get_object_or_404(ChatRoom, pk=pk)

        # Check if the current user is the sender or recipient
        if self.request.user == chatroom.sender:
            recipient = chatroom.recipient
        else:
            recipient = chatroom.sender

        form = MessageForm(self.request.data)
        if form.is_valid():
            # Create a new message
            message = form.save(commit=False)
            message.sender = self.request.user
            message.recipient = recipient
            message.save()

            # Use messages.success to provide feedback to the user
            messages.success(request, 'The message is sent with success!')

            # You can customize the response message or structure here
            return Response({'detail': 'Message sent successfully'}, status=status.HTTP_201_CREATED)

        # Return validation errors if the form is invalid
        return Response({'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

class MessageView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Prepares JSON response with information about the user's messages.
        """
        user = self.request.user
        chatroom = ChatRoom.objects.filter(Q(sender=user) | Q(recipient=user)).first()

        if chatroom:
            redirect_url = reverse('direct_messages:user_message', kwargs={'pk': chatroom.pk})
            response_data = {'redirect_url': redirect_url, 'message': 'Success'}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {'redirect_url': None, 'message': 'You do not have any messages to show.'}
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
