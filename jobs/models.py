from django.db import models
from user.models import User

# Create your models here.
from taggit.managers import TaggableManager

class Job(models.Model):
    """
    Model to create a Job

    Attributes:
    date_created (datetime): Datetime of job creation.
    date_modified (datetime): Datetime of job modified.
    document (file): Job description file.
    consultant (user): Freelancer who's being assigned the job.
    job_description (str): Job description.
    job_title (str): Job title.
    client (user): User who owns the job.
    price (decimal): Job price.
    status (str): Job current status.
    tags (str): Tags representing job.
    """
    client = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="client")
    consultant = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="consultant")
    job_title = models.CharField(max_length=255)
    job_description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    tags = TaggableManager()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    document =models.FileField(upload_to='attachments', blank=True, null=True)

    ACTIVE = 'active'
    WORKING = 'working'
    ENDED = 'ended'
    CHOICES = ((ACTIVE, 'active'), (WORKING, 'working'), (ENDED, 'ended'))

    status = models.CharField(max_length=12, choices=CHOICES, default=ACTIVE)


    class Meta:
        verbose_name = 'job'
        verbose_name_plural = 'jobs'
        unique_together = ('client', 'date_created')

    
    def __str__(self):
        return "%s - %s - %s" % (
            self.client.email if self.client else '',
            self.consultant.email() if self.consultant else '',
            self.status

        )
    
    @property
    def consultants(self):
        """
        It prepares all the consultants of the current job.
        """
        proposals = self.job_proposal.all()
        return [proposal.consultant for proposal in proposals]

class JobProposal(models.Model):
    """
    Model to create a consultant's proposal for a JOB

    Attributes:
    consultant(freelancer) User who submits job proposal
    job (job): Job object
    proposal (text): User proposal for the job
    """
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='job_proposal')
    consultant = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='job_proposal')
    proposal = models.TextField()
    

    class Meta:
        unique_together = ('job', 'consultant')





