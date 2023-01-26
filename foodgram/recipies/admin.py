from django.contrib import admin

from .models import Tag, Recipe, Ingridient, RecipeIngridient

class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'colour', 'colour_example', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('tags', 'author', 'ingredients',)


class IngridientAdmin(admin.ModelAdmin):
    list_filter = ('name',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingridient, IngridientAdmin)
admin.site.register(RecipeIngridient)
