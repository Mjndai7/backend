# views.py
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from chat.serializers import MessageSerializer, ConversationSerializer
from chat.models import Conversation, Message
from chat.paginaters import MessagePagination

class ConversationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          GenericViewSet):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

class MessageViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     GenericViewSet):
    serializer_class = MessageSerializer
    pagination_class = MessagePagination

    def get_queryset(self):
        conversation_uuid = self.request.GET.get('conversation_uuid')
        if conversation_uuid:
            return Message.objects.filter(conversation__uid=conversation_uuid).order_by('timestamp')
        return Message.objects.none()
