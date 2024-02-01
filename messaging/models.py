from django.db import models
from users.models import UserAccount
import string
from django.conf import settings
import random
import uuid

def generate_random_string(length):
    random_string = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return random_string

class ChatRoom(models.Model):
    token = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(to=UserAccount, blank=True)
    type = models.CharField(max_length=10, default='DM')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=128)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

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
    name = models.CharField(max_length=128)
    users = models.ManyToManyField(to=UserAccount, blank=True)
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
        return "DirectChat between: {} and {}".format(self.user1.email, self.user2.email)

    

class Message(models.Model):
    user = models.ForeignKey(to=UserAccount, on_delete=models.CASCADE)
    room = models.ForeignKey(to=ChatRoom, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)


    def __str__(self):
        return f'Public Messages: {self.user.email}: {self.message} [{self.timestamp}]'
    

class PrivateMessage(models.Model):
    """Structure for Messages."""
    private_sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='private_sender')
    private_receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='private_receiver')
    privateroom = models.ForeignKey(to=PrivateChatRoom, on_delete=models.CASCADE)
    message = models.CharField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)


    def __str__(self):
        return f'Private Message From: {self.private_sender.email}: {self.message} [{self.timestamp}] to {self.private_receiver.email} | Post UID: {self.uid}'
