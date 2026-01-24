from django.db import models
from core.models.base import BaseModel


class Region(BaseModel):
    name = models.CharField(max_length=255)
    dtm_id = models.IntegerField(default=0, unique=True)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    ip_port = models.PositiveIntegerField(0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Viloyat'
        verbose_name_plural = 'Viloyatlar'
        db_table = 'region'