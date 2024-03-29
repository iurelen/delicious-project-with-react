from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        'Адрес электронной почты', unique=True, max_length=254,
        blank=False, null=False,
        help_text='Обязательное поле. Не более 254 символов.'
    )
    first_name = models.TextField(
        'Имя', max_length=150, blank=False, null=False,
        help_text='Обязательное поле. Не более 150 символов.'
    )
    last_name = models.TextField(
        'Фамилия', max_length=150, blank=False, null=False,
        help_text='Обязательное поле. Не более 150 символов.'
    )
    # is_subscribed = models.BooleanField(
    #    'Подписан ли текущий пользователь на этого',
    #    blank=False, null=False, default=False
    # )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email',),
                name='unique_pair_username_email'
            )
        ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'
        default_related_name = 'author'

    def __str__(self):
        return self.username
