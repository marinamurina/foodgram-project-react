from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingСart, Tag)


class IngredientInlineAdmin(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'colour', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    list_filter = ('tags', 'author', 'ingredients',)
    search_fields = ('name',)
    inlines = (IngredientInlineAdmin,)

    def favorites_count(self, obj):
        return obj.favorites.count()

    favorites_count.short_description = "Число добавлений в Избранное"


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingСart)
