"""
List all ScrapingTargets for a user.

This query retrieves a paginated list of scraping targets belonging to the specified user.
"""

from dataclasses import dataclass
from datetime import datetime

from shargain.offers.application.actor import Actor


@dataclass(frozen=True)
class TargetDto:
    id_: int
    name: str
    enable_notifications: bool
    is_active: bool
    notification_config_id: int | None
    updated_at: datetime


def list_targets(
    actor: Actor,
    page: int = 1,
    per_page: int = 20,
) -> list[TargetDto]:
    """List all targets for a user with pagination.

    Args:
        actor: The user whose targets to list.
        page: Page number (1-based).
        per_page: Number of items per page.

    Returns: List of TargetDto objects.
    """
    # Implementation will be added in the service layer
    raise NotImplementedError("Implementation pending")
