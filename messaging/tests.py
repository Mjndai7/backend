# tests.py

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import ChatRoom, PrivateChatRoom, Message, PrivateMessage
from accounts.models import Users

class ChatRoomModelTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')

    def test_create_chat_room(self):
        chat_room = ChatRoom.objects.create(name='Test Room', owner=self.user)
        self.assertEqual(ChatRoom.objects.count(), 1)
        self.assertEqual(chat_room.name, 'Test Room')
        self.assertEqual(chat_room.owner, self.user)


class PrivateChatRoomModelTestCase(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(username='user1', password='password1')
        self.user2 = get_user_model().objects.create_user(username='user2', password='password2')

    def test_create_private_chat_room(self):
        private_chat_room = PrivateChatRoom.objects.create(user1=self.user1, user2=self.user2)
        self.assertEqual(PrivateChatRoom.objects.count(), 1)
        self.assertEqual(private_chat_room.user1, self.user1)
        self.assertEqual(private_chat_room.user2, self.user2)


class MessageModelTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.chat_room = ChatRoom.objects.create(name='Test Room', owner=self.user)

    def test_create_message(self):
        message = Message.objects.create(author=self.user, content='Test message', room=self.chat_room)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.author, self.user)
        self.assertEqual(message.content, 'Test message')
        self.assertEqual(message.room, self.chat_room)


class PrivateMessageModelTestCase(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(username='user1', password='password1')
        self.user2 = get_user_model().objects.create_user(username='user2', password='password2')
        self.private_chat_room = PrivateChatRoom.objects.create(user1=self.user1, user2=self.user2)

    def test_create_private_message(self):
        private_message = PrivateMessage.objects.create(author=self.user1, content='Test private message', privateroom=self.private_chat_room)
        self.assertEqual(PrivateMessage.objects.count(), 1)
        self.assertEqual(private_message.author, self.user1)
        self.assertEqual(private_message.content, 'Test private message')
        self.assertEqual(private_message.privateroom, self.private_chat_room)

