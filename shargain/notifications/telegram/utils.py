from django.conf import settings


def get_token_for_webhook_url():
    """
    Used for configuring urlpatterns
    """
    if not settings.TELEGRAM_WEBHOOK_URL:
        return "token"
    else:
        return settings.TELEGRAM_WEBHOOK_URL.rstrip("/").split("/")[-1]
