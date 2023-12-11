from django.db import models
class BookedConsultation(models.Model):
    normal_user = models.ForeignKey('accounts.NormalUser', on_delete=models.CASCADE)
    consultant = models.ForeignKey('accounts.Consultant', on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    # Add other fields as needed

    def __str__(self):
        return f"{self.normal_user.email} - {self.consultant.email}"