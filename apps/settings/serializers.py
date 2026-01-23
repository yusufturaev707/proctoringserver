from rest_framework import serializers
from apps.settings.models import Settings


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = ['id', 'name', 'mode', 'is_check_face_staff', 'is_check_face_candidate', 'is_screen_record', 'is_face_identification', 'timer_face_id', 'is_detect_cheating', 'is_detect_monitor', 'is_detect_camera']