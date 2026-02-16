from django.urls import path
from apps.notification.views import (
    SendWarningAPIView,
    BulkSendWarningAPIView,
    BulkWarningTaskStatusAPIView,
)

urlpatterns = [
    path('send-warning-notification/', SendWarningAPIView.as_view(), name='send-warning-notification'),
    path('bulk-send-warning-notification/', BulkSendWarningAPIView.as_view(), name='bulk-send-warning-notification'),
    path('bulk-warning-task-status/<str:task_id>/', BulkWarningTaskStatusAPIView.as_view(), name='bulk-warning-task-status'),
]
