from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from apps.barcode.models import BarcodeCode
from apps.users.models import BarcodeUpload


class DatePickerFilter(admin.SimpleListFilter):
    title = 'Sana'
    parameter_name = 'exam_date'
    template = 'admin/barcode/datepicker_filter.html'

    def lookups(self, request, model_admin):
        return (('custom', 'Sana tanlang'),)

    def queryset(self, request, queryset):
        value = self.value()
        if value and value != 'custom':
            return queryset.filter(exam_date=value)
        return queryset

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': 'Barchasi',
            'value': self.value() or '',
        }


@admin.register(BarcodeCode)
class BarcodeCodeAdmin(ModelAdmin):
    list_display = ('code', 'exam', 'exam_date', 'smena', 'region', 'is_sent')
    list_filter = ('exam', DatePickerFilter, 'smena', 'region', 'is_sent')
    search_fields = ('code',)
    list_per_page = 50
    change_list_template = 'admin/barcode/barcodecode_changelist.html'

    def get_urls(self):
        custom_urls = [
            path(
                'generate/',
                self.admin_site.admin_view(self.generate_codes_view),
                name='barcode_barcodecode_generate',
            ),
        ]
        return custom_urls + super().get_urls()

    def generate_codes_view(self, request):
        from apps.barcode.views import admin_generate_codes
        return admin_generate_codes(request)


@admin.register(BarcodeUpload)
class BarcodeUploadAdmin(ModelAdmin):
    list_display = ('code', 'exam', 'exam_date', 'smena', 'region', 'uploaded_by', 'is_valid')
    list_filter = ('exam', DatePickerFilter, 'smena', 'region', 'is_valid')
    search_fields = ('code', 'uploaded_by__username')
    list_per_page = 50
    readonly_fields = ('code', 'uploaded_by')
    change_list_template = 'admin/barcode/barcodeupload_changelist.html'

    def get_urls(self):
        custom_urls = [
            path(
                'validate/',
                self.admin_site.admin_view(self.validate_uploads_view),
                name='users_barcodeupload_validate',
            ),
        ]
        return custom_urls + super().get_urls()

    def validate_uploads_view(self, request):
        from apps.barcode.views import admin_validate_uploads
        return admin_validate_uploads(request)
