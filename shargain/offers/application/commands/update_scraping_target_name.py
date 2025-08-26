from __future__ import annotations

from shargain.commons.application.actor import Actor
from shargain.offers.application.exceptions import TargetDoesNotExist
from shargain.offers.models import ScrappingTarget


def update_scraping_target_name(actor: Actor, target_id: int, name: str) -> None:
    """
    Updates the name of a scraping target.
    """
    try:
        target = ScrappingTarget.objects.get(id=target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist as e:
        raise TargetDoesNotExist() from e

    target.name = name
    target.save()
