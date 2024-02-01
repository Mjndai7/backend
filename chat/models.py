from django.db import models
import uuid
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Conversation(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='conversation'
    )
    online = models.ManyToManyField(User, related_name='online_conversations', blank=True)

    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    @property
    def last_message(self):
        return self.last_message.order_by('-timestamp').first()

    def __str__(self):
        last_message = self.last_message
        last_message_info = f" - Last message at {last_message.timestamp}" if last_message else " - No messages yet"
        return f"Conversation with {self.user.email}{last_message_info}"

class Message(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name="messages"
    )
    from_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="messages_from_me"
    )
    to_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="messages_to_me"
    )
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.from_user.email} to {self.to_user.email}: '{self.content}' at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
