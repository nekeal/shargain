from django.contrib import admin

from shargain.telegram.models import TelegramRegisterToken, TelegramUser


@admin.register(TelegramRegisterToken)
class TelegramRegisterTokenAdmin(admin.ModelAdmin):
    pass


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    pass
