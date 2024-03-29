from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

User = get_user_model()


class ValidateUserNameMixin:

    def validate_username(self, value):
        if value == 'me' or value == 'set_password':
            raise serializers.ValidationError(
                'Некорректное имя пользователя.')
        return value


class UserSerializer(ValidateUserNameMixin,
                     serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=8, max_length=150, write_only=True, required=True,
        style={'input_type': 'password'},
        help_text='Обязательное поле. От 8 до 150 символов.'
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'password',
                  # 'is_subscribed'
                  )
        read_only_fields = ('is_staff', 'is_superuser', 'is_active')
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


class MeUserSerializer(ValidateUserNameMixin,
                       serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'password')
        read_only_fields = ('is_staff', 'is_superuser', 'is_active')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class SetPasswordSerializer(ValidateUserNameMixin,
                            serializers.ModelSerializer):
    new_password = serializers.CharField(
        min_length=8, max_length=150, required=True,
        style={'input_type': 'password'},
        help_text='Обязательное поле. От 8 до 150 символов.'
    )
    current_password = serializers.CharField(
        # min_length=8,
        max_length=150, required=True,
        style={'input_type': 'password'},
        help_text='Обязательное поле. От 8 до 150 символов.'
    )

    class Meta:
        model = User
        fields = ('new_password', 'current_password',)


class TokenObtainSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password')
