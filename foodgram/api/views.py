from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingСart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Subscription, User
from .pagination import LimitPagination
from .permissions import AdminOrReadOnly, IsAdminOrOwnerOrReadOnly
from .serializers import (CreateRecipeSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeSerializer,
                          SubscriptionCreateSerializer, SubscriptionSerializer,
                          TagSerializer)

FILENAME = 'shopping_cart.txt'


class RecipeViewSet(viewsets.ModelViewSet):
    """Отображение и создание рецептов."""
    queryset = Recipe.objects.all()
    pagination_class = LimitPagination

    def get_permissions(self):
        """Определение права доступа для запросов."""
        if self.action in (
            'create', 'favorite', 'shopping_card', 'download_shopping_card'
        ):
            self.permission_classes = (IsAuthenticated, )
        elif self.action in ('partial_update', 'destroy'):
            self.permission_classes = (IsAdminOrOwnerOrReadOnly, )
        elif self.action in ('list', 'retrieve'):
            self.permission_classes = (AllowAny, )
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        """Добавление в избранное/удаление из избранного"""
        return self.add_delete_recipe(
            model=Favorite,
            pk=pk,
            method=request.method,
        )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        """Добавление/удаление покупок в корзину/из корзины"""
        return self.add_delete_recipe(
            model=ShoppingСart,
            pk=pk,
            method=request.method,
        )

    def add_delete_recipe(self, model, pk, method):
        """Вспомогательная функция для добавления/удаления
        рецепта в избранное/в корзину."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = model.objects.filter(user=user, recipe=recipe)
        if method == "POST":
            if obj.exists():
                raise ValidationError('Рецепт уже был добавлен.')
            model.objects.create(user=user, recipe=recipe)
            return Response(
                {'Рецепт добавлен.'}, status=status.HTTP_201_CREATED
            )
        if method == "DELETE":
            if not obj.exists():
                raise ValidationError('Рецепт уже был удален/не был добавлен.')
            obj.delete()
            return Response(
                {'Рецепт удален.'}, status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        """Формирование списка покупок."""
        ingredients_to_buy = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user).values(
                    "ingredient__name",
                    "ingredient__measurement_unit",
                ).annotate(total_amount=Sum("amount"))
        )
        shopping_cart = []
        shopping_cart.append(f"Список покупок юзера {request.user.username}\n")
        for i in ingredients_to_buy:
            name = i["ingredient__name"]
            amount = i["total_amount"]
            measurement_unit = i["ingredient__measurement_unit"]
            shopping_cart.append(f"{name}, {amount} {measurement_unit}")
        shopping_list = "\n".join(shopping_cart)
        response = HttpResponse(
            shopping_list, content_type="text/plain,charset=utf8"
        )
        response['Content-Disposition'] = f'attachment; filename={FILENAME}'
        return response


class IngredientViewSet(viewsets.ModelViewSet):
    """Отображение ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)


class TagViewSet(viewsets.ModelViewSet):
    """"Отображение тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class CustomUserViewSet(UserViewSet):
    """"Отображение пользователей. Подписка и ее отмена."""
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    pagination_class = LimitPagination
    # LimitPagination.page_size = 6

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        """Создание/удаление подписки на пользователя."""
        data = {'subscriber': request.user.id, 'author': id}
        serializer = SubscriptionCreateSerializer(
            data=data, context={'request': request}
        )
        if request.method == "POST":
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                subscriber=request.user, author__id=id
            )
            if not subscription.exists():
                raise ValidationError('Вы не подписаны на этого пользователя.')
            subscription.delete()
            return Response(
                {'Вы отменили подписку на пользователя'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Просмотр подписок."""
        subscriptions = User.objects.filter(
            subscribers__subscriber=self.request.user
        )
        paginator = LimitPagination()
        result_page = paginator.paginate_queryset(subscriptions, request)
        serializer = SubscriptionSerializer(
            result_page, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)
