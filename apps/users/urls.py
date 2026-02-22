from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import (PersonFaceViewSet, StaffLoginView, LogoutView, GetAccessTokenView, )

router = DefaultRouter()
router.register(r'users', PersonFaceViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('client/auth/login/', StaffLoginView.as_view()),
    path('client/auth/refresh/', GetAccessTokenView.as_view()),
    path('client/auth/logout/', LogoutView.as_view()),
]
