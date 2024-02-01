# Create your views here.
import datetime
from django.http import JsonResponse
from django.http.response import HttpResponseBadRequest
from django.core import serializers
from django.core.mail import send_mail
from django.db.models import Count
from .get_email import EmailDownload  # Import  email  logic here
from rest_framework.decorators import api_view, permission_classes

from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.views import generic
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .forms import TicketForm, TicketUpdateForm
from .models import Ticket, Comment
from .serializers import TicketSerializer, CommentSerializer

class TicketListView(APIView):
    def get(self, request, format=None):
        tickets = Ticket.objects.all()
        serializer = TicketSerializer(tickets, many=True)
        
        if request.user.is_superuser:
            context = {
                'all_issues': Ticket.objects.all().count(),
                'urgent_count': Ticket.objects.filter(urgent_status=True).count(),
                'resolved_count': Ticket.objects.filter(completed_status=True).count(),
                'unresolved_count': Ticket.objects.filter(completed_status=False).count(),
                'client_user_list': Ticket.objects.filter(user=request.user),
                'consultant_user_list': Ticket.objects.filter(assigned_to=request.user),
                'client_tickets': Ticket.objects.filter(ticket_section='Client').count(),
                'consultant_tickets': Ticket.objects.filter(ticket_section='Consultant').count(),
                'admin_tickets': Ticket.objects.filter(ticket_section='Admin').count(),
                'infracture_tickets': Ticket.objects.filter(ticket_section='Infrastructure and Networking').count(),
                'dbadmin_tickets': Ticket.objects.filter(ticket_section='Database Administrator').count()
            }
            return Response({'tickets': serializer.data, 'context': context})
        
        elif request.user.is_staff:
            context = {
                'all_issues': Ticket.objects.filter(assigned_to=request.user).count(),
                'urgent_count': Ticket.objects.filter(assigned_to=request.user, urgent_status=True).count(),
                'resolved_count': Ticket.objects.filter(assigned_to=request.user, completed_status=True).count(),
                'unresolved_count': Ticket.objects.filter(assigned_to=request.user, completed_status=False).count(),
                'client_user_list': Ticket.objects.filter(user=request.user),
                'consultant_user_list': Ticket.objects.filter(assigned_to=request.user),
                'client_tickets': Ticket.objects.filter(ticket_section='Client', assigned_to=request.user).count(),
                'consultant_tickets': Ticket.objects.filter(ticket_section='Consultant', assigned_to=request.user).count(),
                'admin_tickets': Ticket.objects.filter(ticket_section='Admin', assigned_to=request.user).count(),
                'infracture_tickets': Ticket.objects.filter(ticket_section='Infrastructure and Networking', assigned_to=request.user).count(),
                'dbadmin_tickets': Ticket.objects.filter(ticket_section='Database Administrator', assigned_to=request.user).count()
            }
            return Response({'tickets': serializer.data, 'context': context})

class TicketDetailAPIView(APIView):
    def get(self, request, pk, format=None):
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({"detail": "Ticket not found."}, status=404)

        ticket_serializer = TicketSerializer(ticket)
        comments = Comment.objects.filter(ticket=ticket).order_by('-created_date')
        comment_serializer = CommentSerializer(comments, many=True)

        data = {
            "ticket": ticket_serializer.data,
            "comments": comment_serializer.data
        }
        return Response(data)


class TicketCreateAPIView(APIView):
    def post(self, request, format=None):
        serializer = TicketSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketCreateAPIView(APIView):
    def post(self, request, format=None):
        # Deserialize JSON data using the TicketSerializer
        serializer = TicketSerializer(data=request.data)
        
        # Validate JSON data
        if serializer.is_valid():
            # Create a new ticket from the serialized data
            serializer.save(user=request.user)

            # Create a new ticket from the form data
            form = TicketForm(request.data)
            if form.is_valid():
                form.instance.user = request.user
                form.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # If JSON data is not valid, try to create the ticket from the form data
            form = TicketForm(request.data)
            if form.is_valid():
                form.instance.user = request.user
                form.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If neither JSON nor form data is valid, return error responses
        errors = serializer.errors
        errors.update(form.errors if form.errors else {})
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)



class TicketUpdateAPIView(APIView):
    def put(self, request, pk, format=None):
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({"detail": "Ticket not found."}, status=404)

        # Deserialize and update the ticket using the TicketUpdateSerializer
        serializer = TicketSerializer(ticket, data=request.data)
        
        # Attempt to update the ticket using the TicketUpdateForm
        form = TicketUpdateForm(request.data, instance=ticket)
        if form.is_valid():
            form.save()
            return Response(serializer.data)

        # If form update is not valid, check if serializer update is valid
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            {"errors": {"serializer": serializer.errors, "form": form.errors}},
            status=status.HTTP_400_BAD_REQUEST
        )


