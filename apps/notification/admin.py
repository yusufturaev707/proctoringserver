from django.contrib import admin
from apps.notification import models

@admin.register(models.WarningNotif)
class WarningNotifAdmin(admin.ModelAdmin):
    list_display = ['exam', 'pc', 'imei', 'text', 'created_at']