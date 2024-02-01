from rest_framework import serializers
from .models import Ticket, Comment, EmailDetails

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class EmailDetailsSerializer(serializers.ModelSerializer):
    class Meta:
         
         models = EmailDetails
         fields = '__all__'
