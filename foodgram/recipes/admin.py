from django.contrib import admin

from .models import (
    Tag,
    Recipe,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingСart
)


class IngredientInlineAdmin(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'colour', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author')
    list_filter = ('tags', 'author', 'ingredients',)
    search_fields = ('name',)
    inlines = (IngredientInlineAdmin,)


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingСart)
