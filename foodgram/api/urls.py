from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    CustomUserViewSet
)

router = routers.DefaultRouter()

router.register(r'ingredients', IngredientViewSet, basename="ingredients")
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet, basename="recipes")
router.register(r'users', CustomUserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
