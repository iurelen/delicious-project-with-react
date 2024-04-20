from django.contrib.auth import get_user_model

import django_filters

from recipes.models import Ingredient, Recipe

User = get_user_model()


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr='icontains'
    )
    is_favorited = django_filters.NumberFilter(
        method='filter'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset
        if name == 'is_in_shopping_cart' and value == 1:
            return queryset.filter(
                recipe_in_cart__user=self.request.user
            )
        elif name == 'is_favorited' and value == 1:
            return queryset.filter(
                favorite_recipe__user=self.request.user
            )
        else:
            return queryset
