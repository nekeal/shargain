import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.telegram.models import TelegramUser


@pytest.mark.django_db
class TestTelegramUser:
    def test_create_telegram_user(self):
        user = UserFactory.create()
        telegram_user = TelegramUser.objects.create(
            user=user,
            telegram_id="12345",
            is_active=True,
        )
        assert telegram_user.user == user
        assert telegram_user.telegram_id == "12345"
        assert telegram_user.is_active is True
