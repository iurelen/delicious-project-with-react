from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import LogoutView, TokenObtainView, UserViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', TokenObtainView.as_view(), name='token_obtain'),
    path('auth/token/logout/', LogoutView.as_view(), name='token_logout'),
]

# flushexpiredtokens
