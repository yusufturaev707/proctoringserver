from django.urls import path
from apps.settings.views import (CheckAllowPublicIpAPIView, )

urlpatterns = [
    path('check-perm-public-ip/', CheckAllowPublicIpAPIView.as_view(), name='check-perm-public-ip'),
]