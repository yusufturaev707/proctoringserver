from celery import shared_task
from django.db import transaction

from apps.exams.models import Test
from apps.notification.models import WarningNotification


@shared_task
def process_bulk_warnings(warnings_data):
    """Background task: bulk create warning notifications."""
    exam_keys = {item['exam_key'] for item in warnings_data}
    exams = Test.objects.filter(key__in=exam_keys)
    exam_map = {exam.key: exam.pk for exam in exams}

    missing_keys = exam_keys - set(exam_map.keys())
    if missing_keys:
        raise ValueError(f"Exam topilmadi: {', '.join(missing_keys)}")

    notifications = [
        WarningNotification(
            exam_id=exam_map[item['exam_key']],
            imei=item.get('imei'),
            warning_type=item.get('warning_type', WarningNotification.WarningType.OTHER),
            description=item.get('description'),
            confidence=item.get('confidence', 0.0),
            ip_address=item.get('ip_address'),
            mac_address=item.get('mac_address'),
        )
        for item in warnings_data
    ]

    with transaction.atomic():
        created = WarningNotification.objects.bulk_create(notifications, batch_size=500)

    return {'created_count': len(created)}
