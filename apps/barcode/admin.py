from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.barcode.models import BarcodeCode


@admin.register(BarcodeCode)
class BarcodeCodeAdmin(ModelAdmin):
    list_display = ('code', 'exam', 'exam_date', 'smena', 'region', 'is_sent')
    list_filter = ('exam', 'exam_date', 'smena', 'region', 'is_sent')
    search_fields = ('code',)
    list_per_page = 50
