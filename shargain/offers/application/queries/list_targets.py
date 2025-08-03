"""
List all ScrapingTargets for a user.

This query retrieves a paginated list of scraping targets belonging to the specified user.
"""

from dataclasses import dataclass

from django.db.models import QuerySet

from shargain.offers.application.actor import Actor
from shargain.offers.models import ScrappingTarget


@dataclass(frozen=True)
class TargetDto:
    id_: int
    name: str
    enable_notifications: bool
    is_active: bool
    notification_config_id: int | None


def _get_user_targets(actor: Actor) -> QuerySet[ScrappingTarget]:
    """Get queryset of targets for the given user."""
    return ScrappingTarget.objects.filter(owner_id=actor.user_id)


def list_targets(
    actor: Actor,
    page: int = 1,
    per_page: int = 20,
) -> list[TargetDto]:
    """List all targets for a user with pagination.

    Args:
        actor: The user whose targets to list.
        page: Page number (1-based).
        per_page: Number of items per page (1-100).

    Returns: List of TargetDto objects.
    """
    page = max(1, page)
    per_page = max(1, min(per_page, 100))

    offset = (page - 1) * per_page

    targets = _get_user_targets(actor).order_by("-id")[offset : offset + per_page]

    return [
        TargetDto(
            id_=target.id,
            name=target.name,
            enable_notifications=target.enable_notifications,
            is_active=target.is_active,
            notification_config_id=target.notification_config_id,
        )
        for target in targets
    ]
