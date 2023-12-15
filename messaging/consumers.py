import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.db.models import Q
from .models import ChatRoom, PrivateChatRoom, PrivateMessage, Message
from accounts.models import Users

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = ChatRoom.objects.get(name=self.room_name)
        self.user = self.scope['user']
        self.user_inbox = f'inbox_{self.user.email}'

        # Accepts the WebSocket connection.
        await self.accept()

        # Joins the room group.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        # Display the user list to the newly joined user.
        await self.send(json.dumps({
            'type': 'user_list',
            'users': [user.email for user in self.room.online.all()],
        }))

        if self.user.is_authenticated:
            # Adds the user to the user_inbox group on connect.
            await self.channel_layer.group_add(
                self.user_inbox,
                self.channel_name,
            )

            # Sends the join event to the chatroom.
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'user': self.user.email,
                }
            )
            self.room.online.add(self.user)

    def saveMessage(self, message, userId, roomId):
        userObj = Users.objects.get(email=userId)
        chatObj = ChatRoom.objects.get(roomId=roomId)
        chatMessageObj = Message.objects.create(
            chat=chatObj, user=userObj, message=message
        )
        return {
            'action': 'message',
            'user': userId,
            'roomId': roomId,
            'message': message,
            'userName': userObj.username,
            'timestamp': str(chatMessageObj.timestamp),
        }

    async def sendOnlineUserList(self):
        onlineUserList = await database_sync_to_async(self.getOnlineUsers)()
        Message = {
            'type': 'chat_message',
            'message': {
                'action': 'onlineUser',
                'userList': onlineUserList
            }
        }
        await self.channel_layer.group_send('onlineUser', Message)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

        if self.user.is_authenticated:
            # Removes the user from the user_inbox group on disconnect.
            await self.channel_layer.group_add(
                self.user_inbox,
                self.channel_name,
            )

            # Send the leave event to the chatroom.
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user': self.user.email,
                }
            )
            self.room.online.remove(self.user)

        # When the socket disconnects.
        print('Disconnected')

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        roomId = text_data_json['roomId']
        message = {}

        if action == 'message':
            message = text_data_json['message']
            userId = text_data_json['user']
            Message = await database_sync_to_async(self.saveMessage)(message, userId, roomId)
        elif action == 'typing':
            message = text_data_json

        await self.channel_layer.group_send(
            roomId,
            {
                'type': 'chat_message',
                'message': message
            }
        )

        if not self.user.is_authenticated:
            return
        self.save_message(text_data_json['message'])

        # Sends the chat message event to the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'user': self.user.email,
                'type': 'chat_message',
                'message': message
            }
        )

        # Sends private message to the target inbox.
        await self.channel_layer.group_send(
            f'inbox_{message}',
            {
                'type': 'private_message',
                'user': self.user.email,
                'message': message,
            }
        )

        # Sends private message delivered to the user
        await self.send(json.dumps({
            'type': 'private_message_delivered',
            'user': self.user.email,
            'message': message
        }))

        Message.objects.create(user=self.user, room=self.room, content=message)

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def user_join(self, event):
        self.send(text_data=json.dumps(event))

    def user_leave(self, event):
        self.send(text_data=json.dumps(event))

    def private_message(self, event):
        self.send(text_data=json.dumps(event))

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))


class DirectChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Initialize attributes
        # Info must be unique
        self.room_name = self.scope['url']['kwargs']['pk']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = PrivateChatRoom.objects.get(pk=self.room_name)
        self.user = self.scope['user']

        if self.user == self.room.user1:
            self.other_user = Users.objects.get(pk=self.room.user2.pk)
        else:
            self.other_user = Users.objects.get(pk=self.room.user1.pk)

        await self.accept()

        print(f'[{self.channel_name}] - You are now connected.')

        # Display user list
        await self.send(json.dumps({
            'type': 'user_list',
            'users': [user.email for user in self.room.online.all()],
        }))

        if self.user.is_authenticated:
            # Sends the join event to the chatroom.
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'user': self.user.email,
                }
            )
            self.room.online.add(self.user)

    async def disconnect(self, close_code):
        self.room = PrivateChatRoom.objects.get(pk=self.room_name)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

        if self.user.is_authenticated:
            # Sends the leave event to the chatroom
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user': self.user.email,
                }
            )
            self.room.online.remove(self.user)

        # When the socket disconnects
        print('Disconnected')

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if not self.user.is_authenticated:
            return
        self.save_message(text_data_json['message'])

        # Sends the chat message Event to the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'user': self.user.email,
                'type': 'chat_message',
                'message': message
            }
        )

    def save_message(self, message):
        saved_message = PrivateMessage.objects.create(
            private_sender=self.user,
            private_receive=self.other_user,
            privateroom=self.room,
            content=message
        )

        saved_message.save()

    # Methods for message types for the channel layer
    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def user_join(self, event):
        self.send(text_data=json.dumps(event))

    def user_leave(self, event):
        self.send(text_data=json.dumps(event))
