from django.db import models
from core.models.base import BaseModel

class Test(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    key = models.CharField(max_length=100, blank=True, null=True)
    setting_mode = models.ForeignKey("settings.Settings", on_delete=models.SET_NULL, blank=True, null=True)
    status = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        abstract = False
        verbose_name = 'Test'
        verbose_name_plural = 'Testlar'
        db_table = 'test'