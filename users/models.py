from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ("male", "Мужской"),
        ("female", "Женский"),
    ]

    GOAL_CHOICES = [
        ("lose", "Похудение"),
        ("maintain", "Поддержание веса"),
        ("gain", "Набор массы"),
    ]

    PROFILE_STATUS_CHOICES = [
        ("active", "Активный"),
        ("in_progress", "Заполняется"),
        ("paused", "Приостановлен"),
        ("needs_update", "Требует обновления данных"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(verbose_name="Возраст")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Пол")
    height = models.PositiveIntegerField(verbose_name="Рост")
    current_weight = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Текущий вес")
    target_weight = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Целевой вес")
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, verbose_name="Цель")

    profile_status = models.CharField(
        max_length=20,
        choices=PROFILE_STATUS_CHOICES,
        default="active",
        verbose_name="Статус профиля",
    )

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название продукта")
    calories = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Калории на 100 г",
    )
    proteins = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Белки на 100 г",
    )
    fats = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Жиры на 100 г",
    )
    carbs = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Углеводы на 100 г",
    )
    is_custom = models.BooleanField(
        default=False,
        verbose_name="Пользовательский продукт",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["name"]

    def __str__(self):
        return self.name

class MealEntry(models.Model):
    MEAL_TYPE_CHOICES = [
        ("breakfast", "Завтрак"),
        ("lunch", "Обед"),
        ("dinner", "Ужин"),
        ("snack", "Перекус"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="meal_entries",
        verbose_name="Пользователь",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="meal_entries",
        verbose_name="Продукт",
    )
    meal_type = models.CharField(
        max_length=20,
        choices=MEAL_TYPE_CHOICES,
        verbose_name="Тип приёма пищи",
    )
    amount_grams = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Количество, г",
    )
    date = models.DateField(verbose_name="Дата")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Запись рациона"
        verbose_name_plural = "Записи рациона"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.user.username} — {self.product.name} ({self.meal_type})"

class WeightHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="weight_entries",
        verbose_name="Пользователь",
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Вес, кг",
    )
    date = models.DateField(verbose_name="Дата")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "История веса"
        verbose_name_plural = "История веса"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.user.username} — {self.weight} кг ({self.date})"

class WaterEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="water_entries",
        verbose_name="Пользователь",
    )
    date = models.DateField(verbose_name="Дата")
    amount_ml = models.PositiveIntegerField(verbose_name="Количество воды, мл")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Запись воды"
        verbose_name_plural = "Записи воды"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.user.username} — {self.amount_ml} мл ({self.date})"