# urls.py

from django.urls import path
from .views import (
    ChatRoomView,
    MessageView,
    DirectChatRoomView,
    PrivateMessagesView,
)
from .consumers import ChatConsumer, DirectChatConsumer
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application


urlpatterns = [
    path('chat-room/', ChatRoomView.as_view(), name='chat-room'),
    path('messages/<int:room_name>/', MessageView.as_view(), name='messages'),
    path('direct-chat-room/<int:pk>/', DirectChatRoomView.as_view(), name='direct-chat-room'),
    path('private-messages/<int:room_uid>/', PrivateMessagesView.as_view(), name='private-messages'),
]


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                path("ws/chat-room/<str:room_name>/", ChatConsumer.as_asgi()),
                path("ws/direct-chat/<int:pk>/", DirectChatConsumer.as_asgi()),
            ]
        )
    ),
})

