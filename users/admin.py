from django.contrib import admin
from .models import UserProfile, Product, MealEntry, WeightHistory, WaterEntry


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "age",
        "gender",
        "height",
        "current_weight",
        "target_weight",
        "goal",
    )
    search_fields = ("user__username",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "calories", "proteins", "fats", "carbs", "is_custom")
    search_fields = ("name",)
    list_filter = ("is_custom",)

@admin.register(MealEntry)
class MealEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "meal_type", "amount_grams", "date")
    list_filter = ("meal_type", "date")
    search_fields = ("user__username", "product__name")

@admin.register(WeightHistory)
class WeightHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "weight", "date")
    list_filter = ("date",)
    search_fields = ("user__username",)

@admin.register(WaterEntry)
class WaterEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "amount_ml", "created_at")
    list_filter = ("date",)
    search_fields = ("user__username",)