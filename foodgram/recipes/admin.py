from django.contrib import admin

from .models import Tag, Recipe, Ingridient, RecipeIngridient


class IngridientInlineAdmin(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'colour', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('tags', 'author', 'ingredients',)
    inlines = (IngridientInlineAdmin,)


class IngridientAdmin(admin.ModelAdmin):
    list_filter = ('name',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingridient, IngridientAdmin)
admin.site.register(RecipeIngridient)
