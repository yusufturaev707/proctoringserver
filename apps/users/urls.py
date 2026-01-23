from django.urls import path, include
from apps.users.views import PersonFaceViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', PersonFaceViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]