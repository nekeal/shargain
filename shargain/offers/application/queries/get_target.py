from __future__ import annotations

from shargain.offers.application.actor import Actor
from shargain.offers.application.dto import TargetDTO
from shargain.offers.application.exceptions import TargetDoesNotExist
from shargain.offers.models import ScrappingTarget


def get_target(actor: Actor, target_id: int) -> TargetDTO:
    try:
        target = ScrappingTarget.objects.prefetch_related("scrapingurl_set").get(id=target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist as e:
        raise TargetDoesNotExist() from e
    return TargetDTO.from_orm(target)


def get_target_by_user(actor: Actor) -> TargetDTO:
    if not (
        target := ScrappingTarget.objects.prefetch_related("scrapingurl_set")
        .filter(owner=actor.user_id)
        .order_by("-id")
        .first()
    ):
        raise TargetDoesNotExist()
    return TargetDTO.from_orm(target)
