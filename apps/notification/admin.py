from django.contrib import admin
from apps.notification import models

@admin.register(models.WarningNotification)
class WarningNotifAdmin(admin.ModelAdmin):
    list_display = ['exam', 'imei', 'description', 'created_at']