from django.shortcuts import redirect, get_object_or_404, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView, ListView,
    DetailView, RedirectView,
)
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.models import User

from direct_messages.services import MessagingService
from direct_messages.models import ChatRoom

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Job, JobProposal
from .serializers import JobSerializer, JobProposalSerializer

class JobListAPIView(APIView):
    """
    Show a list of jobs.
    """

    def get(self, request, format=None):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])  # Add your authentication class here
@permission_classes([IsAuthenticated])
class JobCreateView(generics.CreateAPIView):
    """
    Create a job.
    """
    serializer_class = JobSerializer

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        messages.success(request, 'The job was created with success!')
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class JobDetailView(generics.RetrieveAPIView):
    """
    Show the job's detail.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get(self, request, *args, **kwargs):
        job = self.get_object()

        # Assuming JobProposalSerializer is defined for JobProposal model
        current_proposal = JobProposal.objects.filter(job=job, consultant=request.user).first()
        current_proposal_serializer = JobProposalSerializer(current_proposal)

        serializer_context = {'request': request}
        job_serializer = JobSerializer(job, context=serializer_context)

        context_data = {
            'current_proposal': current_proposal_serializer.data,
            'job': job_serializer.data,
        }

        return Response(context_data, status=status.HTTP_200_OK)


class JobApplyView(generics.CreateAPIView):
    """
    Try to apply a job.
    """
    queryset = JobProposal.objects.all()
    serializer_class = JobProposalSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        job_id = self.kwargs.get('pk')
        job = get_object_or_404(Job, pk=job_id)
        serializer.save(job=job, consultant=self.request.user)

class ProposalAcceptView(APIView):
    def post(self, request, pk, username, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)

        # Ensure the user accepting the proposal is the job owner
        if request.user != job.client:
            return Response({'detail': 'You are not the owner of this job.'}, status=status.HTTP_403_FORBIDDEN)

        # Ensure the job is in 'active' status and has no assigned freelancer
        if job.status != 'active' or job.freelancer is not None:
            return Response({'detail': 'Job cannot be accepted at the moment.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the freelancer and update the job status
        consultant = get_object_or_404(User, username=username)
        job.consultant = consultant
        job.status = 'working'
        job.save()

        # Create or get the chatroom
        chatroom, created = ChatRoom.objects.get_or_create(sender=request.user, recipient=consultant)
        if not created:
            # If chatroom already exists, update it
            chatroom.save()

        # Send a message to notify the freelancer
        MessagingService().send_message(
            sender=request.user,
            recipient=consultant,
            message=f"Hi {consultant.username},\n\nYour proposal is accepted.\n\nProject details: {reverse('jobs:job_detail', kwargs={'pk': job.pk})}"
        )

        # Send a success message
        messages.success(request, f'User: {consultant.username} is assigned to your project.')

        # Serialize the updated job and return the response
        serializer = JobSerializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)


class JobCloseView(APIView):
    def post(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)

        # Ensure the user closing the job is the job owner
        if request.user != job.client:
            return Response({'detail': 'You are not the owner of this job.'}, status=status.HTTP_403_FORBIDDEN)

        # Ensure the job is in 'working' status and has an assigned freelancer
        if job.status != 'working' or job.consultant is None:
            return Response({'detail': 'Job cannot be closed at the moment.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the job status to 'ended'
        job.status = 'ended'
        job.save()

        # Send a warning message
        messages.warning(request, 'Job is ended successfully')

        # Serialize the updated job and return the response
        serializer = JobSerializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)


    

