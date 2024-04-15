import json
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Import data from JSON file"

    def handle(self, *args, **kwargs):
        file_path = 'data/ingredients.json'
        if not Path(file_path).is_file():
            print('Файл не найден.')
            return
        with open(file_path, encoding='utf-8') as fh:
            ingredients_data = json.load(fh)

        for data in ingredients_data:
            if not Ingredient.objects.filter(
                name=data.get('name'),
                measurement_unit=data.get('measurement_unit')
            ).exists():
                ingredient = Ingredient(
                    name=data.get('name'),
                    measurement_unit=data.get('measurement_unit')
                )
                ingredient.save()

            print('Данные успешно загружены.')
