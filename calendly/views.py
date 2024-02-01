from django.shortcuts import render

# Create your views here.
import datetime
import time
from django.shortcuts import get_object_or_404

from .functions import generate_google_calendar_link
from .constants import ResponseMessages

import datetime
import time
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .constants import ResponseMessages
from .functions import generate_google_calendar_link
from .models import CalendarSlot, SlotBooking


User = get_user_model()

from django.utils import timezone

class SlotDataView(APIView):
    """
    Creates a bookable slot for the logged in user.
    The slot is created if it does not conflict with any existing slot and if the end time
    of the slot is greater than the current time.
    """

    def post(self, request, *args, **kwargs):
        try:
            start_time = datetime.datetime.strptime(request.data['start_time'], "%Y-%m-%dT%H:%M:%SZ")
            start_time = timezone.make_aware(start_time)
        except (KeyError, ValueError):
            return Response(data=ResponseMessages.MISSING_KEY, status=HTTP_400_BAD_REQUEST)
        
        end_time = start_time + datetime.timedelta(hours=1)
        if end_time <= timezone.now():
            return Response(data=ResponseMessages.CREATE_FUTURE_SLOTS, status=HTTP_400_BAD_REQUEST)

        overlapping_slots = CalendarSlot.objects.filter(
            belongs_to=request.user,
            end_time__gt=start_time,
            start_time__lt=end_time
        )
        if overlapping_slots.exists():
            return Response(data=ResponseMessages.CONFLICTING_SLOT, status=HTTP_400_BAD_REQUEST)

        calendar_slot = CalendarSlot.objects.create(
            belongs_to=request.user, start_time=start_time, end_time=end_time
        )
        return Response(data={'uid': calendar_slot.uid}, status=HTTP_200_OK)
    
    def get(self, request, *args, **kwargs):
        """
        Returns all the slot details created  by the logged in user.
        """
        all_created_slots = CalendarSlot.objects.filter(belongs_to=request.user)
        response_data = []
        for slot_detail in all_created_slots:
            slot_data = {
                "uid": slot_detail.uid,
                "start_time": str(slot_detail.start_time),
                "end_time": str(slot_detail.end_time)
            }
            try:
                slot_detail.booking_details
            except: 
                slot_data['is_booked'] = False
            else:
                slot_data['is_booked'] = True
        return Response(data=response_data, status=HTTP_200_OK)
    
class SlotDetailsView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Gives detailed information of the specified slot, including details of the booking if it is booked.
        """
        try:
            slot_details = CalendarSlot.objects.select_related('booking_details__booked_by').get(uid=kwargs['uid'], belongs_to=request.user)
        except CalendarSlot.DoesNotExist:
            return Response(data=ResponseMessages.CALENDAR_SLOT_NOT_FOUND, status=HTTP_404_NOT_FOUND)

        response_data = {
            "uid": slot_details.uid,
            "start_time": slot_details.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": slot_details.end_time.strftime("%Y-%m-%d %H:%M:%S")
        }

        if hasattr(slot_details, 'booking_details'):
            booked_by = slot_details.booking_details.booked_by.user_email if slot_details.booking_details.booked_by else "Anonymous User"
            response_data.update({
                "is_booked": True,
                "booking_id": slot_details.booking_details.uid,
                "booked_by": booked_by,
                "booked_at": slot_details.booking_details.booked_at.strftime("%Y-%m-%d %H:%M:%S"),
                "description": slot_details.booking_details.description
            })
        else:
            response_data['is_booked'] = False

        return Response(data=response_data, status=HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """
        Deletes the requested calendar slot.
        """
        try:
            CalendarSlot.objects.get(uid=kwargs['uid'], belongs_to=request.user).delete()
        except CalendarSlot.DoesNotExist:
            return Response(data=ResponseMessages.CALENDAR_SLOT_NOT_FOUND, status=HTTP_404_NOT_FOUND)

        return Response(status=HTTP_200_OK)

class GetAvailableSlotsView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, uid=user_id)

        available_slots = CalendarSlot.objects.filter(
            start_time__gt=timezone.now(),
            booking_details__isnull=True,
            belongs_to=user
        ).order_by('start_time')

        response_data = [{
            "uid": slot.uid,
            "start_time": slot.start_time.isoformat(),
            "end_time": slot.end_time.isoformat()
        } for slot in available_slots]

        return Response(data=response_data, status=HTTP_200_OK)

class BookSlotView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        slot_id = kwargs.get('uid')
        slot = get_object_or_404(CalendarSlot, uid=slot_id)

        if slot.end_time < timezone.now():
            return Response(data=ResponseMessages.CALENDAR_SLOT_EXPIRED, status=HTTP_400_BAD_REQUEST)
        if SlotBooking.objects.filter(slot=slot).exists():
            return Response(data=ResponseMessages.CALENDAR_SLOT_ALREADY_BOOKED, status=HTTP_400_BAD_REQUEST)

        booking_description = request.data.get('description', '')
        slot_booking_details = SlotBooking.objects.create(slot=slot, booked_by=request.user, description=booking_description)

        response_data = {
            "uid": slot_booking_details.uid,
            "add_to_google_calendar": generate_google_calendar_link(slot_booking_details)
        }

        return Response(data=response_data, status=HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        slot_id = kwargs.get('uid')
        booking = get_object_or_404(SlotBooking, slot__id=slot_id, slot__belongs_to=request.user)

        booking.delete()
        return Response(status=HTTP_200_OK)


class CreateSlotsForIntervalView(APIView):
    def post(self, request, *args, **kwargs):
        """Generates slots in bulk for the provided start and end interval time.

        Prevents creation of slots which conflict with the already created slots.

        """
        interval_start = datetime.datetime.strptime(request.data['interval_start'], "%Y-%m-%dT%H:%M:%SZ")
        interval_stop = datetime.datetime.strptime(request.data['interval_stop'], "%Y-%m-%dT%H:%M:%SZ")

        slot_start_time = interval_start
        slot_end_time = slot_start_time + datetime.timedelta(hours=1)
        interval_date = datetime.date(slot_start_time.year, slot_start_time.month, slot_start_time.day)
        queryset = CalendarSlot.objects.filter(belongs_to=request.user).filter(start_time__date=interval_date)
        created_slot_ids = []
        while slot_end_time <= interval_stop:
            if not queryset.filter(
                (Q(start_time__lt=slot_end_time) & Q(start_time__gte=slot_start_time)) | 
                (Q(end_time__gt=slot_start_time) & Q(end_time__lte=slot_end_time)),
                start_time__date=interval_date
            ):
                slot = CalendarSlot.objects.create(belongs_to=request.user, start_time=slot_start_time, end_time=slot_end_time)
                created_slot_ids.append(slot.uid)
            slot_start_time = slot_end_time
            slot_end_time = slot_end_time + datetime.timedelta(hours=1)
        return Response(data=created_slot_ids, status=HTTP_200_OK)
