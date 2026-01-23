from django.urls import path
from apps.exams.views import LoadTestsAPIView, CheckCandidateAPIView

urlpatterns = [
    path('load-tests/', LoadTestsAPIView.as_view(), name='load-tests'),
    path('check-candidate-exam/', CheckCandidateAPIView.as_view(), name='check-candidate-exam'),
]