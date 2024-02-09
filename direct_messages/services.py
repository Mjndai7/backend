from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

from .models import Message, ChatRoom
from .signals import message_read, message_sent

from user.models import User

class MessagingService(object):
    """
    A object to manage all messages and conversations.
    """

    # Message creation

    def send_message(self, sender, recipient, message):
        """
        Send a new Message:
        :param sender: user
        :param recipient: user
        :param message: String
        :return: Messages and status code.
        """
        if sender == recipient:
            raise ValidationError("You can't send messages to yourself!")
        message = Message(sender=sender, recipient=recipient, content=str(message))
        message.save()

        message_sent.send(sender=message, form_user=message.sender, to=message.recipient)

        # The second value acts as a status value

        return message, 200
    
    # Message reading

    def get_unread_messages(self, user):
        """
        List of unread messages for a specific user.
        :param user: user
        :return: messages
        """
        return Message.objects.all().filter(recipient=user, read_at=None)
     
    def read_message(self, message_id):
        """
        Read specific message
        :param message_id: Integer
        :return: Message Text
        """
        try:
            message = Message.objects.get(id=message_id)
            self.mark_as_read(message)
            return message.content
        except Message.DoesNotExist:
            return ""
        
    # helper Methods
    def mark_as_read(self, message):
        """
        Marks a message as read, if i t hasn't been read before
        :param message: Message
        """
        if message.read_at is None:
            message.read_at = timezone.now()
            message_read.send(sender=message, from_user=message.sender, to=message.recipient)
            message.save()
    
    def read_message_formatted(self, message_id):
        """
        Read a message in the format <User>: <Message>
        :param message_id: ID
        :return: Formatted message Text
        """
        try:
            message = Message.objects.get(id=message_id)
            self.mark_as_read(message)
            return message.sender.username + ": " + message.content
        except Message.DoesNotExist:
            return ""
        
    
    # Conversation management
    
    def get_active_conversations(self, sender, recipient):
        active_conversations = Message.objects.filter(
            (Q(sender=sender) & Q(recipient=recipient))
            | (Q(sender=recipient) & Q(recipient=sender))
        ).order_by('sent_at')

        # print('active conversions', active_conversations)
        return active_conversations
    
    def get_conversations(self, user):
        """
        Lists all conversation-partners for a specific  user
        :param user: User
        :return: Conversation list.
        """
        chatrooms = ChatRoom.objects.filter((Q(sender=user) | Q(recipient=user)))

        chatroom_mapper = []
        for chatroom in chatrooms:
            chatroom_dict = {}
            chatroom_dict['pk'] = chatroom.pk

            if user == chatroom.sender:
                recipient = chatroom.recipient
            else:
                recipient = chatroom.sender
            chatroom_dict['recipient'] = recipient
            chatroom_mapper.append(chatroom_dict)
        
        return chatroom_mapper
