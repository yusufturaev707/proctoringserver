from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.notification import models


@admin.register(models.WarningNotification)
class WarningNotifAdmin(ModelAdmin):
    list_display = ['id', 'exam', 'warning_type', 'confidence', 'ip_address',
                    'mac_address', 'is_valid', 'created_at']
    list_display_links = ['id', 'exam']
    list_filter = ['warning_type', 'is_valid', 'exam']
    search_fields = ['exam__name', 'ip_address', 'mac_address', 'imei', 'description']
    list_editable = ['is_valid']
    list_select_related = ['exam']
    list_per_page = 50
    ordering = ('-id',)
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    compressed_fields = True
    warn_unsaved_form = True

    fieldsets = (
        ('Asosiy', {
            'fields': ('exam', 'warning_type', 'confidence', 'description', 'is_valid'),
            'classes': ('tab',),
        }),
        ('Tarmoq ma\'lumoti', {
            'fields': ('ip_address', 'mac_address', 'imei'),
            'classes': ('tab',),
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab',),
        }),
    )


@admin.register(models.InstallInfoLog)
class InstallInfoLogAdmin(ModelAdmin):
    list_display = ['id', 'user', 'mac', 'public_ip', 'local_ip', 'os_name', 'login_time', 'created_at']
    list_display_links = ['id', 'user']
    list_filter = ['os_name']
    search_fields = ['user__username', 'mac', 'public_ip', 'local_ip', 'os_name']
    list_select_related = ['user']
    list_per_page = 50
    ordering = ('-id',)
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    compressed_fields = True
    warn_unsaved_form = True

    fieldsets = (
        ('Asosiy', {
            'fields': ('user', 'os_name', 'login_time'),
            'classes': ('tab',),
        }),
        ('Tarmoq', {
            'fields': ('public_ip', 'local_ip', 'mac'),
            'classes': ('tab',),
        }),
        ('Joylashuv', {
            'fields': ('latitude', 'longitude'),
            'classes': ('tab',),
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab',),
        }),
    )
