import os
import time
import json
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .agora_key.RtcTokenBuilder import RtcTokenBuilder, Role_Attendee
from pusher import Pusher

# Instantiate a Pusher Client
pusher_client = Pusher(
    app_id=os.environ.get('PUSHER_APP_ID'),
    key=os.environ.get('PUSHER_KEY'),
    secret=os.environ.get('PUSHER_SECRET'),
    ssl=True,
    cluster=os.environ.get('PUSHER_CLUSTER')
)

class PusherAuth(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        User = get_user_model()
        user = User.objects.get(id=request.user.id)
        payload = pusher_client.authenticate(
            channel=request.data['channel_name'],
            socket_id=request.data['socket_id'],
            custom_data={
                'user_id': user.id,
                'user_info': {
                    'id': user.id,
                    'name': user.get_full_name()  # Assuming you have a get_full_name method
                }
            })
        return Response(payload)


class AgoraToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        User = get_user_model()
        user = User.objects.get(id=request.user.id)
        appID = os.environ.get('AGORA_APP_ID')
        appCertificate = os.environ.get('AGORA_APP_CERTIFICATE')
        channelName = request.data['channelName']
        userAccount = user.get_email_field_name  # Or any other unique identifier from the user model

        expireTimeInSeconds = 3600
        currentTimestamp = int(time.time())
        privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

        token = RtcTokenBuilder.buildTokenWithAccount(
            appID, appCertificate, channelName, userAccount, Role_Attendee, privilegeExpiredTs)

        return Response({'token': token, 'appID': appID})

class CallUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        body = request.data
        user_to_call = body.get('user_to_call')
        channel_name = body.get('channel_name')
        caller = request.user.id

        # Triggering the event to Pusher
        pusher_client.trigger(
            'presence-online-channel',
            'make-agora-call',
            {
                'userToCall': user_to_call,
                'channelName': channel_name,
                'from': caller
            }
        )

        return Response({'message': 'call has been placed'})