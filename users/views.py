from datetime import timedelta

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import (
    MealEntryForm,
    ProductForm,
    RegisterForm,
    UserProfileForm,
    WeightHistoryForm,
)
from .models import (
    MealEntry,
    Product,
    UserProfile,
    WaterEntry,
    WeightHistory,
)


def get_or_create_user_profile(user):
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "age": 18,
            "gender": "male",
            "height": 170,
            "current_weight": 70,
            "target_weight": 70,
            "goal": "maintain",
            "profile_status": "in_progress",
        },
    )
    return profile


def calculate_target_calories(profile):
    weight = float(profile.current_weight)
    height = float(profile.height)
    age = int(profile.age)

    if profile.gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # Пока без коэффициента активности: базовая логика
    maintenance = bmr * 1.2

    if profile.goal == "lose":
        return round(maintenance - 300, 2)
    elif profile.goal == "gain":
        return round(maintenance + 300, 2)

    return round(maintenance, 2)


def calculate_target_macros(target_calories):
    # Базовое распределение:
    # белки 30%, жиры 30%, углеводы 40%
    target_proteins = round((target_calories * 0.30) / 4, 2)
    target_fats = round((target_calories * 0.30) / 9, 2)
    target_carbs = round((target_calories * 0.40) / 4, 2)

    return target_proteins, target_fats, target_carbs


def calculate_target_water(profile):
    # Базовая рекомендация: 30 мл на 1 кг веса
    return int(float(profile.current_weight) * 30)


def get_selected_date(request):
    selected_date_str = request.GET.get("date")

    if selected_date_str:
        try:
            selected_date = timezone.datetime.strptime(
                selected_date_str,
                "%Y-%m-%d",
            ).date()
        except ValueError:
            selected_date = timezone.localdate()
    else:
        selected_date = timezone.localdate()

    return selected_date


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "age": 18,
                    "gender": "male",
                    "height": 170,
                    "current_weight": 70,
                    "target_weight": 70,
                    "goal": "maintain",
                    "profile_status": "in_progress",
                },
            )

            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def profile_view(request):
    profile = get_or_create_user_profile(request.user)

    bmi = None
    bmi_category = "Недостаточно данных"
    bmi_status_class = "bg-soft-primary"

    target_bmi = None
    target_bmi_category = "Недостаточно данных"
    target_weight_warning = None

    if profile.height and profile.current_weight:
        height_m = float(profile.height) / 100
        current_weight = float(profile.current_weight)

        if height_m > 0:
            bmi = current_weight / (height_m ** 2)

            if bmi < 16:
                bmi_category = "Выраженный дефицит массы тела"
                bmi_status_class = "bg-soft-danger"
            elif bmi < 18.5:
                bmi_category = "Недостаточная масса тела"
                bmi_status_class = "bg-soft-warning"
            elif bmi < 25:
                bmi_category = "Норма"
                bmi_status_class = "bg-soft-success"
            elif bmi < 30:
                bmi_category = "Избыточная масса тела"
                bmi_status_class = "bg-soft-warning"
            elif bmi < 35:
                bmi_category = "Ожирение I степени"
                bmi_status_class = "bg-soft-danger"
            elif bmi < 40:
                bmi_category = "Ожирение II степени"
                bmi_status_class = "bg-soft-danger"
            else:
                bmi_category = "Ожирение III степени"
                bmi_status_class = "bg-soft-danger"

    if profile.height and profile.target_weight:
        height_m = float(profile.height) / 100
        target_weight = float(profile.target_weight)

        if height_m > 0:
            target_bmi = target_weight / (height_m ** 2)

            if target_bmi < 16:
                target_bmi_category = "Критически низкий целевой вес"
                target_weight_warning = (
                    "Целевой вес выглядит слишком низким для указанного роста. "
                    "Рекомендуется проверить введённые данные."
                )
            elif target_bmi < 18.5:
                target_bmi_category = "Низкий целевой вес"
                target_weight_warning = (
                    "Целевой вес находится ниже рекомендуемого диапазона. "
                    "Рекомендуется внимательно оценить цель."
                )
            elif target_bmi < 25:
                target_bmi_category = "Целевой вес в пределах нормы"
            elif target_bmi < 30:
                target_bmi_category = "Целевой вес в зоне избыточной массы"
            else:
                target_bmi_category = "Целевой вес остаётся в зоне ожирения"

    return render(
        request,
        "users/profile.html",
        {
            "profile": profile,
            "bmi": bmi,
            "bmi_category": bmi_category,
            "bmi_status_class": bmi_status_class,
            "target_bmi": target_bmi,
            "target_bmi_category": target_bmi_category,
            "target_weight_warning": target_weight_warning,
        },
    )


