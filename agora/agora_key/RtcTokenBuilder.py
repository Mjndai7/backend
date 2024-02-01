
from .AccessToken import *
import os
import sys
from collections import OrderedDict


Role_Attendee = 0  # depreated, same as publisher
Role_Publisher = 1  # for live broadcaster
Role_Subscriber = 2  # default, for live audience
Role_Admin = 101  # deprecated, same as publisher


class RtcTokenBuilder:

    @staticmethod
    def buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs):
        return RtcTokenBuilder.buildTokenWithAccount(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)

    @staticmethod
    def buildTokenWithAccount(appId, appCertificate, channelName, account, role, privilegeExpiredTs):
        token = AccessToken(appId, appCertificate, channelName, account)
        token.addPrivilege(kJoinChannel, privilegeExpiredTs)
        if (role == Role_Attendee) or (role == Role_Admin) or (role == Role_Publisher): 
            token.addPrivilege(kPublishVideoStream, privilegeExpiredTs)
            token.addPrivilege(kPublishAudioStream, privilegeExpiredTs)
            token.addPrivilege(kPublishDataStream, privilegeExpiredTs)
        return token.build()
