from django.urls import path
from apps.notification.views import (SendWarningAPIView, )

urlpatterns = [
    path('send-warning-notification/', SendWarningAPIView.as_view(), name='send-warning-notification'),
]