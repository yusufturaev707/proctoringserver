from django.urls import path
from apps.barcode.views import barcode_scan, barcode_stats

urlpatterns = [
    path('', barcode_scan, name='barcode-scan'),
    path('stats/', barcode_stats, name='barcode-stats'),
]
