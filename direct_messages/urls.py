from django.urls import path
from .views import MessageDetailView, MessageView

app_name = 'direct_messages'

urlpatterns = [
    # API endpoint for retrieving and creating messages
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='api_message_detail'),
    path('messages/', MessageView.as_view(), name='api_messages'),
]
