from django.dispatch import Signal

message_sent = Signal()
message_sent.providing_args = ['from_user', 'to']

message_read = Signal()
message_read.providing_args = ['from_user', 'to']
