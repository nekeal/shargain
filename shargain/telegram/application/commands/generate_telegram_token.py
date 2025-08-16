"""
Application command to generate a Telegram registration token for a user.
"""

from dataclasses import dataclass

from django.contrib.auth import get_user_model

from shargain.commons.application.actor import Actor
from shargain.offers.application.exceptions import ApplicationException
from shargain.telegram.bot import TelegramBot
from shargain.telegram.models import TelegramRegisterToken


class UserDoesNotExist(ApplicationException):
    """Exception raised when a user does not exist."""

    code: str = "user_does_not_exist"
    message: str = "User does not exist."


@dataclass
class GenerateTelegramTokenResult:
    """Result of the generate_telegram_token command."""

    token: str
    telegram_bot_url: str


User = get_user_model()


def generate_telegram_token(bot: TelegramBot, actor: Actor) -> GenerateTelegramTokenResult:
    """
    Generate a Telegram registration token for a user.

    Args:
        actor: The user performing the action.

    Returns:
        A dictionary containing the token and the Telegram bot URL.

    Raises:
        UserDoesNotExist: If the user doesn't exist.
    """

    try:
        user = User.objects.get(pk=actor.user_id)
    except User.DoesNotExist as e:
        raise UserDoesNotExist() from e

    # Check if user already has an active token
    active_token = TelegramRegisterToken.objects.filter(user=user, is_used=False).first()

    if active_token:
        token = active_token.register_token
    else:
        # Create a new token
        token_obj = TelegramRegisterToken.objects.create(user=user)
        token = token_obj.register_token
    return GenerateTelegramTokenResult(
        token=token,
        telegram_bot_url=f"https://t.me/{bot.get_username()}?start={token}",
    )
