from django.db import transaction

from shargain.telegram.models import TelegramRegisterToken, TelegramUser


def verify_telegram_token(token: str, chat_id: int) -> bool:
    with transaction.atomic():
        register_token = (
            TelegramRegisterToken.objects.select_for_update().filter(register_token=token, is_used=False).first()
        )
        if not register_token:
            return False

        register_token.is_used = True
        register_token.save()

        TelegramUser.objects.get_or_create(
            user=register_token.user,
            telegram_id=chat_id,
            defaults={"is_active": True},
        )
    return True
