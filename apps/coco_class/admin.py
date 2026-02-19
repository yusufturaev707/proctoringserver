from django.contrib import admin
from apps.coco_class.models import (ModelVersion, CocoObjectGroup, CocoObject, RdpObject, HotKeyboardKey, )

@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'status']
    list_display_links = ['id', 'name']


@admin.register(CocoObjectGroup)
class CocoObjectGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'status']
    list_display_links = ['id', 'name']


@admin.register(CocoObject)
class CocoObjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'status']
    list_display_links = ['id', 'name']


@admin.register(RdpObject)
class RdpObjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'is_active']
    list_display_links = ['id', 'name']


@admin.register(HotKeyboardKey)
class HotKeyboardKeyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'is_active']
    list_display_links = ['id', 'name']
