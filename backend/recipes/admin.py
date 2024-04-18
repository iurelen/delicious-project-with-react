from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 0
    min_num = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj=None, **kwargs)
        formset.validate_min = True
        return formset


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj=None, **kwargs)
        formset.validate_min = True
        return formset


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'color',)
    list_display_links = ('slug',)
    list_editable = ('name', 'color',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):

    list_display = ('recipe', 'tag',)
    list_filter = ('recipe',)
    ordering = ('recipe',)
    search_fields = ('recipe',)
    list_display_links = ('recipe',)
    list_editable = ('tag',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):

    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe',)
    ordering = ('recipe',)
    search_fields = ('recipe',)
    list_display_links = ('recipe',)
    list_editable = ('ingredient', 'amount',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        RecipeTagInline,
        RecipeIngredientInline
    ]
    list_display = ('name', 'author', 'tags_name',
                    'ingredients_name', 'favorite_count')
    search_fields = ('username',)
    list_filter = ('name', 'author', 'tags')
    filter_horizontal = ('tags',)
    list_display_links = ('name',)

    @admin.display(
        description='Число добавлений рецепта в избранное'
    )
    def favorite_count(self, obj):
        return obj.favorite_recipe.count()

    @admin.display(
        description='Теги'
    )
    def tags_name(self, obj):
        return '\n'.join([tag.name for tag in obj.tags.all()])

    @admin.display(
        description='Ингредиенты'
    )
    def ingredients_name(self, obj):
        return '\n'.join(
            [(str(ingredient.name)) + ', ' + str(ingredient.measurement_unit)
             for ingredient in obj.ingredients.all()]
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipe',)
    list_filter = ('user',)
    ordering = ('user',)
    search_fields = ('recipe', 'user')
    list_display_links = ('user',)
    list_editable = ('recipe',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipe',)
    list_filter = ('user',)
    ordering = ('user',)
    search_fields = ('recipe', 'user')
    list_display_links = ('user',)
    list_editable = ('recipe',)


admin.site.empty_value_display = 'Не задано'
