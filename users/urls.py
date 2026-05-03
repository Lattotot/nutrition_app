from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    register_view,
    logout_view,
    profile_view,
    edit_profile_view,
    meal_list_view,
    add_meal_view,
    edit_meal_view,
    delete_meal_view,
    progress_view,
    add_water_view,
    add_water_view,
    add_water_500_view,
    remove_last_water_view,
    offline_view,
    add_product_view,
)

urlpatterns = [
    path("", profile_view, name="home"),
    path("register/", register_view, name="register"),
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", logout_view, name="logout"),

    path("profile/", profile_view, name="profile"),
    path("edit-profile/", edit_profile_view, name="edit_profile"),
    path("meals/", meal_list_view, name="meals"),
    path("add-meal/", add_meal_view, name="add_meal"),
    path("edit-meal/<int:entry_id>/", edit_meal_view, name="edit_meal"),
    path("delete-meal/<int:entry_id>/", delete_meal_view, name="delete_meal"),
    path("progress/", progress_view, name="progress"),
    path("add-water/", add_water_view, name="add_water"),
    path("add-water/", add_water_view, name="add_water"),
    path("add-water-500/", add_water_500_view, name="add_water_500"),
    path("remove-last-water/", remove_last_water_view, name="remove_last_water"),
    path("offline/", offline_view, name="offline"),
    path("add-product/", add_product_view, name="add_product"),
]
