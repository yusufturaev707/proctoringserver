from django.contrib import admin

from apps.settings.models import Computer, Settings, IPCamera


@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = ['zone', 'name', 'ip_address', 'mac_address', 'ip_camera', 'is_active']



@admin.register(IPCamera)
class IPCameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'mac_address', 'zone']


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_check_face_staff', 'is_check_face_candidate', 'is_screen_record',
                    'is_face_identification', 'is_detect_monitor', 'is_detect_camera',
                    'identification_interval', 'identification_max_fail', 'warning_timeout', 'identity_min_score',
                    'identify_min_score_test']
