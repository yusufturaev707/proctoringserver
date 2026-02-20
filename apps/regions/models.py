from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseModel


class Region(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    dtm_id = models.IntegerField(default=0, unique=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Viloyat'
        verbose_name_plural = 'Viloyatlar'
        db_table = 'region'


class Zone(BaseModel):
    region = models.ForeignKey("regions.Region", verbose_name=_("Viloyat"), on_delete=models.SET_NULL, null=True, help_text='Hudud')
    name = models.CharField(max_length=255, verbose_name=_("Nom"))
    number = models.IntegerField(default=0, verbose_name=_("Nomer"))
    status = models.BooleanField(default=True, verbose_name=_("Holat"))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Bino'
        verbose_name_plural = 'Binolar'
        db_table = 'zone'