from django.contrib import admin

from apps.settings.models import (Computer, Settings, IPCamera, ExitPassword, )


@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = ['id', 'zone', 'name', 'ip_address', 'mac_address', 'ip_camera', 'is_active']



@admin.register(IPCamera)
class IPCameraAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'ip_address', 'mac_address', 'zone']


@admin.register(ExitPassword)
class ExitPasswordAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'password', 'is_active']
    list_display_links = ['id', 'name']


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_check_face_staff', 'is_check_face_candidate', 'is_screen_record',
                    'is_face_identification', 'is_detect_monitor', 'is_detect_camera',
                    'identification_interval', 'identification_max_fail', 'warning_timeout', 'identity_min_score_staff', 'identity_min_score_candidate', 'identity_min_score_test']
    list_display_links = ['id', 'name']
