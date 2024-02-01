# serializers.py
from rest_framework import serializers
from .models import UserProfile, CalendarSlot, SlotBooking
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'availability', 'timezone']
        extra_kwargs = {
            'user': {'read_only': True}
        }

class CalendarSlotSerializer(serializers.ModelSerializer):
    belongs_to = serializers.ReadOnlyField(source='belongs_to.email')

    class Meta:
        model = CalendarSlot
        fields = ['id', 'belongs_to', 'created_at', 'start_time', 'end_time', 'duration', 'status', 'recurring']

class SlotBookingSerializer(serializers.ModelSerializer):
    slot = CalendarSlotSerializer(read_only=True)
    booked_by = serializers.ReadOnlyField(source='booked_by.email')

    class Meta:
        model = SlotBooking
        fields = ['uid', 'slot', 'booked_by', 'booked_at', 'description', 'cancellation_reason']

class CreateSlotBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlotBooking
        fields = ['slot', 'description']

    def create(self, validated_data):
        # Add additional logic here if necessary, e.g., checking slot availability
        return SlotBooking.objects.create(**validated_data, booked_by=self.context['request'].user)

