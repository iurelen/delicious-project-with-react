from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import (FavoriteView, IngredientViewSet, RecipeViewSet,
                           ShoppingCartView, TagViewSet)
from users.views import FollowView, LogoutView, TokenObtainView, UserViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet)

token_urls = [
    path('login/', TokenObtainView.as_view(), name='token_obtain'),
    path('logout/', LogoutView.as_view(), name='token_logout'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', include(token_urls)),
    path('users/<int:user_id>/subscribe/',
         FollowView.as_view(), name='subscribe'),
    path('recipes/<int:recipe_id>/favorite/',
         FavoriteView.as_view(), name='favorite'),
    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppingCartView.as_view(), name='shopping_cart'),
]

# flushexpiredtokens
