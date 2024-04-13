from django.contrib import admin

from .models import Ingredient, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_display_links = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count')
    search_fields = ('username',)
    list_filter = ('name', 'author', 'tags')
    filter_horizontal = ('tags',)
    list_display_links = ('name',)

    @admin.display(
        description='Общее число добавлений этого рецепта в избранное'
    )
    def favorite_count(self, obj):
        return obj.favorite_recipe.count()


admin.site.empty_value_display = 'Не задано'
