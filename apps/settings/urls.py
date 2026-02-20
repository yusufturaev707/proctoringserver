from django.urls import path
from apps.settings.views import (CheckPermissionDeviceAPIView, )

urlpatterns = [
    path('check-permission-device/', CheckPermissionDeviceAPIView.as_view(), name='check-permission-device'),
]