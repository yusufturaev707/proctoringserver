from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
import requests

from apps.exams.models import Test
from apps.settings.models import Settings
from core.api_service import TestAPIClient


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'setting_mode', 'status']
    change_list_template = "exams/test_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-api/', self.admin_site.admin_view(self.import_from_api), name='test_import_api'),
        ]
        return custom_urls + urls

    def import_from_api(self, request):
        try:
            student_api = TestAPIClient()
            data = student_api.get_test_list()

            if data.get('status') != 1:
                self.message_user(request, f"{data['message']}", messages.ERROR)
                return redirect('..')

            items = data.get('data', [])

            existing_keys = set(Test.objects.values_list('key', flat=True))
            default_setting = Settings.objects.first()

            for item in items:
                key = ''
                if key not in existing_keys:
                    Test.objects.create(
                        name=item['title'],
                        key=key,
                        setting_mode=default_setting,
                        status=item['status'],
                    )
                else:
                    Test.objects.filter(key=key).update(
                        name=item['title'],
                        status=item['status'],
                    )
            self.message_user(request, f"{data['message']}.", messages.SUCCESS)

        except requests.RequestException as e:
            self.message_user(request, f"API xatosi: {e}", messages.ERROR)
        except Exception as e:
            self.message_user(request, f"Xatolik: {e}", messages.ERROR)

        return redirect('..')