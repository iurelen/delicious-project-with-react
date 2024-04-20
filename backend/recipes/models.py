from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from colorfield.fields import ColorField

from foodgram_backend.constants import LOWER_LIMIT, MEDIUM_FIELD

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название', max_length=MEDIUM_FIELD, unique=True,
        blank=False, null=False
    )
    color = ColorField(format="hexa")
    slug = models.SlugField(
        'Слаг', max_length=MEDIUM_FIELD, unique=True, blank=False, null=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tag'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название', max_length=MEDIUM_FIELD, blank=False, null=False
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=MEDIUM_FIELD, blank=False, null=False
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = 'ingredient'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        'Название', max_length=MEDIUM_FIELD, unique=True,
        blank=False, null=False
    )
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to='recipes/images/', blank=False, null=False,
        verbose_name='Изображение'
    )
    text = models.TextField(
        'Описание', blank=False, null=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах', blank=False, null=False,
        validators=[
            MaxValueValidator(MEDIUM_FIELD),
            MinValueValidator(LOWER_LIMIT)
        ]
    )
    tags = models.ManyToManyField(
        Tag, through='RecipeTag',
        related_name='tag_recipe', verbose_name='тег'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        related_name='ingredient_recipe', verbose_name='ингредиент'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipe'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_recipetag',
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.SET_NULL, null=True,
        related_name='tag_recipetag',
        verbose_name='Тег'
    )

    class Meta:
        verbose_name = 'тег в рецепте'
        verbose_name_plural = 'Теги в рецептах'

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_recipeingredient',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredient_recipeingredient',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество', blank=False, null=False,
        validators=[
            MaxValueValidator(MEDIUM_FIELD),
            MinValueValidator(LOWER_LIMIT)
        ]
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipe_follower', verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorite_recipe', verbose_name='Избранный рецепт')

    class Meta:
        verbose_name = 'объект избранного'
        verbose_name_plural = 'Объекты избранного'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_pair_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_cart', verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_in_cart', verbose_name='Рецепт')

    class Meta:
        verbose_name = 'объект корзины'
        verbose_name_plural = 'Объекты корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_pair_user_recipe_in_cart'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'
