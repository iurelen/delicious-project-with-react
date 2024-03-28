from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField('Почта', unique=True, max_length=150,
                              blank=False, null=False)
    first_name = models.TextField('Имя', max_length=150,
                                  blank=False, null=False)
    last_name = models.TextField('Фамилия', max_length=150,
                                 blank=False, null=False)

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
