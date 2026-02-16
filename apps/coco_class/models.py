from django.db import models

from core.models.base import BaseModel


class ModelVersion(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'model_version'
        verbose_name_plural = 'Model versions'
        verbose_name = 'Model version'
        ordering = ['id']


class CocoObjectGroup(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'coco_object_group'
        verbose_name_plural = 'Coco object groups'
        verbose_name = 'Coco object group'
        ordering = ['id']


class CocoObject(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.PositiveSmallIntegerField(unique=True)
    coco_object_group = models.ForeignKey('coco_class.CocoObjectGroup', on_delete=models.CASCADE, blank=True, null=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'coco_object'
        verbose_name_plural = 'Coco objects'
        verbose_name = 'Coco object'
        ordering = ['id']
