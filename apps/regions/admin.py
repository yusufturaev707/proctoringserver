from django.contrib import admin

from apps.regions.models import Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display =['name', 'dtm_id']