import csv

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from recipes.models import Ingredient

from foodgram.settings import IMPORT_DATA_ADRESS


class Command(BaseCommand):
    help = 'Импортирует базу данных для модели Ingredients из файла csv'

    def handle(self, *args, **options):

        with open(
            f'{IMPORT_DATA_ADRESS}/ingredients.csv',
            'r', encoding="utf-8-sig"
        ) as csv_file:
            dataReader = csv.DictReader(csv_file)

            for row in dataReader:

                try:
                    ingredient_name = row['name']

                    Ingredient.objects.create(
                        name=row['name'],
                        measurement_unit=row['measurement_unit']
                    )

                except IntegrityError as err:
                    self.stdout.write(
                        f'Ингредиент {ingredient_name} уже внесен в базу. '
                        f'Ошибка внесения - {err}'
                    )

                else:
                    self.stdout.write(
                        f'Ингредиент {ingredient_name} внесен в базу.'
                    )
