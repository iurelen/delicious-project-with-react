from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow

from .fields import Base64ImageField

User = get_user_model()


class ValidateUsernameMixin:

    def validate_username(self, value):
        if (
            value == 'me'
            or value == 'set_password'
            or value == 'subscriptions'
        ):
            raise serializers.ValidationError(
                'Некорректное имя пользователя.')
        return value


class UserPostSerializer(serializers.ModelSerializer,
                         ValidateUsernameMixin):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email',)
            )
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)


class UserGetSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
        read_only=True,
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request')
        if user and user.user.is_authenticated:
            return user.user.follower.filter(following=obj).exists()
        return False


class SetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(
        min_length=8, max_length=150, required=True,
        style={'input_type': 'password'},
        help_text='Обязательное поле. От 8 до 150 символов.'
    )
    current_password = serializers.CharField(
        min_length=8, max_length=150, required=True,
        style={'input_type': 'password'},
        help_text='Обязательное поле. От 8 до 150 символов.'
    )

    class Meta:
        model = User
        fields = ('new_password', 'current_password',)


class UserRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class SubscriptionsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='following.id')
    email = serializers.ReadOnlyField(source='following.email')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.ReadOnlyField(default=True)
    recipes = serializers.SerializerMethodField('get_recipes')
    recipes_count = serializers.ReadOnlyField(source='following.recipes.count')

    class Meta:
        model = Follow
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.following)
        request = self.context.get('request')
        value = request.GET.get('recipes_limit')
        if value:
            queryset = queryset[:int(value)]
        serializer = UserRecipeSerializer(queryset, many=True)
        return serializer.data


class TokenObtainSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password')


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
    author = AuthorSerializer(required=False, read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeGetIngredientSerializer(
        source='recipe_recipeingredient', many=True
    )
    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited', read_only=True,
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart', read_only=True,
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'image', 'name',
                  'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.recipe_follower.filter(
                recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.shopping_cart.filter(
                recipe=obj
            ).exists()
        return False


class IngredientPostFields(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(required=False, read_only=True)
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

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        ingredients.sort(key=lambda lst: lst['id'].name)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags, clear=False)
        self.set_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' not in validated_data:
            raise serializers.ValidationError(
                'Необходимо выбрать теги.'
            )
        if 'ingredients' not in validated_data:
            raise serializers.ValidationError(
                'Необходимо указать ингредиенты.'
            )
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)

        tags = validated_data.pop('tags')
        instance.tags.set(tags, clear=True)

        ingredients = validated_data.pop('ingredients')
        ingredients.sort(key=lambda lst: lst['id'].name)
        instance.ingredients.clear()
        self.set_ingredients(instance, ingredients)
        instance.save()
        return instance

    def set_ingredients(self, instance, lst):
        objs = [
            RecipeIngredient(
                recipe=instance,
                ingredient=item['id'],
                amount=item['amount']
            )
            for item in lst
        ]
        RecipeIngredient.objects.bulk_create(objs)

    def to_representation(self, value):
        serializer = RecipeGetSerializer(value)
        return serializer.data

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Укажите хотя бы один тег.'
            )
        unique_tags = {item for item in value}
        if len(unique_tags) < len(value):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Укажите хотя бы один ингредиент.'
            )
        unique_ingredients = {item['id'] for item in value}
        if len(unique_ingredients) < len(value):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        return value


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(
        source='recipe.cooking_time'
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(
        source='recipe.cooking_time'
    )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')