@login_required
def edit_profile_view(request):
    profile = get_or_create_user_profile(request.user)
    old_weight = profile.current_weight

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)

        if form.is_valid():
            updated_profile = form.save()

            if old_weight != updated_profile.current_weight:
                WeightHistory.objects.create(
                    user=request.user,
                    weight=updated_profile.current_weight,
                    date=timezone.localdate(),
                )

            return redirect("profile")
    else:
        form = UserProfileForm(instance=profile)

    return render(
        request,
        "users/edit_profile.html",
        {
            "form": form,
            "profile": profile,
        },
    )


@login_required
def meal_list_view(request):
    profile = get_or_create_user_profile(request.user)

    selected_date = get_selected_date(request)
    selected_date_str = selected_date.strftime("%Y-%m-%d")

    previous_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)

    previous_date_str = previous_date.strftime("%Y-%m-%d")
    next_date_str = next_date.strftime("%Y-%m-%d")

    meal_entries = MealEntry.objects.filter(
        user=request.user,
        date=selected_date,
    ).select_related("product")

    breakfast_entries = meal_entries.filter(meal_type="breakfast")
    lunch_entries = meal_entries.filter(meal_type="lunch")
    dinner_entries = meal_entries.filter(meal_type="dinner")
    snack_entries = meal_entries.filter(meal_type="snack")

    total_calories = 0
    total_proteins = 0
    total_fats = 0
    total_carbs = 0

    for entry in meal_entries:
        amount_factor = float(entry.amount_grams) / 100

        total_calories += float(entry.product.calories) * amount_factor
        total_proteins += float(entry.product.proteins) * amount_factor
        total_fats += float(entry.product.fats) * amount_factor
        total_carbs += float(entry.product.carbs) * amount_factor

    target_calories = calculate_target_calories(profile)
    target_proteins, target_fats, target_carbs = calculate_target_macros(target_calories)

    remaining_proteins = max(target_proteins - total_proteins, 0)
    remaining_fats = max(target_fats - total_fats, 0)
    remaining_carbs = max(target_carbs - total_carbs, 0)

    calories_percent = 0
    proteins_percent = 0
    fats_percent = 0
    carbs_percent = 0

    if target_calories > 0:
        calories_percent = round((total_calories / target_calories) * 100)

    if target_proteins > 0:
        proteins_percent = round((total_proteins / target_proteins) * 100)

    if target_fats > 0:
        fats_percent = round((total_fats / target_fats) * 100)

    if target_carbs > 0:
        carbs_percent = round((total_carbs / target_carbs) * 100)

    calories_percent = min(calories_percent, 100)
    proteins_percent = min(proteins_percent, 100)
    fats_percent = min(fats_percent, 100)
    carbs_percent = min(carbs_percent, 100)

    recommendations = []

    if total_calories < target_calories * 0.8:
        recommendations.append(
            "Калорийность рациона ниже рекомендуемой нормы. Можно увеличить общий объём пищи или добавить более питательные продукты."
        )
    elif total_calories > target_calories * 1.1:
        recommendations.append(
            "Калорийность рациона выше рекомендуемой нормы. Рекомендуется пересмотреть объём порций."
        )
    else:
        recommendations.append(
            "Калорийность рациона находится близко к рекомендуемому уровню."
        )

    if total_proteins < target_proteins:
        recommendations.append(
            "В рационе недостаточно белка. Рекомендуется добавить белковые продукты: курицу, яйца, творог, рыбу или бобовые."
        )
    else:
        recommendations.append(
            "Количество белка соответствует рекомендуемому уровню."
        )

    if total_fats > target_fats:
        recommendations.append(
            "Количество жиров превышает рекомендуемый уровень. Стоит сократить жирные продукты или масла."
        )
    else:
        recommendations.append(
            "Количество жиров не превышает рекомендуемый уровень."
        )

    if profile.goal == "lose":
        recommendations.append(
            "Так как выбрана цель похудения, рекомендуется соблюдать умеренный дефицит калорий и поддерживать высокий уровень белка в рационе."
        )
    elif profile.goal == "gain":
        recommendations.append(
            "Так как выбрана цель набора массы, рекомендуется поддерживать умеренный профицит калорий и достаточное количество белка."
        )
    else:
        recommendations.append(
            "Так как выбрана цель поддержания веса, рекомендуется удерживать рацион близко к дневной норме."
        )

    water_entries = WaterEntry.objects.filter(
        user=request.user,
        date=selected_date,
    ).order_by("created_at")

    total_water = sum(entry.amount_ml for entry in water_entries)
    target_water = calculate_target_water(profile)
    remaining_water = max(target_water - total_water, 0)
    water_count = water_entries.count()

    average_glass = 0
    if water_count > 0:
        average_glass = round(total_water / water_count)

    water_percent = 0
    if target_water > 0:
        water_percent = round((total_water / target_water) * 100)

    if water_percent > 100:
        water_percent = 100

    if water_percent >= 100:
        water_status = "Цель по воде выполнена"
    else:
        water_status = "Норма не достигнута"

    return render(
        request,
        "users/meal_list.html",
        {
            "profile": profile,
            "today": selected_date.strftime("%B %d, %Y"),
            "selected_date": selected_date,
            "selected_date_str": selected_date_str,
            "previous_date_str": previous_date_str,
            "next_date_str": next_date_str,

            "breakfast_entries": breakfast_entries,
            "lunch_entries": lunch_entries,
            "dinner_entries": dinner_entries,
            "snack_entries": snack_entries,

            "total_calories": round(total_calories, 2),
            "total_proteins": round(total_proteins, 2),
            "total_fats": round(total_fats, 2),
            "total_carbs": round(total_carbs, 2),

            "target_calories": target_calories,
            "target_proteins": target_proteins,
            "target_fats": target_fats,
            "target_carbs": target_carbs,


            "remaining_proteins": round(remaining_proteins, 2),
            "remaining_fats": round(remaining_fats, 2),
            "remaining_carbs": round(remaining_carbs, 2),

            "calories_percent": calories_percent,
            "proteins_percent": proteins_percent,
            "fats_percent": fats_percent,
            "carbs_percent": carbs_percent,

            "recommendations": recommendations,

            "total_water": total_water,
            "target_water": target_water,
            "remaining_water": remaining_water,
            "water_count": water_count,
            "average_glass": average_glass,
            "water_percent": water_percent,
            "water_status": water_status,
        },
    )


