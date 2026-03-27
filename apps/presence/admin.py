from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from apps.presence.models import PresenceConnection


@admin.register(PresenceConnection)
class PresenceConnectionAdmin(ModelAdmin):
    list_display = [
        'id', 'get_username', 'mac_address', 'get_status_badge',
        'connected_at', 'disconnected_at',
    ]
    list_display_links = ['id', 'get_username']
    list_filter = ['is_online', 'user__region']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'mac_address']
    list_select_related = ['user']
    list_per_page = 50
    ordering = ('-connected_at',)
    compressed_fields = True

    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user', 'mac_address'),
            'classes': ('tab',),
        }),
        ('Holat', {
            'fields': ('is_online', 'channel_name', 'connected_at', 'disconnected_at'),
            'classes': ('tab',),
        }),
    )

    readonly_fields = ['channel_name', 'connected_at', 'disconnected_at']

    @admin.display(description='Foydalanuvchi')
    def get_username(self, obj):
        return obj.user.username

    @admin.display(description='Holat')
    def get_status_badge(self, obj):
        if obj.is_online:
            return format_html(
                '<span style="display:inline-flex;align-items:center;gap:4px;">'
                '<span style="width:8px;height:8px;border-radius:50%;background:#10b981;'
                'display:inline-block;animation:pulse 2s infinite"></span>'
                '<span style="color:#065f46;font-weight:600;">Online</span></span>'
            )
        return format_html(
            '<span style="color:#9ca3af;">Offline</span>'
        )
