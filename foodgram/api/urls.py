from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
    SubscriptionViewSet
)

router = routers.DefaultRouter()

router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'users', UserViewSet)
router.register(r'users/subscriptions', SubscriptionViewSet, basename='subscriptions')
router.register(r'users/(?P<user_id>\d+)/subscribe', SubscriptionViewSet, basename='subscribe')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
