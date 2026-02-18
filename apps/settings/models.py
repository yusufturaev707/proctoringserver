from django.db import models, transaction
from core.models.base import BaseModel


class IPCamera(BaseModel):
    name = models.CharField(max_length=120)
    ip_address = models.GenericIPAddressField(unique=True)
    mac_address = models.CharField(max_length=255, unique=True)
    zone = models.ForeignKey('regions.Zone', on_delete=models.SET_NULL, blank=True, null=True)
    login = models.CharField(max_length=120, blank=True, null=True)
    password = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.ip_address}"

    class Meta:
        db_table = 'ipcamera'
        verbose_name = 'IP Camera'
        verbose_name_plural = 'IP Cameras'


class Computer(BaseModel):
    zone = models.ForeignKey('regions.Zone', on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(unique=True)
    mac_address = models.CharField(max_length=255, unique=True)
    ip_camera = models.ForeignKey('settings.IPCamera', on_delete=models.SET_NULL, blank=True, null=True)
    info_pc = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.ip_address}"

    class Meta:
        abstract = False
        verbose_name = 'Kompyuter'
        verbose_name_plural = 'Kompyuterlar'
        db_table = 'computer'


class Settings(BaseModel):
    name = models.CharField(verbose_name="Nomi", max_length=255, unique=True, blank=True, null=True)
    mode = models.PositiveSmallIntegerField(verbose_name="Mode", default=0)
    is_check_face_staff = models.BooleanField(verbose_name="Xodim", default=False)
    is_check_face_candidate = models.BooleanField(verbose_name="Talabgor", default=False)
    is_face_identification = models.BooleanField(verbose_name="Testda yuz tekshiruvi", default=False) #Test jarayonida identifikatsiya qilib turish
    identification_interval = models.PositiveSmallIntegerField(verbose_name="Interval", default=10)
    identification_max_fail = models.PositiveSmallIntegerField(verbose_name="Max Fail", default=3)
    warning_timeout = models.PositiveSmallIntegerField(verbose_name="Kutish vaqti", default=5)
    identity_min_score_staff = models.PositiveSmallIntegerField(verbose_name="Score staff", default=70)
    identity_min_score_candidate = models.PositiveSmallIntegerField(verbose_name="Score candidate", default=70)
    identity_min_score_test = models.PositiveSmallIntegerField(verbose_name="Score test", default=70)
    is_screen_record = models.BooleanField(verbose_name="Ekran yozish", default=False)
    is_detect_monitor = models.BooleanField(verbose_name="Ekran tekshiruvi", default=False)
    is_detect_camera = models.BooleanField(verbose_name="Kamera tekshiruvi", default=False)
    is_enable_detect = models.BooleanField(verbose_name="Cheating", default=False)
    detect_model = models.ForeignKey('coco_class.ModelVersion', on_delete=models.SET_NULL, blank=True, null=True)
    detect_classes = models.ManyToManyField('coco_class.CocoObject', related_name='detect_classes')
    detect_confidence = models.FloatField(verbose_name="Confidence", default=0.5)
    detect_frame_skip = models.PositiveSmallIntegerField(verbose_name="Skip frame", default=20)


    def __str__(self):
        return str(self.name)

    class Meta:
        abstract = False
        verbose_name = 'Sozlama'
        verbose_name_plural = 'Sozlamalar'
        db_table = 'settings'


class ExitPassword(BaseModel):
    name = models.CharField(verbose_name="Dasturdan chiqish", max_length=255, blank=True, null=True)
    password = models.CharField(max_length=120, unique=True, blank=True, default='123')
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            with transaction.atomic():
                ExitPassword.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"

    class Meta:
        db_table = 'exitpassword'
        verbose_name = 'Exit Password'
        verbose_name_plural = 'Exit Passwords'
        ordering = ['id']