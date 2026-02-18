from rest_framework import serializers

from apps.exams.models import Test
from apps.settings.serializers import SettingSerializer
from apps.users.models import User


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['embedding']



class TestSerializer(serializers.ModelSerializer):
    setting_mode = SettingSerializer(read_only=True)
    class Meta:
        model = Test
        fields = ['id', 'name', 'key', 'setting_mode', 'site_url', 'status']