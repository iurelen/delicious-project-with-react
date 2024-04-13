from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название', max_length=200, unique=True, blank=False, null=False
    )
    color = models.CharField(
        'Цвет', max_length=7, blank=False, null=True
    )
    # #ffff00 #00ff00
    slug = models.SlugField(
        'Слаг', max_length=200, unique=True, blank=False, null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'теги'
        default_related_name = 'tag'


class Ingredient(models.Model):
    name = models.CharField(
        'Название', max_length=24, unique=True, blank=False, null=False
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=16, blank=False, null=False
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'ингредиенты'
        default_related_name = 'ingredient'


class Recipe(models.Model):
    name = models.CharField(
        'Название', max_length=200, unique=True, blank=False, null=False
    )
    author = models.ForeignKey(
        User, related_name='pecipes', on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to='recipes/images/', blank=False, null=False,
        verbose_name='Изображение'
    )
    text = models.TextField(
        'Описание', blank=False, null=False
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления в минутах', blank=False, null=False
    )
    tags = models.ManyToManyField(
        Tag, through='RecipeTag', verbose_name='тег', blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', verbose_name='ингредиент',
        blank=False
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепты'
        default_related_name = 'recipe'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_ingredient')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.FloatField('Количество', blank=False, null=False)

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipe_follower', verbose_name='Пользователь')
    favorite_recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorite_recipe', verbose_name='Избранный рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'favorite_recipe'],
                name='unique_pair_user_recipe'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_cart', verbose_name='Пользователь')
    recipe_in_cart = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_in_cart', verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe_in_cart'],
                name='unique_pair_user_recipe_in_cart'
            )
        ]
