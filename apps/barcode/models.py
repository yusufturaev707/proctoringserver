from django.db import models
from core.models.base import BaseModel


class BarcodeCode(BaseModel):
    exam = models.ForeignKey('exams.Test', on_delete=models.CASCADE, blank=True)
    exam_date = models.DateField()
    smena = models.IntegerField()
    region = models.ForeignKey('regions.Region', on_delete=models.CASCADE)
    code = models.BigIntegerField()
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.code} | {self.exam} | {self.region}"

    class Meta:
        verbose_name = 'Barcode kod'
        verbose_name_plural = 'Barcode kodlar'
        db_table = 'barcode_code'
        indexes = [
            models.Index(fields=['exam', 'exam_date', 'smena', 'region']),
            models.Index(fields=['code', 'exam', 'exam_date', 'smena', 'region']),
        ]
