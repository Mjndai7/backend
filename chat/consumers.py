import json
from uuid import UUID
# In consumers.py
from chat.models import Conversation, Message

from asgiref.sync import async_to_sync
from chat.serializers import MessageSerializer
from django.contrib.auth import get_user_model
from channels.generic.websocket import JsonWebsocketConsumer

User = get_user_model()

class UUIDEncode(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)
    

class ChatConsumer(JsonWebsocketConsumer):
    """
    This consumer is used to show user's online status,
    and send notifications.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.conversation_uuid = None
        self.conversation = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            self.close()
            return
        
        self.accept()
        self.conversation_uuid = (
            f"{self.scope['url_route']['kwargs']['conversation_uuid']}"
        )
        self.conversation, created = Conversation.objects.get_or_create(uid=self.conversation_uuid)
        self.conversation.online.add(self.user)

        async_to_sync(self.channel_layer.group_add)(
            self.conversation_uuid,
            self.channel_name,
        )
        self.send_json(
            {
                "type": "online_user_list",
                "users": [user.email for user in self.conversation.online.all()],
            }
        )

        async_to_sync(self.channel_layer.group_send)(
            self.conversation_uuid,
            {
                "type": "user_join",
                "user": self.user.email,
            },
        )
        self.conversation.online.add(self.user)
        last_message = self.conversation.last_message.all().order_by("-timestamp")[0:10]
        message_count = self.conversation.last_message.all().count()
        self.send_json(
            {
                "type": "last_50_messages",
                "messages": MessageSerializer(last_message, many=True, context={'request': self.scope['user']}).data,
                "has_more": message_count > 5,
            }
        )   

    def disconnect(self, code):
        if self.user and self.user.is_authenticated:
            # send the leave event to the room
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_uuid,
                {
                    "type": "user_leave",
                    "user": self.user.email,
                },

            )
            self.conversation.online.remove(self.user)
        return super().disconnect(code)
    
    def get_receiver(self):
    # Assuming one-on-one conversation, find the participant who isn't the current user
        user = self.conversation.user.exclude(email=self.user.email)
        if user.exists():
           return user.first()  # Return the other participant
        return None


    def receive_json(self, content, **kwargs):
        message_type = content["type"]

        if message_type == "read_messages":
            messages_to_me = self.conversation.last_message.filter(to_user=self.user)
            messages_to_me.update(read=True)

            # update the unread message count
            unread_count = Message.objects.filter(to_user=self.user, read=False).count()
            async_to_sync(self.channel_layer.group_send)(
                self.user.email + "__notifications",
                {
                    "type": "unread_count",
                    "unread_count": unread_count,
                },
            )
        if message_type == "typing":
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_uuid,
                {
                    "type": "typing",
                    "user": self.user.email,
                    "typing": content["typing"],
                },
            )
        if message_type == "chat_message":
            receiver = self.get_receiver()
            if not receiver:
                return
            
            last_message = Message.objects.create(
                from_user=self.user,
                to_user=self.get_receiver(),
                content=content["last_message"],
                conversation=self.conversation,
            )
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_uuid,
                {
                    "type": "chat_message_echo",
                    "name": self.user.email,
                    "message": MessageSerializer(last_message, context={'request': self.scope['user']}).data,
                },
            )

            notification_group_name = self.get_receiver().email + "__notifications"
            async_to_sync(self.channel_layer.group_send)(
                notification_group_name,
                {
                    "type": "new_message_notification",
                    "name": self.user.email,
                    "message": MessageSerializer(last_message, context={'request': self.scope}).data
                },
            )
        return super().receive_json(content, **kwargs)
    
    def chat_message_echo(self, event):
        self.send_json(event)

    def user_join(self, event):
        self.send_json(event)

    def user_leave(self, event):
        self.send_json(event)
    
    def typing(self, event):
        self.send_json(event)
    
    def new_message_notification(self, event):
        self.send_json(event)
    
    def unread_count(self, event):
        self.send_json(event)

             
    @classmethod
    def encode_json(cls, content):
        return json.dumps(content, cls=UUIDEncode)


class NotificationConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.notification_group_name = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return
        
        self.accept()

        # private notification group

        self.notification_group_name = f"{self.user.email}__notifications"
        async_to_sync(self.channel_layer.group_add)(
            self.notification_group_name,
            self.channel_name,
        )

        # send count of unread messages
        unread_count = Message.objects.filter(to_user=self.user, read=False).count()
        self.send_json(
            {
                "type": "unread_count",
                "unread_count": unread_count,
            }
        )

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.notification_group_name,
            self.channel_name,
        )
        return super().disconnect(code)
    
    def new_message_notification(self, event):
        self.send_json(event)

    def unread_count(self, event):
        self.send_json(event)
    
        
