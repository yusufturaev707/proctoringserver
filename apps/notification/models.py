from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel


class WarningNotification(BaseModel):
    class WarningType(models.TextChoices):
        NO_FACE = 'no_face', _('Yuz aniqlanmadi')
        MULTIPLE_FACES = 'multiple_faces', _('Bir nechta yuz aniqlandi')
        PHONE_DETECTED = 'phone_detected', _('Telefon aniqlandi')
        FORBIDDEN_OBJECT = 'forbidden_object', _('Taqiqlangan buyum')
        TAB_SWITCH = 'tab_switch', _('Tab yoki oyna almashdi')
        LOOKING_AWAY = 'looking_away', _('Chetga qarash')
        VOICE_DETECTED = 'voice_detected', _('Ovoz aniqlandi')
        OTHER = 'other', _('Boshqa')

    exam = models.ForeignKey('exams.Test', on_delete=models.CASCADE, related_name='warnings_exam')
    imei = models.CharField(max_length=14, blank=True, null=True)
    warning_type = models.CharField(
        max_length=50,
        choices=WarningType.choices,
        default=WarningType.OTHER
    )
    description = models.TextField(blank=True, null=True)
    confidence = models.FloatField(default=0.0, blank=True, null=True) # Masalan: 0.98 (98% ishonch bilan bu telefon)
    is_valid = models.BooleanField(default=True, help_text="Ogohlantirish haqiqiy qoidabuzarlikmi?") # Admin tomonidan tasdiqlash (False positive'larni ajratish uchun)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(blank=True, null=True, max_length=32)

    def __str__(self):
        return f'{self.exam} - {self.get_warning_type_display()} ({self.confidence})'

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ('-id',)
        indexes = [
            models.Index(fields=['exam', 'warning_type', 'ip_address', 'mac_address']),
        ]
        db_table = 'warning_notification'