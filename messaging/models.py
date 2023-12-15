from django.db import models
from accounts.models import Users
import uuid
import string
from django.conf import settings
import random

def generate_random_string(length):
    random_string = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return random_string

class ChatRoom(models.Model):
    token = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(Users)
    type = models.CharField(max_length=10, default='DM')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(null=True, unique=True)
    email = models.EmailField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = generate_random_string(20)

        return super(ChatRoom, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.token + ' -> ' + str(self.name)
    
    def get_online_count(self):
        return self.users.count()
    
    def join(self, user):
        self.users.add(user)
        self.save()
    
    def leave(self, user):
        self.users.remove(user)
        self.save
    
    def __str__(self):
        return f'{self.name} ({self.get_online_count()})'

    
class PrivateChatRoom(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    users = models.ManyToManyField(Users)
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user2")
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    def get_online_count(self):
        return self.users.count()
    
    def join(self, user):
        self.users.add(user)
        self.save()
    
    def leave(self, user):
        self.users.remove(user)
        self.save()
        
    def __str__(self):
        return f'DirectChat between: {self.user1.email} and {self.user2.email}'
    

class Message(models.Model):
    user = models.ForeignKey(to=Users, on_delete=models.CASCADE)
    room = models.ForeignKey(to=ChatRoom, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Messages: {self.user.email}: {self.message} [{self.timestamp}]'
    

class PrivateMessage(models.Model):
    private_sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='private_sender')
    private_receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='private_receiver')
    privateroom = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE)
    message = models.CharField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Private Message From: {self.private_sender.email}: {self.message} [{self.timestamp}] to {self.private_receiver.email}'
