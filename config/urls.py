from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static

from apps.presence.views import presence_dashboard_view

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]


urlpatterns += [
    # Presence dashboard — admin panel ichida
    path('admin/presence/dashboard/', presence_dashboard_view, name='presence_dashboard'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/', include('apps.exams.urls')),
    path('api/v1/', include('apps.notification.urls')),
    path('api/v1/', include('apps.settings.urls')),
    path('barcode/', include('apps.barcode.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
