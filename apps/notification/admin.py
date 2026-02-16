from django.contrib import admin
from apps.notification import models

@admin.register(models.WarningNotification)
class WarningNotifAdmin(admin.ModelAdmin):
    list_display = ['exam', 'mac_address', 'ip_address', 'imei', 'warning_type', 'description', 'confidence', 'created_at', 'is_valid']