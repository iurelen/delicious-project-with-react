from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe

from .models import Follow

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
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')
    recipes = serializers.SerializerMethodField('get_recipes')
    recipes_count = serializers.SerializerMethodField('get_recipes_count')

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

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.following)
        request = self.context.get('request')
        value = request.GET.get('recipes_limit')
        if value:
            queryset = queryset[:int(value)]
        serializer = UserRecipeSerializer(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.following).count()


class TokenObtainSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password')