@login_required
def add_meal_view(request):
    recent_product_id = request.GET.get("product")
    selected_date_str = request.GET.get("date")

    if request.method == "POST":
        form = MealEntryForm(request.POST)

        if form.is_valid():
            meal_entry = form.save(commit=False)
            meal_entry.user = request.user
            meal_entry.save()

            return redirect(f"/meals/?date={meal_entry.date}")
    else:
        initial_data = {}

        if selected_date_str:
            initial_data["date"] = selected_date_str
        else:
            initial_data["date"] = timezone.localdate()

        if recent_product_id:
            initial_data["product"] = recent_product_id

        form = MealEntryForm(initial=initial_data)

    return render(
        request,
        "users/add_meal.html",
        {
            "form": form,
            "selected_date_str": selected_date_str,
        },
    )


@login_required
def edit_meal_view(request, entry_id):
    meal_entry = get_object_or_404(
        MealEntry,
        id=entry_id,
        user=request.user,
    )

    if request.method == "POST":
        form = MealEntryForm(request.POST, instance=meal_entry)

        if form.is_valid():
            updated_entry = form.save()
            return redirect(f"/meals/?date={updated_entry.date}")
    else:
        form = MealEntryForm(instance=meal_entry)

    return render(
        request,
        "users/edit_meal.html",
        {
            "form": form,
            "meal_entry": meal_entry,
        },
    )


