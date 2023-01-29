from django.contrib.auth import get_user_model
from django.db import models
from django.utils.html import format_html
from django.core.validators import MinValueValidator, MaxValueValidator 

User = get_user_model()

class Ingridient(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Имя ингридиента',
        )  
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единицы измерения'
    )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингридиент' 
        verbose_name_plural = 'Ингридиенты'


class Tag(models.Model):
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

    # def colour_example(self):
    #     return format_html(
    #         '<span style="color: #{};">{}</span>',
    #         self.colour,
    #     )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Тег' 
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
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
        Ingridient,
        through='RecipeIngridient',
        verbose_name='Ингридиенты'
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
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(600)
        ],
        verbose_name='Время приготовления'
    )

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngridient(models.Model):
    recipe = models.ForeignKey(
        Ingridient,
        on_delete=models.CASCADE
    )
    ingridient = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.recipe} в рецепте "{self.ingridient}"'
    

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingridient'],
                name = 'recipe_ingridient',
            )
        ]

        verbose_name = 'Ингридиент в рецепте' 
        verbose_name_plural = 'Ингридиенты рецепта'
