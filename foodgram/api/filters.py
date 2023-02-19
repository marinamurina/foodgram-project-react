from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """Фильтр для сортировки ингридентов."""

    name = filters.CharFilter(field_name="name", lookup_expr="istartswith",)

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilter(filters.FilterSet):
    """Фильтр для сортировки рецептов."""

    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr='exact',
    )

    is_favorited = filters.BooleanFilter(method='favorite')
    is_in_shopping_cart = filters.BooleanFilter(
        method='shopping_cart')

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")

    def favorite(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorites__user=user)
        return Recipe.objects.all()

    def shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(shopping_cart__user=user)
        return Recipe.objects.all()
