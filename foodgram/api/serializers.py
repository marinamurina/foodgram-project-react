import base64
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import ValidationError, UniqueTogetherValidator
from django.shortcuts import get_object_or_404
from django.db import transaction

from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, Tag, ShoppingСart
from users.models import Subscription, User


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для кодирования изображений в base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

    def to_representation(self, value):
        return value.url


class CustomUserSerializer(UserSerializer):
    """Cериализатор для работы с пользователями."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        is_subscribed = (
            user.is_authenticated and Subscription.objects.filter(
                subscriber=user, author=obj).exists()
        )
        return is_subscribed


class IngredientSerializer(serializers.ModelSerializer):
    """Cериализатор для работы с ингредиентами."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Cериализатор для работы с тегами."""
    class Meta:
        model = Tag
        fields = ('name', 'colour', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Cериализатор для связи рецептов с их ингридиентами."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.CharField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientShortSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов при создании рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""
    author = CustomUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientShortSerializer(many=True)
    image = Base64ImageField(use_url=True, max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=['author', 'name'],
                message='Вы уже публиковали рецепт с таким названием!'
            )
        ]

    def validate(self, data):
        """Валидиация ингредиентов и тегов."""
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        if not ingredients:
            raise ValidationError(
                'Нельзя создать рецепт без ингредиентов!'
            )
        recipe_ingredients = [i['ingredient'] for i in data['ingredients']]
        if len(recipe_ingredients) > len(set(recipe_ingredients)):
            raise ValidationError(
                'Ингредиенты в рецепте не должны повторяться!'
            )
        if not tags:
            raise ValidationError(
                'Нельзя создать рецепт без тегов!'
            )
        if len(data['tags']) > len(set(data['tags'])):
            raise ValidationError(
                'Теги в рецепте не должны повторяться!'
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.recipe_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        recipe.tags.set(tags)
        self.recipe_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def recipe_ingredients(self, recipe, ingredients):
        recipe_ingredients = [RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeSerializer(instance, context=context).data


class RecipeSerializer(serializers.ModelSerializer):
    """Cериализатор для отображения рецепта."""
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
        read_only=True
        )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(use_url=True, max_length=None)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta(CreateRecipeSerializer.Meta):
        fields = CreateRecipeSerializer.Meta.fields + (
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        is_favorited = (
            user.is_authenticated and Favorite.objects.filter(
                user=user, recipe=obj).exists()
        )
        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        is_favorited = (
            user.is_authenticated and ShoppingСart.objects.filter(
                user=user, recipe=obj).exists()
        )
        return is_favorited


class SubscriptionShortSerializer(serializers.ModelSerializer):
    """Сериализатор отображения рецептов в подписке."""
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор отображения подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        return SubscriptionShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        return recipes.count()

    def get_is_subscribed(self, obj):
        return CustomUserSerializer.get_is_subscribed(self, obj)


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания/удаления подписки на пользователя."""

    subscriber = serializers.IntegerField(source="subscriber.id")
    author = serializers.IntegerField(source="author.id")

    class Meta:
        model = Subscription
        fields = ["subscriber", "author"]

    def validate(self, data):
        subscriber = data["subscriber"]["id"]
        author = data["author"]["id"]
        if Subscription.objects.filter(
            subscriber=subscriber,
            author=author
        ).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя.')
        if subscriber == author:
            raise ValidationError('Нельзя подписаться на самого себя.')
        return data

    def create(self, validated_data):
        author = get_object_or_404(
            User, pk=validated_data["author"]["id"]
        )
        subscriber = get_object_or_404(
            User, pk=validated_data["subscriber"]["id"]
        )
        subscription = Subscription.objects.create(
            author=author, subscriber=subscriber
        )
        return subscription


class FavoriteSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe'
        )

    validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['recipe', 'user'],
                message='Вы уже добавили этот рецепт в Избранное!'
            )
        ]
