from rest_framework import serializers
from .models import Job, JobProposal


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

    def create(self, validated_data):
        # Extract the 'owner' from the request context
        client = self.context['request'].user

        # Remove 'owner' from validated_data to avoid duplication
        validated_data.pop('client', None)

        # Create and return the Job instance
        job = Job.objects.create(client=client, **validated_data)
        return job


class JobProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobProposal
        fields = '__all__'