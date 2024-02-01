# urls.py
from django.urls import path
from .views import ConversationViewSet, MessageViewSet

# Create instances of the ViewSet classes for each action
conversation_list = ConversationViewSet.as_view({'get': 'list'})
conversation_detail = ConversationViewSet.as_view({'get': 'retrieve'})

message_list = MessageViewSet.as_view({'get': 'list'})
message_detail = MessageViewSet.as_view({'get': 'retrieve'})

urlpatterns = [
    path('conversations/', conversation_list, name='conversation-list'),
    path('conversations/<uuid:uuid>/', conversation_detail, name='conversation-detail'),
    path('messages/', message_list, name='message-list'),
    path('messages/<uuid:uuid>/', message_detail, name='message-detail'),
]
