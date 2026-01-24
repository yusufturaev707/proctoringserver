from django.contrib import admin

from apps.settings.models import MinScore, Computer, Settings, IPCamera


@admin.register(MinScore)
class MinScoreAdmin(admin.ModelAdmin):
    list_display = ['score']


@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'mac_address', 'ip_camera', 'info_pc', 'is_active']



@admin.register(IPCamera)
class IPCameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'mac_address', 'region']


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'mode', 'is_check_face_staff', 'is_check_face_candidate', 'is_screen_record',
                    'is_face_identification', 'timer_face_id', 'is_detect_cheating', 'is_detect_monitor',
                    'is_detect_camera']
