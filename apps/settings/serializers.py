from rest_framework import serializers
from apps.settings.models import Settings

class SettingSerializer(serializers.ModelSerializer):
    detect_model = serializers.CharField(source='detect_model.code', read_only=True)
    detect_classes = serializers.SlugRelatedField(many=True, read_only=True, slug_field='code')
    class Meta:
        model = Settings
        fields = [
            'id', 'name', 'mode', 'is_check_face_staff', 'is_check_face_candidate',
            'is_face_identification', 'identification_interval', 'identification_max_fail', 'warning_timeout',
            'identity_min_score_staff', 'identity_min_score_candidate', 'identity_min_score_test',
            'is_screen_record', 'is_detect_monitor', 'is_detect_camera',
            'is_enable_detect', 'detect_model', 'detect_confidence', 'detect_frame_skip', 'detect_classes'
        ]