class TicketDeleteAPIView(APIView):
    def delete(self, request, pk, format=None):
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({"detail": "Ticket not found."}, status=404)

        ticket.delete()
        return Response({"detail": "Ticket deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
def ticket_list_api(request):
    tickets = Ticket.objects.all()
    serializer = TicketSerializer(tickets, many=True)
    return JsonResponse({"tickets": serializer.data}, safe=False)

def urgent_ticket_list_api(request):
    if request.user.is_superuser:
        tickets = Ticket.objects.filter(urgent_status=True)
    else:
        tickets = Ticket.objects.filter(assigned_to=request.user, urgent_status=True)
    
    serializer = TicketSerializer(tickets, many=True)
    return JsonResponse({"tickets": serializer.data}, safe=False)


def unresolved_tickets_api(request):
    if request.user.is_superuser:
        tickets = Ticket.objects.filter(completed_status=False)
    else:
        tickets = Ticket.objects.filter(assigned_to=request.user, completed_status=False)
    
    serializer = TicketSerializer(tickets, many=True)
    return JsonResponse({"tickets": serializer.data}, safe=False)

def mark_ticket_as_resolved_api(request, id):
    if request.method == 'POST':
        try:
            ticket = Ticket.objects.get(id=id)
        except Ticket.DoesNotExist:
            return JsonResponse({"detail": "Ticket not found."}, status=404)

        comment_text = request.POST.get('comment', '')

        # Update the ticket and add a comment
        if not ticket.completed_status:
            user = request.user
            date_time = datetime.datetime.now()
            ticket.resolved_by = user
            ticket.resolved_date = date_time
            ticket.completed_status = True
            ticket.save()
            comment = Comment.objects.create(ticket=ticket, user=user, text=comment_text)

            # Send an email notification
            subject = 'Issue resolved'
            message = f'Good day.\n Please note your issue: \n{ticket.issue_description}\n has been resolved successfully\nRegards,\n Elloe Helpdesk'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [ticket.customer_email]
            send_mail(subject, message, email_from, recipient_list)

            # Serialize the updated ticket and comment
            data = {
                'ticket': serializers.serialize('json', [ticket]),
                'comment': serializers.serialize('json', [comment]),
            }
            return JsonResponse(data, status=200)

    return HttpResponseBadRequest("Bad Request")


def mark_ticket_as_unresolved_api(request, id):
    try:
        ticket = Ticket.objects.get(id=id)
    except Ticket.DoesNotExist:
        return JsonResponse({"detail": "Ticket not found."}, status=404)

    if request.method == 'POST':
        ticket.completed_status = False
        ticket.save()

        # Serialize the updated ticket
        data = {
            'ticket': serializers.serialize('json', [ticket]),
        }
        return JsonResponse(data, status=200)

    return HttpResponseBadRequest("Bad Request")



def add_comment_api(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return JsonResponse({"detail": "Ticket not found."}, status=404)

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '')
        user = request.user
        date_time = datetime.datetime.now()

        comment = Comment.objects.create(ticket=ticket, user=user, text=comment_text)

        # Update the ticket resolved information if needed
        if not ticket.completed_status:
            ticket.resolved_by = user
            ticket.resolved_by = date_time
            ticket.completed_status = True
            ticket.save()

        # Serialize the updated ticket and new comment
        data = {
            'ticket': serializers.serialize('json', [ticket]),
            'comment': serializers.serialize('json', [comment]),
        }
        return JsonResponse(data, status=200)

    return HttpResponseBadRequest("Bad Request")


def search_results_api(request):
    query = request.GET.get("q")
    if not query:
        return HttpResponseBadRequest("Bad Request: 'q' parameter missing")

    object_list = Ticket.objects.filter(
        Q(title__icontains=query) | Q(customer_full_name__icontains=query) | Q(
            issue_description__icontains=query)
    ).filter(user=request.user)

    # Serialize the queryset to JSON
    data = {
        'results': serializers.serialize('json', object_list),
    }
    return JsonResponse(data, status=200)


def staff_search_results_api(request):
    query = request.GET.get("q")
    if not query:
        return HttpResponseBadRequest("Bad Request: 'q' parameter missing")

    object_list = Ticket.objects.filter(
        Q(title__icontains=query) | Q(customer_full_name__icontains=query) | Q(
            issue_description__icontains=query)
    ).filter(assigned_to=request.user)

    # Serialize the queryset to JSON
    data = {
        'results': serializers.serialize('json', object_list),
    }
    return JsonResponse(data, status=200)


def all_search_results_api(request):
    query = request.GET.get("q")
    if not query:
        return HttpResponseBadRequest("Bad Request: 'q' parameter missing")

    object_list = Ticket.objects.filter(
        Q(title__icontains=query) | Q(customer_full_name__icontains=query) | Q(
            issue_description__icontains=query)
    )

    # Serialize the queryset to JSON
    data = {
        'results': serializers.serialize('json', object_list),
    }
    return JsonResponse(data, status=200)


def user_performance_api(request):
    queryset = Ticket.objects.values('resolved_by__username').annotate(
        resolved_count=Count('resolved_by'))

    # Serialize the queryset to JSON
    data = {
        'user_performance': list(queryset),
    }

    # Include additional context data in the JSON response
    vals = list(queryset)
    my_users = [str(x['resolved_by__username']) for x in vals]
    my_users.pop(0)
    data['my_users'] = my_users

    user_num_tickets = [i['resolved_count'] for i in vals]
    user_num_tickets.pop(0)
    data['user_num_tickets'] = user_num_tickets

    return JsonResponse(data, status=200)


def user_performance_details_api(request, username):
    user = get_object_or_404(User, username=username)
    tickets = Ticket.objects.filter(assigned_to=user)
    resolved_tickets = Ticket.objects.filter(
        assigned_to=user, completed_status=True)
    unresolved_tickets = Ticket.objects.filter(
        assigned_to=user, completed_status=False)
    resolved_count = resolved_tickets.count()
    unresolved_count = unresolved_tickets.count()

    # Serialize the data to JSON
    data = {
        'user_details': {
            'username': user.username,
            'resolved_count': resolved_count,
            'unresolved_count': unresolved_count,
        },
        'tickets': serializers.serialize('json', tickets),
        'resolved_tickets': serializers.serialize('json', resolved_tickets),
        'unresolved_tickets': serializers.serialize('json', unresolved_tickets),
    }

    return JsonResponse(data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def retrieve_emails(request):
    user = request.user  # Assuming you are using authentication to get the user
    email = user.email
    password = request.data.get('password', '')  # Retrieve the password from the request data

    try:
        retrieved_emails = EmailDownload(email, password).retrieve_emails()
        return Response({'emails': retrieved_emails}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


