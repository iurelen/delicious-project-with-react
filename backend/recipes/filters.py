import django_filters

from recipes.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):

    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    author = django_filters.CharFilter(
        field_name='author__id',
    )
    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset
        if value == 1:
            return queryset.filter(
                favorite_recipe__user=self.request.user
            )
        else:
            return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset
        if value == 1:
            return queryset.filter(
                recipe_in_cart__user=self.request.user
            )
        else:
            return queryset
