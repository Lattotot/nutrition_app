from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    MealEntry,
    Product,
    UserProfile,
    WeightHistory,
)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Введите email",
        }),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        labels = {
            "username": "Имя пользователя",
            "password1": "Пароль",
            "password2": "Подтверждение пароля",
        }
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Введите имя пользователя",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Введите пароль",
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Повторите пароль",
        })


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "age",
            "gender",
            "height",
            "current_weight",
            "target_weight",
            "goal",
            "profile_status",
        ]

        labels = {
            "age": "Возраст",
            "gender": "Пол",
            "height": "Рост, см",
            "current_weight": "Текущий вес, кг",
            "target_weight": "Целевой вес, кг",
            "goal": "Цель",
            "profile_status": "Статус профиля",
        }

        widgets = {
            "age": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "placeholder": "Введите возраст",
            }),
            "gender": forms.Select(attrs={
                "class": "form-select",
            }),
            "height": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "placeholder": "Рост в сантиметрах",
            }),
            "current_weight": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "1",
                "placeholder": "Текущий вес",
            }),
            "target_weight": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "1",
                "placeholder": "Целевой вес",
            }),
            "goal": forms.Select(attrs={
                "class": "form-select",
            }),
            "profile_status": forms.Select(attrs={
                "class": "form-select",
            }),
        }


class MealEntryForm(forms.ModelForm):
    class Meta:
        model = MealEntry
        fields = ["product", "meal_type", "amount_grams", "date"]

        labels = {
            "product": "Продукт",
            "meal_type": "Тип приёма пищи",
            "amount_grams": "Количество, г",
            "date": "Дата",
        }

        widgets = {
            "product": forms.Select(attrs={
                "class": "form-select",
            }),
            "meal_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "amount_grams": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "1",
                "placeholder": "Количество в граммах",
            }),
            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["product"].queryset = Product.objects.order_by("name")


class WeightHistoryForm(forms.ModelForm):
    class Meta:
        model = WeightHistory
        fields = ["weight", "date"]

        labels = {
            "weight": "Вес, кг",
            "date": "Дата",
        }

        widgets = {
            "weight": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "1",
                "placeholder": "Введите вес",
            }),
            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "calories", "proteins", "fats", "carbs"]

        labels = {
            "name": "Название продукта",
            "calories": "Калории на 100 г",
            "proteins": "Белки на 100 г",
            "fats": "Жиры на 100 г",
            "carbs": "Углеводы на 100 г",
        }

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Например: Йогурт клубничный",
            }),
            "calories": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "placeholder": "Ккал на 100 г",
            }),
            "proteins": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "placeholder": "Белки на 100 г",
            }),
            "fats": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "placeholder": "Жиры на 100 г",
            }),
            "carbs": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "placeholder": "Углеводы на 100 г",
            }),
        }