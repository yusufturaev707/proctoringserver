from django.contrib import admin
from apps.coco_class.models import ModelVersion, CocoObjectGroup, CocoObject

@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'status']


@admin.register(CocoObjectGroup)
class CocoObjectGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'status']


@admin.register(CocoObject)
class CocoObjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'status']
