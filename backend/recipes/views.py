import io

import reportlab.rl_config
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.paginations import CustomPagination

from .filters import RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          ShoppingCartSerializer, TagSerializer)

reportlab.rl_config.warnOnMissingFontGlyphs = 0
reportlab.rl_config.TTFSearchPath.append(
    str(settings.BASE_DIR) + '/lib/reportlab/fonts'
)
pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8'))

User = get_user_model()


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.order_by('id')
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.order_by('id')
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.order_by('-id')
    serializer_class = RecipePostSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = CustomPagination
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        queryset = RecipeIngredient.objects.filter(
            recipe__recipe_in_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(sum_amount=Sum('amount', distinct=True))

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont('DejaVuSerif', 16)
        y = 700
        p.drawString(100, y + 50, 'Список покупок')
        p.setFont('DejaVuSerif', 14)
        for qs in queryset:
            name = qs['ingredient__name']
            amount = qs['sum_amount']
            measurement_unit = qs['ingredient__measurement_unit']
            p.drawString(
                100, y,
                f'{name} - {amount} {measurement_unit}'
            )
            y -= 30
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True,
            filename='shopping_cart.pdf',
            status=status.HTTP_200_OK
        )


class FavoriteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer = FavoriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.recipe_follower.filter(
            favorite_recipe_id=recipe_id
        ).exists():
            return Response(
                {
                    'errors': 'Рецепт уже есть в избранном.',
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(user=request.user, favorite_recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        instance = get_object_or_404(Favorite, user=self.request.user,
                                     favorite_recipe=recipe)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, recipe_id):
        serializer = ShoppingCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if request.user.shopping_cart.filter(
             recipe_in_cart_id=recipe_id
        ).exists():
            return Response(
                {
                    'errors': 'Рецепт уже есть в корзине.',
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(user=request.user, recipe_in_cart=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        instance = get_object_or_404(ShoppingCart, user=self.request.user,
                                     recipe_in_cart=recipe)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
