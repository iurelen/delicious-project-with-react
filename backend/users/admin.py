from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import CustomUser, Follow


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username',
                    'email',
                    'first_name',
                    'last_name',
                    'follower_count',
                    'recipes_count',
                    'is_staff',)
    list_editable = ('is_staff',)
    search_fields = ('username',)
    list_filter = ('username',
                   'email',)
    list_display_links = ('username',)

    @admin.display(description='Количество подписчиков')
    def follower_count(self, obj):
        return obj.following.count()

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):

    list_display = ('user', 'following')
    list_filter = ('user',)
    ordering = ('user',)
    list_display_links = ('user',)
    list_editable = ('following',)


admin.site.unregister(Group)
admin.site.empty_value_display = 'Не задано'
