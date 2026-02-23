from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminPasswordInputWidget, UnfoldAdminTextInputWidget

from apps.users.models import Role, User


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = UnfoldAdminTextInputWidget()
        self.fields['password1'].widget = UnfoldAdminPasswordInputWidget()
        self.fields['password2'].widget = UnfoldAdminPasswordInputWidget()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ['id', 'name', 'code']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'code']
    list_per_page = 25
    compressed_fields = True


@admin.register(User)
class UserAdmin(ModelAdmin, DjangoUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    compressed_fields = True
    warn_unsaved_form = True

    list_display = ['id', 'username', 'first_name', 'last_name', 'role', 'region',
                    'is_active', 'is_staff', 'is_superuser']
    list_display_links = ['id', 'username']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'role', 'region']
    search_fields = ['username', 'first_name', 'last_name', 'telegram_id']
    list_per_page = 25
    ordering = ('-id',)

    fieldsets = (
        ('Kirish ma\'lumotlari', {
            'fields': ('username', 'password'),
            'classes': ('tab',),
        }),
        ('Shaxsiy ma\'lumot', {
            'fields': ('first_name', 'last_name', 'middle_name', 'telegram_id', 'region', 'role'),
            'classes': ('tab',),
        }),
        ('Ruxsatlar', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'classes': ('tab',),
        }),
        ('Yuz ma\'lumoti', {
            'fields': ('image_base64', 'embedding'),
            'classes': ('tab',),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
