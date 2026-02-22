from django.contrib import admin
from apps.notification import models

@admin.register(models.WarningNotification)
class WarningNotifAdmin(admin.ModelAdmin):
    list_display = ['exam', 'mac_address', 'ip_address', 'imei', 'warning_type', 'description', 'confidence', 'created_at', 'is_valid']


@admin.register(models.InstallInfoLog)
class InstallInfoLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'mac', 'public_ip', 'local_ip', 'os_name']
    list_display_links = ['id', 'mac', 'user']
    list_filter = ['public_ip', 'os_name', 'user']