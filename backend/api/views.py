import io

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404

import reportlab.rl_config
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow

from .filters import RecipeFilter
from .paginations import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          SetPasswordSerializer, ShoppingCartSerializer,
                          SubscriptionsSerializer, TagSerializer,
                          TokenObtainSerializer, UserGetSerializer,
                          UserPostSerializer)

reportlab.rl_config.warnOnMissingFontGlyphs = 0
reportlab.rl_config.TTFSearchPath.append(
    str(settings.BASE_DIR) + '/lib/reportlab/fonts'
)
pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8'))

User = get_user_model()


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by('-id')
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return UserGetSerializer
        return UserPostSerializer

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = self.request.user
        serializer = UserGetSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=SetPasswordSerializer()
    )
    def set_password(self, request):
        user = self.request.user
        serializer = SetPasswordSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        if user.check_password(serializer.validated_data['current_password']):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {
                    'errors': 'Ошибка пароля.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        pages = self.paginate_queryset(
            self.request.user.follower.order_by('-id')
        )
        serializer = SubscriptionsSerializer(
            pages, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(
            serializer.data
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        following = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            serializer = SubscriptionsSerializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            if following == request.user:
                return Response(
                    {
                        'errors': 'Нельзя подписаться на самого себя.',
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            if request.user.follower.filter(following_id=pk).exists():
                return Response(
                    {
                        'errors': 'Подписка уже создана.',
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save(user=request.user, following=following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            try:
                instance = Follow.objects.get(
                    user=self.request.user, following=following
                )
            except ObjectDoesNotExist:
                return Response(
                    {
                        'errors': 'Запись не найдена.',
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = SubscriptionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.follower.all()


class TokenObtainView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        if 'email' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if 'password' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, email=request.data['email'])
        serializer = TokenObtainSerializer(
            user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        if user.check_password(serializer.validated_data['password']):
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'auth_token': str(refresh.access_token)
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'detail': 'Учетные данные не были предоставлены.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = self.request.user
        try:
            token = RefreshToken.for_user(user)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exept:
            return Response(exept, status=status.HTTP_401_UNAUTHORIZED)


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.order_by('id')
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.order_by('id')
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.order_by('-id')
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    search_fields = ('^name',)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipePostSerializer

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
        ).annotate(sum_amount=Sum('amount'))

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

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.shopping_cart_or_favorite(
            request, pk, Favorite, FavoriteSerializer
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.shopping_cart_or_favorite(
            request, pk, ShoppingCart, ShoppingCartSerializer
        )

    def shopping_cart_or_favorite(self, request, pk, model, modelserializer):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
            except ObjectDoesNotExist:
                return Response(
                    {
                        'errors': 'Рецепт не найден.',
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = modelserializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if model.objects.filter(
                user=self.request.user, recipe=recipe
            ).exists():
                return Response(
                    {
                        'errors': 'Рецепт уже добавлен.',
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            try:
                instance = model.objects.get(
                    user=self.request.user, recipe=recipe
                )
            except ObjectDoesNotExist:
                return Response(
                    {
                        'errors': 'Запись не найдена.',
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
