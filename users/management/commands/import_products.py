import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from users.models import Product


class Command(BaseCommand):
    help = "Импорт продуктов из CSV-файла"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            type=str,
            help="Путь к CSV-файлу с продуктами",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])

        if not csv_path.exists():
            raise CommandError(f"Файл не найден: {csv_path}")

        created_count = 0
        updated_count = 0

        with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, delimiter=";")

            required_columns = {
                "name",
                "calories",
                "proteins",
                "fats",
                "carbohydrates",
            }

            missing_columns = required_columns - set(reader.fieldnames or [])

            if missing_columns:
                raise CommandError(
                    f"В CSV отсутствуют колонки: {', '.join(missing_columns)}"
                )

            for row in reader:
                name = row["name"].strip()

                if not name:
                    continue

                product, created = Product.objects.update_or_create(
                    name=name,
                    defaults={
                        "calories": float(row["calories"].replace(",", ".")),
                        "proteins": float(row["proteins"].replace(",", ".")),
                        "fats": float(row["fats"].replace(",", ".")),
                        "carbs": float(row["carbohydrates"].replace(",", ".")),
                        "is_custom": False,
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Импорт завершён. Создано: {created_count}, обновлено: {updated_count}"
            )
        )