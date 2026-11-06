"""Job handlers for the notifications domain."""

import logging

from shargain.jobs.exceptions import RateLimited, RetryableError
from shargain.jobs.registry import job_handler
from shargain.notifications.models import NotificationConfig
from shargain.notifications.senders import TelegramNotificationSender

logger = logging.getLogger(__name__)


@job_handler("notification.telegram")
def handle_telegram_notification(job) -> None:
    payload = job.payload or {}
    config_id = payload.get("config_id")
    if not config_id:
        raise RetryableError("Missing config_id in payload")

    try:
        config = NotificationConfig.objects.get(pk=config_id)
    except NotificationConfig.DoesNotExist as exc:
        raise RetryableError(f"NotificationConfig {config_id} not found") from exc

    sender = TelegramNotificationSender(config)
    kind = payload.get("kind", "text")

    try:
        if kind == "location":
            sender.send_with_pin(
                payload["message"],
                payload["lat"],
                payload["lon"],
                horizontal_accuracy=payload.get("horizontal_accuracy", 1500.0),
            )
        else:
            sender.send(payload["message"])
    except Exception as exc:  # noqa: BLE001
        # detect rate limit from telebot
        retry_after = getattr(exc, "retry_after", None)
        status_code = getattr(getattr(exc, "result", None), "status_code", None)
        if retry_after is not None or status_code == 429:
            raise RateLimited(retry_after=retry_after or 60) from exc
        raise
