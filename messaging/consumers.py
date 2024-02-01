import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.db.models import Q
from .models import ChatRoom, PrivateChatRoom, PrivateMessage, Message
from users.models import UserAccount
class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None
        self.user_inbox = None


    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = ChatRoom.objects.get(name=self.room_name)
        self.user = self.scope['user']
        self.user_inbox = f'inbox_{self.user.email}'

        # Accepts the websocket connection
        self.accept()

        # joins the room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name,
        )

        # Display the user list to the newly joined user
        self.send(json.dumps({
            'type': 'user_list',
            'users': [user.email for user in self.room.users.all()],
        }))

        if self.user.is_authenticated:
            # Adds the user to the user_inbox group.
            async_to_sync(self.channel_layer.group_add)(
                self.user_inbox,
                self.channel_name,
            )
        
        # Sends the join event to the chatroom
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'user': self.user.email,
                }
            )
            self.room.users.add(self.user)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name,
        )

        if self.user.is_authenticated:
            # Removes the user from the user_inbox group.
            async_to_sync(self.channel_layer.group_add)(
                self.user_inbox,
                self.channel_name,
            )

            # Sends the leave event to the chatroom
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user': self.user.email,
                }
            )
            self.room.users.remove(self.user)
        # When the socket disconnects
        print('user Disconnected')

    
    # Forward Message to the using group send to chat message
    
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if not self.user.is_authenticated:
            return
        if message.startswith('/pm'):
            split = message.split[' ', 2]
            target = split[1]
            target_msg = split[2]

            # Sends private message to target inbox
            async_to_sync(self.channel_layer.group_send)(
                f'inbox_{target}',
                {
                    'type': 'private_message',
                    'user': self.user.email,
                    'message': target_msg,
                }
            )

            # Sends private message delivered to the user
            self.send(json.dumps({
                'type': 'private_message_delivered',
                'target': target,
                'message': target_msg,
            }))
            return
        # sends the chat message event to the room
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'user': self.user.email,
                'type': 'chat_message',
                'message': message
            }
        )
        Message.objects.create(user=self.user, room=self.room, message=message)

        # Methods for the message types for the channel layer

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
        
    def user_join(self, event):
        self.send(text_data=json.dumps(event))
        
    def user_leave(self, event):
        self.send(text_data=json.dumps(event))
        
    def private_message(self, event):
        self.send(text_data=json.dumps(event))
        
    def private_message_delivered(self, event):
        self.send(text_data=json.dumps(event))     
# Consumer for Direct Chat

class DirectChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.other_email = None
        self.other_user = None

        self.room_name = None
        self.room_group_name = None
        self.room = None

    
    # Called on Connection
    def connect(self):
        # initialize attributes properly based on available info
        # room info must be unique for each pair of users
        self.room_name = self.scope['url_route']['kwargs']['pk']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = PrivateChatRoom.objects.get(pk=self.room_name)
        self.user = self.scope['user']

        # if the chat initiator, other user object is equal to the receiver
        if self.user == self.room.user1:
            self.other_user = UserAccount.objects.get(pk=self.room.user2.pk)
        # Else other user was the initiator.
        else:
            self.other_user = UserAccount.objects.get(pk=self.room.user1.pk)
        
        # Accepts the WebSocket connection
        self.accept()
        # joins the room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        print(f'[{self.channel_name}] - You are now Connected to private messaging.')

        # Display the user list to the newly joined user.
        self.send(json.dumps({
            'type': 'user_list',
            'user': [user.email for user in self.room.users.all()],

        }))

        if self.user.is_authenticated:
            # Sends the join event to the chatroom.
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'user': self.user.email,
                }
            )
            self.room.users.add(self.user)

    
    def disconnect(self, close_code):
        self.room = PrivateChatRoom.objects.get(pk=self.room_name)

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

        if self.user.is_authenticated:
            # Sends the leave event to the chat room.
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user': self.user.email,
                }
            )
            self.room.users.remove(self.user)

        # When the socket disconnects
        print('Disconnected')
    
    # json format data is parsed and message is extracted.
        
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if not self.user.is_authenticated:
            return
        self.save_message(text_data_json['message'])

        # Sends the chat message Event to the room.
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'user': self.user.email,
                'type': 'chat_message',
                'message': message,
            }
        )
    
    def save_message(self, message):
        saved_message = PrivateMessage.objects.create(private_sender=self.user, private_receiver=self.other_user, privateroom=self.room, message=message)

        saved_message.save()
        return saved_message
    
    # methods for message types for the channels

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
    
    def user_join(self, event):
        self.send(text_data=json.dumps(event))
    
    def user_leave(self, event):
        self.send(text_data=json.dumps(event))

