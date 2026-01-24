from django.db import models

from core.models.base import BaseModel


class WarningNotif(BaseModel):
    exam = models.ForeignKey('exams.Test', on_delete=models.CASCADE, related_name='warnings_exam')
    pc = models.ForeignKey('settings.Computer', on_delete=models.CASCADE, related_name='warnings_pc')
    imei = models.CharField(max_length=14, blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.exam} {self.pc} {self.imei}'