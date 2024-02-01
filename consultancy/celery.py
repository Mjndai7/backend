import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'consultancy.settings')

app = Celery('consultancy')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
