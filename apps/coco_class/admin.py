from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.coco_class.models import ModelVersion, CocoObjectGroup, CocoObject, RdpObject, HotKeyboardKey


@admin.register(ModelVersion)
class ModelVersionAdmin(ModelAdmin):
    list_display = ['id', 'name', 'code', 'status']
    list_display_links = ['id', 'name']
    list_filter = ['status']
    search_fields = ['name', 'code']
    list_editable = ['status']
    list_per_page = 25
    compressed_fields = True


@admin.register(CocoObjectGroup)
class CocoObjectGroupAdmin(ModelAdmin):
    list_display = ['id', 'name', 'code', 'status']
    list_display_links = ['id', 'name']
    list_filter = ['status']
    search_fields = ['name', 'code']
    list_editable = ['status']
    list_per_page = 25
    compressed_fields = True


@admin.register(CocoObject)
class CocoObjectAdmin(ModelAdmin):
    list_display = ['id', 'name', 'code', 'coco_object_group', 'status']
    list_display_links = ['id', 'name']
    list_filter = ['status', 'coco_object_group']
    search_fields = ['name', 'code']
    list_editable = ['status']
    list_select_related = ['coco_object_group']
    list_per_page = 25
    compressed_fields = True


@admin.register(RdpObject)
class RdpObjectAdmin(ModelAdmin):
    list_display = ['id', 'name', 'code', 'is_active']
    list_display_links = ['id', 'name']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    list_per_page = 25
    compressed_fields = True


@admin.register(HotKeyboardKey)
class HotKeyboardKeyAdmin(ModelAdmin):
    list_display = ['id', 'name', 'code', 'is_active']
    list_display_links = ['id', 'name']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    list_per_page = 25
    compressed_fields = True
