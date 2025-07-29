from __future__ import annotations

from shargain.offers.application.actor import Actor
from shargain.offers.application.dto import TargetDTO
from shargain.offers.models import ScrappingTarget


def get_target(actor: Actor, target_id: int) -> TargetDTO | None:
    try:
        target = ScrappingTarget.objects.prefetch_related("scrapingurl_set").get(id=target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist:
        return None
    return TargetDTO.from_orm(target)
