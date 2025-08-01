"""
Create a new ScrapingTarget for a user.

This command handles the creation of a new scraping target with the given name and configuration.
"""

from shargain.offers.application.actor import Actor


def create_target(
    actor: Actor,
    name: str,
    enable_notifications: bool = True,
    notification_config_id: int | None = None,
) -> dict:
    """Create a new scraping target.

    Args:
        actor: The user for whom the target is being created.
        name: Name for the new target.
        enable_notifications: Whether to enable notifications
        notification_config_id: Optional ID of the notification configuration.

    Returns:
        dict: Created target data.

    Raises:
        ValueError: If the target name is invalid or already exists.
    """
    # Implementation will be added in the service layer
    raise NotImplementedError("Implementation pending")
