from django.contrib import admin

from apps.regions.models import Region, Zone


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display =['id', 'name', 'dtm_id', 'status']


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display =['id', 'region', 'name', 'number', 'status']