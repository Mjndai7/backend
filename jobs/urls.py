from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from .views import (
    JobListAPIView, JobCreateView, JobDetailView,
    ProposalAcceptView, JobCloseView, JobApplyView,
)

app_name = 'jobs'

urlpatterns = [
    path('jobs/', JobListAPIView.as_view(), name='job-list-api'),
    path('jobs/create/', JobCreateView.as_view(), name='job-create-api'),
    path('jobs/<int:pk>/', JobDetailView.as_view(), name='job-detail-api'),
    path('jobs/<int:pk>/apply/', JobApplyView.as_view(), name='job-apply-api'),  # Include the apply view and endpoint
    path('jobs/<int:pk>/accept/<str:username>/', ProposalAcceptView.as_view(), name='proposal-accept-api'),
    path('jobs/<int:pk>/close/', JobCloseView.as_view(), name='job-close-api'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
