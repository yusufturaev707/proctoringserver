from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.regions.models import Region, Zone


@admin.register(Region)
class RegionAdmin(ModelAdmin):
    list_display = ['id', 'name', 'dtm_id', 'status']
    list_display_links = ['id', 'name']
    list_filter = ['status']
    search_fields = ['name', 'dtm_id']
    list_editable = ['status']
    list_per_page = 25
    ordering = ('id',)
    compressed_fields = True
    warn_unsaved_form = True


@admin.register(Zone)
class ZoneAdmin(ModelAdmin):
    list_display = ['id', 'region', 'name', 'number', 'status']
    list_display_links = ['id', 'name']
    list_filter = ['status', 'region']
    search_fields = ['name', 'region__name']
    list_editable = ['status']
    list_select_related = ['region']
    list_per_page = 25
    ordering = ('id',)
    compressed_fields = True
    warn_unsaved_form = True
