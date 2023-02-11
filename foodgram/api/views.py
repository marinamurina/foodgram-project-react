from rest_framework import viewsets, status, mixins
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import action, api_view, permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from djoser.views import UserViewSet
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, Tag, Recipe, Favorite
from .permissions import IsAdminOrOwnerOrReadOnly, AdminOrReadOnly
from users.models import User, Subscription
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    CreateRecipeSerializer,
    TagSerializer,
    CustomUserSerializer,
    SubscriptionSerializer,
    FavoriteSerializer,
    SubscriptionCreateSerializer
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
        if self.action == 'post':
            return CreateRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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
    
    def add_delete_recipe(self, model, pk, method):
        """Общая функция для добавления/удаления рецепта в избранное/в корзину."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = model.objects.filter(user=user, recipe=recipe)
        if method == "POST":
            if obj.exists():
                raise ValidationError('Рецепт уже был добавлен.')
            model.objects.create(user=user, recipe=recipe)
            return Response(
                {'Рецепт добавлен.'},status=status.HTTP_201_CREATED
            )
        if method == "DELETE":
            if not obj.exists():
                raise ValidationError('Рецепт уже был удален/не был добавлен.')
            obj.delete()
            return Response({'Рецепт удален.'}, status=status.HTTP_204_NO_CONTENT)
            
  
class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    # serializer_class = SubscriptionCreateSerializer 
  
    def get_serializer_class(self):
        if self.action in ('list','retrieve'):
            return SubscriptionSerializer
        return SubscriptionCreateSerializer
    
    def get_queryset(self):
        author = get_object_or_404(
            User, username=self.request.user.username
        )
        return author.subscribers.all()
    
    # def post(self, request, **kwargs):
    #     author = get_object_or_404(
    #         User, id=kwargs.get('user_id')
    #     )
    #   if hasattr(request.data, '_mutable'):
    #        request.data._mutable = True
    #    request.data.update(
    #        {'author':author.id, 'subscriber': self.request.user.id} 
    #    )
    #    return self.create(request)


    # @action(detail=True, methods=('POST', 'DELETE'))
    def create(self, request, **kwargs):
        context ={
            'subscriber': request.user, 
            'author': get_object_or_404(
            User, id=kwargs.get('user_id')),
            'request': request
        }
        data = {
            'subscriber': context['subscriber'].id,
            'author': context['author'].id
         }
        serializer = SubscriptionCreateSerializer(
            data=data, context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


    @action(detail=False,)
    def subscriptions(self, request):
        subscriber = request.user
        queryset = User.objects.filter(subscribers__subscriber=subscriber)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    # permission_classes = (IsAuthenticated, )    
    

class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    