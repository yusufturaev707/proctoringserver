from django.db import models
from core.models.base import BaseModel


class MinScore(BaseModel):
    score = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return str(self.score)

    class Meta:
        db_table = 'minscore'
        verbose_name = 'Minimum chegara'
        verbose_name_plural = 'Minimum chegaralar'


class IPCamera(BaseModel):
    name = models.CharField(max_length=120)
    ip_address = models.GenericIPAddressField(unique=True)
    mac_address = models.CharField(max_length=255, unique=True)
    region = models.ForeignKey('regions.Region', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.ip_address}"

    class Meta:
        db_table = 'ipcamera'
        verbose_name = 'IP Camera'
        verbose_name_plural = 'IP Cameras'


class Computer(BaseModel):
    name = models.CharField(max_length=255, unique=True, blank=True, null=True)
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
    name = models.CharField(max_length=255, unique=True, blank=True, null=True)
    mode = models.PositiveSmallIntegerField(default=0)
    is_check_face_staff = models.BooleanField(default=False)
    is_check_face_candidate = models.BooleanField(default=False)
    is_screen_record = models.BooleanField(default=False)
    is_face_identification = models.BooleanField(default=False) #Test jarayonida identifikatsiya qilib turish
    timer_face_id = models.PositiveSmallIntegerField(default=10)
    is_detect_cheating = models.BooleanField(default=False)
    is_detect_monitor = models.BooleanField(default=False)
    is_detect_camera = models.BooleanField(default=False)


    def __str__(self):
        return str(self.name)

    class Meta:
        abstract = False
        verbose_name = 'Sozlama'
        verbose_name_plural = 'Sozlamalar'
        db_table = 'settings'

