from django.urls import path

from .views import ChatRoomView, MessagesView, DirectChatInitiateView, PrivateMessagesView

urlpatterns = [
    path('chat-rooms/<str:user_email>/', ChatRoomView.as_view(), name='chat-room-list'),
    path('messages/<uuid:room_id>/', MessagesView.as_view(), name='message-list'),
    path('initiate-direct-chat/', DirectChatInitiateView.as_view(), name='initiate-direct-chat'),
    path('private-messages/<uuid:room_id>/', PrivateMessagesView.as_view(), name='private-message-list'),
]
