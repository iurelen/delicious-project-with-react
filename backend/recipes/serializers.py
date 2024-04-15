import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from rest_framework import serializers

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',)


class RecipeGetIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(required=False)
    tags = TagSerializer(many=True)
    ingredients = RecipeGetIngredientSerializer(
        source='recipe_ingredient', many=True
    )
    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited',
        read_only=True,
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart',
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'image', 'name',
                  'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')
        read_only_fields = ('author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        user = self.context.get('request')
        if user and user.user.is_authenticated:
            return user.user.recipe_follower.filter(
                favorite_recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request')
        if user and user.user.is_authenticated:
            return user.user.shopping_cart.filter(
                recipe_in_cart=obj
            ).exists()
        return False


class IngredientPostFields(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество должно быть больше или равно 1.')
        return value


class RecipePostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(required=False)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True, required=True
    )
    ingredients = IngredientPostFields(many=True, required=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'image', 'name',
                  'text', 'cooking_time')
        read_only_fields = ('author',)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.get_or_create(
                tag=tag, recipe=recipe
            )
        for ingredient in ingredients:
            RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)

        if 'tags' not in validated_data:
            raise serializers.ValidationError(
                'Необходимо выбрать теги.'
            )

        tags = validated_data.pop('tags')
        instance.tags.clear()
        for tag in tags:
            RecipeTag.objects.get_or_create(
                tag=tag, recipe_id=instance.id
            )

        if 'ingredients' not in validated_data:
            raise serializers.ValidationError(
                'Необходимо указать ингредиенты.'
            )

        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        for ingredient in ingredients:
            RecipeIngredient.objects.get_or_create(
                recipe_id=instance.id,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

        instance.save()
        return instance

    def to_representation(self, value):
        serializer = RecipeGetSerializer(value)
        return serializer.data

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше или равно 1.'
            )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Укажите хотя бы один тег.'
            )
        lst = []
        for item in value:
            if item not in lst:
                lst.append(item)
            else:
                raise serializers.ValidationError(
                    'Теги не должны повторяться.'
                )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Укажите хотя бы один ингредиент.'
            )
        lst = []
        for item in value:
            if item['id'] not in lst:
                lst.append(item['id'])
            else:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
        return value


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='favorite_recipe.id')
    name = serializers.ReadOnlyField(source='favorite_recipe.name')
    image = Base64ImageField(source='favorite_recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(
        source='favorite_recipe.cooking_time'
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe_in_cart.id')
    name = serializers.ReadOnlyField(source='recipe_in_cart.name')
    image = Base64ImageField(source='recipe_in_cart.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(
        source='recipe_in_cart.cooking_time'
    )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')
