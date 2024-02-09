from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("auth/api/", include("authentication.urls")),
    path('user/api/', include('user.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/chat/', include('chat.urls')),
    path('jobs/api/', include('jobs.urls')),
    path('direct_messages/api/', include('direct_messages.urls')),
 

    path('api/calendly/', include('calendly.urls')),
    path('api/ticketing/', include('ticketing.urls')),
    path('api/agora/', include('agora.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
