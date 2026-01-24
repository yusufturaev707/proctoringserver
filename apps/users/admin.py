from django.contrib import admin

from apps.users.models import Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display =['username', 'first_name', 'last_name', 'middle_name', 'is_staff',
                    'is_superuser', 'is_active', 'telegram_id', 'region',
                    'role']
