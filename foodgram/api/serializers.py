from rest_framework import serializers

from recipies.models import Ingridient, Tag, Recipe, RecipeIngridient


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = (
            'name',
            'measurement_unit',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'name',
            'colour',
            'slug'
            )

class RecipeIngridientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingridient.name')
    measurement_unit = serializers.CharField(
        source='ingridient.measurement_unit'
    )
    amount = serializers.CharField()
    
    class Meta:
        model = RecipeIngridient
        fields = (
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingridiens = RecipeIngridientSerializer(
        source='recipeingridient_set',
        many=True,
        read_only=True
        )

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    
    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'ingridients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
