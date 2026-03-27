from django.urls import path
from apps.barcode.views import barcode_scan

urlpatterns = [
    path('', barcode_scan, name='barcode-scan'),
]
