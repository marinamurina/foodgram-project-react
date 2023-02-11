import base64
# from drf_base64.fields import Base64ImageField
# from drf_extra_fields.fields import Base64ImageField
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, ValidationError, UniqueTogetherValidator
from django.shortcuts import get_object_or_404


from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, Tag
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
        is_subscribed = (user.is_authenticated and
        Subscription.objects.filter(
            subscriber=user, author=obj).exists())
        return is_subscribed


class IngredientSerializer(serializers.ModelSerializer):
    """Cериализатор для работы с ингредиентами."""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class TagSerializer(serializers.ModelSerializer):
    """Cериализатор для работы с тегами."""
    class Meta:
        model = Tag
        fields = (
            'name',
            'colour',
            'slug'
            )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Cериализатор для связи ингредиентов с рецептом."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
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
    # is_in_shopping_card = serializers.SerializerMethodField()

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
            'cooking_time',
            'is_favorited'
        )
    
    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        is_favorited = (
            user.is_authenticated and Favorite.objects.filter(
            user=user, recipe=obj).exists()
        )
        return is_favorited
    
    def get_is_in_shopping_card(self, obj):
        pass


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Cериализатор для создания рецептов."""
    author = CustomUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset =Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(use_url=True, max_length=None)
    ingredients = RecipeIngredientSerializer(
        many=True,
    )
    
    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=['author', 'name'],
                message='Вы уже публиковали рецепт с таким названием!'
            )
        ] 
    def validate_ingredients(self, value):
        """Валидиация ингредиентов."""
        ingredients = value
        if not ingredients:
            raise ValidationError(
                "Нельзя опубликовать рецепт без ингредиентов!"
            )
        ingredients_list = [i["id"] for i in ingredients]
        if len(ingredients_list) > len(set(ingredients_list)):
            raise serializers.ValidationError(
                'Ингредиенты в рецепте не должны повторяться!'
            )
        amount = ingredients['amount']
        if int(amount) <= 0:
            raise serializers.ValidationError(
                f'{amount} - количество должно быть больше нуля!'
            )
        return ingredients
    
    def create(self, validated_data):
        # author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        obj = [
            RecipeIngredient(
                recipe=recipe, 
                ingredient=Ingredient.objects.get(id=i['id']),
                amount = i['amount']
            ) for i in ingredients
        ]
        RecipeIngredient.objects.bulk_create(obj)
        return recipe
    
    def update(self, instance, validated_data):
        instance.tags = validated_data.get('tags', instance.tags)
        instance.ingredients = validated_data.get('ingredients', instance.ingredients)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        return RecipeSerializer(instance).data


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = serializers.SlugRelatedField(
        read_only=True, default=serializers.CurrentUserDefault(),
        slug_field='id'
    )
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='id'
    )

    class Meta:
        model = Subscription
        fields = ('__all__')


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    subscriber = serializers.SlugRelatedField(
        read_only=True, default=serializers.CurrentUserDefault(),
        slug_field='id'
    )
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='id'
    )
    
    # serializers.PrimaryKeyRelatedField(
    #    write_only=True,
    #    queryset=User.objects.all(),
    #)
    
    # def get_author(self, obj):
    #    request_object = self.context['request']
    #    author_id = request_object.query_params.get('user_id')
    #    author = get_object_or_404(
    #        User, id=author_id)
    #    return author
    
    # serializers.SlugRelatedField(
    #    queryset=User.objects.all(),
    #    slug_field='id'
    # )
    # CustomUserSerializer(read_only=True)
    
    class Meta:
        model = Subscription
        fields = ('subscriber', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['author', 'subscriber'],
                message='Вы уже подписаны на этого юзера!'
            )
        ]

    def validate_subscriber(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return value


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
