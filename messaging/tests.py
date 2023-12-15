from django.test import TestCase

# Create your tests here.
from rest_framework import status
from rest_framework.test import APIClient
from .models import ChatRoom, PrivateChatRoom, Message, PrivateMessage
from accounts.models import Users
from django.urls import reverse

from rest_framework.authtoken.models import Token

class ChatRoomAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(username="testuser", password="testpassword")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    
    def test_chat_room_creation(self):
        url = reverse('chat-room-list', kwargs={'user_email': self.user1.email})
        data = {
            'members': [self.user.email],
            'type': 'DM',
            'name': 'Test Room'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ChatRoom.objects.count(), 1)

    def test_direct_chat_initiate(self):
        url = reverse('initiate-direct-chat')
        data = {
            'user2_email': 'user2@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PrivateChatRoom.objects.count(), 1)

    def test_get_chat_rooms(self):
        url = reverse('chat-room-list', kwargs={'user_email': self.user.email})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MessagesAPITestCase(TestCase):
    def setup(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.chat_room = ChatRoom.objects.create(name='Test Room')
        self.message = Message.objects.create(user=self.user, room=self.chat_room, message='Test Message')

    
    def test_get_messages(self):
        url = reverse('message-list', kwargs={'room_id': self.chat_room.uid})
        data = {
            'user': self.user.email,
            'room': self.chat_room.uid,
            'message': 'Test Message',
        }
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PrivateMessagesAPITestCase(TestCase):
    def setup(self):
        self.client = APIClient()
        self.user1 = Users.objects.create_user(username='user1', password='testpassword1')
        self.user2 = Users.objects.create_user(username='user2', password='testpassword2')
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.client1 = APIClient()
        self.client2 = APIClient()
        self.client1.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        self.client2.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)

        self.private_chat_room = PrivateChatRoom.objects.create(user1=self.user1, user2=self.user2)
        self.private_message = PrivateMessage.objects.create(
            private_sender=self.user1,
            private_receiver=self.user2,
            privateroom=self.private_chat_room,
            message='Private test Message'
        )

    def test_get_private_messages(self):
        private_chat_room = PrivateChatRoom.objects.create(name='Private Test Room')
        url = reverse('private-message-list', kwargs={'room_id': private_chat_room.uid})
        data = {
            'private_sender': self.user1.email,
            'private_receiver': self.user2.email,
            'privateroom': private_chat_room.uid,
            'message': 'Private test Message',
        }
        response = self.client1.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(private_chat_room.privatemessages.count(), 1)

