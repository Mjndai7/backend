from django.urls import path
from .views import PusherAuth, AgoraToken, CallUserView

urlpatterns = [
    path('pusher/auth/', PusherAuth.as_view(), name='pusher-auth'),
    path('agora/token/', AgoraToken.as_view(), name='agora-token'),
    path('call-user/', CallUserView.as_view(), name='call-user'),
]
