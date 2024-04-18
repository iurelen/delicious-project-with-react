from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, LogoutView, RecipeViewSet, TagViewSet,
                    TokenObtainView, UserViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

token_urls = [
    path('login/', TokenObtainView.as_view(), name='token_obtain'),
    path('logout/', LogoutView.as_view(), name='token_logout'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', include(token_urls))
]
