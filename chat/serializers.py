from rest_framework import serializers
from chat.models import Message, Conversation
from user.serializers import Profile  # Assuming Profile is your detailed user serializer
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    conversation = serializers.SerializerMethodField()  # Add this line if it's not present

    class Meta:
        model = Message
        fields = (
            "uid",
            "conversation",
            "from_user",
            "to_user",
            "content",
            "timestamp",
            "read",
        )

    def get_conversation(self, obj):
        # Returns the conversation UID as a string
        return str(obj.conversation.uid)

    def get_from_user(self, obj):
        # Using Profile serializer for detailed user information
        return Profile(obj.from_user.profile, context=self.context).data

    def get_to_user(self, obj):
        # Similarly, using Profile serializer for the receiver's user information
        return Profile(obj.to_user.profile, context=self.context).data

class ConversationSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    online_users = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ("uid", "user", "online_users", "last_message")

    def get_user(self, obj):
        # Serializing the user associated with the conversation using their profile
        return Profile(obj.user.profile, context=self.context).data

    def get_online_users(self, obj):
        # Serializes all users that are currently online in the conversation using their profiles
        profiles = [user.profile for user in obj.online.all()]
        return Profile(profiles, many=True, context=self.context).data

    def get_last_message(self, obj):
        # Dynamically fetches the last message of the conversation
        last_message = obj.last_message  # Utilizing the @property method in Conversation model
        if last_message:
            return MessageSerializer(last_message, context=self.context).data
        return None