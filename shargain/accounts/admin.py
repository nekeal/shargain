from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from shargain.accounts.models import CustomUser, RegisterToken


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(RegisterToken)
class RegisterTokenAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "created_at",
        "already_used",
    )
    list_filter = ("already_used",)
    search_fields = ("token",)
