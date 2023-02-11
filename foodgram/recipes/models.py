from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator 

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Имя ингредиента',
        )  
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единицы измерения'
    )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент' 
        verbose_name_plural = 'Ингредиенты'


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега'
    )  
    colour = models.CharField(
        max_length=7,
        unique=True,
        verbose_name="Цвет в HEX"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Тег' 
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    """Модель рецепта."""
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты рецепта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Фото блюда'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(600)
        ],
        verbose_name='Время приготовления, мин.'
    )

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        

class RecipeIngredient(models.Model):
    """Модель для связи между рецептом и его ингредиентами."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.ingredient} в рецепте "{self.recipe}"'
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name = 'recipe_ingredient',
            )
        ]
        verbose_name = 'Ингредиент в рецепте' 
        verbose_name_plural = 'Ингредиенты рецепта'


class Favorite(models.Model):
    """Модель избранного."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name = 'Рецепт'
        )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name = 'Пользователь'
    )
    
    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name = 'unique_favorite',
            )
        ]

        verbose_name = 'Избранный рецепт' 
        verbose_name_plural = 'Избранные рецепты'


class ShoppingСart(models.Model):
    """Модель корзины."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_card',
        verbose_name = 'Рецепт'
        )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_card',
        verbose_name = 'Пользователь'
    )
    
    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в список покупок.'
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name = 'unique_shopping_cart',
            )
        ]

        verbose_name = 'Покупка' 
        verbose_name_plural = 'Покупки'
