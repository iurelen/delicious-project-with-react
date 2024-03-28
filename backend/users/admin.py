from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username',
                    'email',
                    'first_name',
                    'last_name',
                    'is_staff',)
    list_editable = ('is_staff',)
    search_fields = ('username',)
    list_filter = ('is_staff',)
    list_display_links = ('username',)

    # @admin.display(description='Добавлено рецептов')
    # def amount_review(self, obj):
    #    return obj.reviews.count()


admin.site.unregister(Group)
admin.site.empty_value_display = 'Не задано'
