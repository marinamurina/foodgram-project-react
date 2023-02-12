from rest_framework import viewsets, status, mixins
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import action, api_view, permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from djoser.views import UserViewSet
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import Ingredient, Tag, Recipe, Favorite, ShoppingСart
from .permissions import IsAdminOrOwnerOrReadOnly, AdminOrReadOnly
from users.models import User, Subscription
from .pagination import LimitPagination
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    CreateRecipeSerializer,
    TagSerializer,
    CustomUserSerializer,
    SubscriptionSerializer,
    FavoriteSerializer,
    SubscriptionCreateSerializer,
    SubscriptionShortSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    """Отображение и создание рецептов."""
    queryset = Recipe.objects.all()

    # def get_permissions(self):
    #    """Определение права доступа для запросов."""
    #    if self.action in ('create', 'favorite'):
    #        self.permission_classes = (IsAuthenticated, )
    #    elif self.action in ('partial_update', 'destroy'):
    #        self.permission_classes = (IsAdminOrOwnerOrReadOnly, )
    #    elif self.action in ('list', 'retrieve'):
    #        self.permission_classes = (AllowAny, )
    #    return super().get_permissions()
    #  'shopping_card', 'download_shopping_card'

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer
        return RecipeSerializer

        # if self.request.method == 'DELETE':
        #     if object.exists():
        #         object.delete()
        #         return Response(status=status.HTTP_204_NO_CONTENT)
        #    return Response({'error': 'Этого рецепта нет в списке'},
        #                    status=status.HTTP_400_BAD_REQUEST)

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
        """Общая функция для добавления/удаления
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


class IngredientViewSet(viewsets.ModelViewSet):
    """"Отображение ингредиента, списка ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)


class TagViewSet(viewsets.ModelViewSet):
    """"Отображение тега, списка тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class CustomUserViewSet(UserViewSet):
    """"Отображение пользователей. Подписка и ее отмена."""
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    LimitPagination.page_size = 6

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