@login_required
def delete_meal_view(request, entry_id):
    meal_entry = get_object_or_404(
        MealEntry,
        id=entry_id,
        user=request.user,
    )

    selected_date = meal_entry.date

    if request.method == "POST":
        meal_entry.delete()
        return redirect(f"/meals/?date={selected_date}")

    return render(
        request,
        "users/delete_meal.html",
        {
            "meal_entry": meal_entry,
        },
    )


@login_required
def add_product_view(request):
    selected_date_str = request.GET.get("date", "").strip()

    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.is_custom = True
            product.save()

            if selected_date_str:
                return redirect(f"/add-meal/?product={product.id}&date={selected_date_str}")

            return redirect(f"/add-meal/?product={product.id}")
    else:
        form = ProductForm()

    return render(
        request,
        "users/add_product.html",
        {
            "form": form,
            "selected_date_str": selected_date_str,
        },
    )


@login_required
def progress_view(request):
    profile = get_or_create_user_profile(request.user)

    if request.method == "POST":
        form = WeightHistoryForm(request.POST)

        if form.is_valid():
            weight_entry = form.save(commit=False)
            weight_entry.user = request.user
            weight_entry.save()

            profile.current_weight = weight_entry.weight
            profile.save()

            return redirect("progress")
    else:
        form = WeightHistoryForm(initial={"date": timezone.localdate()})

    weight_entries = WeightHistory.objects.filter(
        user=request.user,
    ).order_by("date")

    labels = [entry.date.strftime("%d.%m.%Y") for entry in weight_entries]
    weights = [float(entry.weight) for entry in weight_entries]

    return render(
        request,
        "users/progress.html",
        {
            "profile": profile,
            "form": form,
            "weight_entries": weight_entries,
            "labels": labels,
            "weights": weights,
        },
    )


@login_required
def add_water_view(request):
    selected_date = get_selected_date(request)

    WaterEntry.objects.create(
        user=request.user,
        date=selected_date,
        amount_ml=250,
    )

    return redirect(f"/meals/?date={selected_date}")


@login_required
def add_water_500_view(request):
    selected_date = get_selected_date(request)

    WaterEntry.objects.create(
        user=request.user,
        date=selected_date,
        amount_ml=500,
    )

    return redirect(f"/meals/?date={selected_date}")


@login_required
def remove_last_water_view(request):
    selected_date = get_selected_date(request)

    last_entry = WaterEntry.objects.filter(
        user=request.user,
        date=selected_date,
    ).order_by("-created_at").first()

    if last_entry:
        last_entry.delete()

    return redirect(f"/meals/?date={selected_date}")


def offline_view(request):
    return render(request, "users/offline.html")

import os

from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseForbidden


def create_superadmin_view(request):
    secret = request.GET.get("secret")
    expected_secret = os.environ.get("ADMIN_CREATE_SECRET")

    if not expected_secret or secret != expected_secret:
        return HttpResponseForbidden("Forbidden")

    username = os.environ.get("ADMIN_USERNAME", "superadmin")
    email = os.environ.get("ADMIN_EMAIL", "")
    password = os.environ.get("ADMIN_PASSWORD")

    if not password:
        return HttpResponse("ADMIN_PASSWORD is not set", status=500)

    User = get_user_model()

    user, created = User.objects.get_or_create(username=username)

    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()

    if created:
        return HttpResponse(f"Superuser '{username}' created successfully.")

    return HttpResponse(f"User '{username}' updated to superuser successfully.")