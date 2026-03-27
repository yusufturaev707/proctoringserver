from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.barcode.models import BarcodeCode
from apps.users.models import BarcodeUpload


@admin.register(BarcodeCode)
class BarcodeCodeAdmin(ModelAdmin):
    list_display = ('code', 'exam', 'exam_date', 'smena', 'region', 'is_sent')
    list_filter = ('exam', 'exam_date', 'smena', 'region', 'is_sent')
    search_fields = ('code',)
    list_per_page = 50


@admin.register(BarcodeUpload)
class BarcodeUploadAdmin(ModelAdmin):
    list_display = ('code', 'exam', 'exam_date', 'smena', 'region', 'uploaded_by', 'is_valid')
    list_filter = ('exam', 'exam_date', 'smena', 'region', 'is_valid')
    search_fields = ('code', 'uploaded_by__username')
    list_per_page = 50
    readonly_fields = ('code', 'uploaded_by')
