from __future__ import annotations

from shargain.commons.application.actor import Actor
from shargain.offers.application.access import can_manage_target
from shargain.offers.application.exceptions import TargetDoesNotExist, TargetPermissionDenied
from shargain.offers.models import ScrappingTarget


def update_scraping_target_name(actor: Actor, target_id: int, name: str) -> None:
    """
    Updates the name of a scraping target.
    """
    try:
        target = ScrappingTarget.objects.for_user(actor.user_id).get(id=target_id)
    except ScrappingTarget.DoesNotExist as e:
        raise TargetDoesNotExist() from e

    if not can_manage_target(actor.user_id, target):
        raise TargetPermissionDenied()

    target.name = name
    target.save()
