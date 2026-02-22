from rest_framework import serializers

from apps.exams.models import Test
from apps.notification.models import WarningNotification, InstallInfoLog


class WarningNotificationSerializer(serializers.ModelSerializer):
    exam_key = serializers.CharField(write_only=True)

    class Meta:
        model = WarningNotification
        fields = ('exam_key', 'imei', 'warning_type', 'description', 'confidence', 'ip_address', 'mac_address')

    def validate_exam_key(self, value):
        try:
            exam = Test.objects.get(key=value)
            return exam
        except Test.DoesNotExist:
            raise serializers.ValidationError('Bunday key bilan exam topilmadi')

    def create(self, validated_data):
        try:
            exam = validated_data.pop('exam_key')
            validated_data['exam'] = exam
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError(f'Saqlashda xatolik: {str(e)}')


class BulkWarningItemSerializer(serializers.Serializer):
    """Bulk ichidagi har bir warning element uchun serializer."""
    exam_key = serializers.CharField()
    imei = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    warning_type = serializers.ChoiceField(
        choices=WarningNotification.WarningType.choices,
        default=WarningNotification.WarningType.OTHER,
    )
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    confidence = serializers.FloatField(required=False, default=0.0)
    ip_address = serializers.IPAddressField(required=False, allow_null=True)
    mac_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class BulkWarningNotificationSerializer(serializers.Serializer):
    """Bitta requestda 1000 tagacha warning qabul qiluvchi serializer."""
    warnings = BulkWarningItemSerializer(many=True)

    def validate_warnings(self, items):
        if not items:
            raise serializers.ValidationError("Warnings ro'yxati bo'sh bo'lmasligi kerak.")
        if len(items) > 1000:
            raise serializers.ValidationError(
                f"Bir requestda maksimum 1000 ta warning jo'natish mumkin. Yuborildi: {len(items)}"
            )

        # Barcha exam_key'larni yig'ish va 1 ta queryda bazadan olish
        exam_keys = {item['exam_key'] for item in items}
        exams = Test.objects.filter(key__in=exam_keys)
        exam_map = {exam.key: exam for exam in exams}

        # Topilmagan key'larni tekshirish
        missing_keys = exam_keys - set(exam_map.keys())
        if missing_keys:
            raise serializers.ValidationError(
                f"Bunday key bilan exam topilmadi: {', '.join(missing_keys)}"
            )

        # Har bir itemga exam obyektini biriktirish
        for item in items:
            item['exam'] = exam_map[item['exam_key']]

        return items

    def create(self, validated_data):
        warnings = validated_data['warnings']
        notifications = [
            WarningNotification(
                exam=item['exam'],
                imei=item.get('imei'),
                warning_type=item.get('warning_type', WarningNotification.WarningType.OTHER),
                description=item.get('description'),
                confidence=item.get('confidence', 0.0),
                ip_address=item.get('ip_address'),
                mac_address=item.get('mac_address'),
            )
            for item in warnings
        ]
        created = WarningNotification.objects.bulk_create(notifications, batch_size=500)
        return created


class LoginInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallInfoLog
        fields = [
            'id', 'user', 'mac', 'public_ip', 'local_ip',
            'os_name', 'latitude', 'longitude', 'login_time'
        ]