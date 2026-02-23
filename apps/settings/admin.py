from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.settings.models import Computer, Settings, IPCamera, ExitPassword, AllowPublicIp


@admin.register(IPCamera)
class IPCameraAdmin(ModelAdmin):
    list_display = ['id', 'name', 'ip_address', 'mac_address', 'zone']
    list_display_links = ['id', 'name']
    list_filter = ['zone']
    search_fields = ['name', 'ip_address', 'mac_address']
    list_select_related = ['zone']
    list_per_page = 25
    ordering = ('id',)
    compressed_fields = True
    warn_unsaved_form = True

    fieldsets = (
        ('Asosiy', {
            'fields': ('name', 'zone'),
            'classes': ('tab',),
        }),
        ('Tarmoq', {
            'fields': ('ip_address', 'mac_address'),
            'classes': ('tab',),
        }),
        ('Kirish ma\'lumotlari', {
            'fields': ('login', 'password'),
            'classes': ('tab',),
        }),
    )


@admin.register(Computer)
class ComputerAdmin(ModelAdmin):
    list_display = ['id', 'get_region_name', 'zone', 'name', 'ip_address', 'mac_address', 'ip_camera', 'is_active']
    list_display_links = ['id', 'name']
    list_filter = ['zone', 'is_active', 'zone__region']
    search_fields = ['name', 'ip_address', 'mac_address', 'zone__name', 'zone__region__name']
    list_editable = ['is_active']
    list_select_related = ['zone', 'zone__region', 'ip_camera']
    list_per_page = 25
    ordering = ('id',)
    compressed_fields = True
    warn_unsaved_form = True

    fieldsets = (
        ('Asosiy', {
            'fields': ('name', 'zone', 'ip_camera', 'is_active'),
            'classes': ('tab',),
        }),
        ('Tarmoq', {
            'fields': ('ip_address', 'mac_address'),
            'classes': ('tab',),
        }),
        ('Qo\'shimcha ma\'lumot', {
            'fields': ('info_pc',),
            'classes': ('tab',),
        }),
    )

    @admin.display(description='Viloyat')
    def get_region_name(self, obj):
        return obj.zone.region.name if obj.zone and obj.zone.region else '—'


@admin.register(AllowPublicIp)
class AllowPublicIpAdmin(ModelAdmin):
    list_display = ['id', 'get_region_name', 'zone', 'name', 'ip_address', 'is_active']
    list_display_links = ['id', 'name']
    list_filter = ['zone', 'is_active', 'zone__region']
    search_fields = ['name', 'ip_address', 'zone__name', 'zone__region__name']
    list_editable = ['is_active']
    list_select_related = ['zone', 'zone__region']
    list_per_page = 25
    ordering = ('id',)
    compressed_fields = True
    warn_unsaved_form = True

    @admin.display(description='Viloyat')
    def get_region_name(self, obj):
        return obj.zone.region.name if obj.zone and obj.zone.region else '—'


@admin.register(ExitPassword)
class ExitPasswordAdmin(ModelAdmin):
    list_display = ['id', 'name', 'password', 'is_active']
    list_display_links = ['id', 'name']
    list_filter = ['is_active']
    search_fields = ['name', 'password']
    list_per_page = 25
    compressed_fields = True


@admin.register(Settings)
class SettingsAdmin(ModelAdmin):
    list_display = ['id', 'name', 'mode', 'is_check_face_staff', 'is_check_face_candidate',
                    'is_face_identification', 'is_screen_record', 'is_detect_monitor',
                    'is_detect_camera', 'is_enable_detect', 'is_enable_rdp_detect']
    list_display_links = ['id', 'name']
    search_fields = ['name']
    list_per_page = 25
    filter_horizontal = ['detect_classes', 'rdp_objects']
    compressed_fields = True
    warn_unsaved_form = True

    fieldsets = (
        ('Asosiy', {
            'fields': ('name', 'mode'),
            'classes': ('tab',),
        }),
        ('Yuz tekshiruvi', {
            'fields': (
                'is_check_face_staff', 'is_check_face_candidate',
                'is_face_identification',
                'identification_interval', 'identification_max_fail', 'warning_timeout',
                'identity_min_score_staff', 'identity_min_score_candidate', 'identity_min_score_test',
            ),
            'classes': ('tab',),
        }),
        ('Qurilma nazorati', {
            'fields': ('is_screen_record', 'is_detect_monitor', 'is_detect_camera'),
            'classes': ('tab',),
        }),
        ('Cheating aniqlash (YOLO)', {
            'fields': (
                'is_enable_detect', 'detect_model',
                'detect_classes', 'detect_confidence', 'detect_frame_skip',
            ),
            'classes': ('tab',),
        }),
        ('RDP nazorati', {
            'fields': ('is_enable_rdp_detect', 'rdp_objects'),
            'classes': ('tab',),
        }),
    )
