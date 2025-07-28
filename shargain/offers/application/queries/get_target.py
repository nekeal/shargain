from __future__ import annotations

import dataclasses

from shargain.offers.application.actor import Actor
from shargain.offers.models import ScrappingTarget


@dataclasses.dataclass
class GetTargetQuery:
    id: int


@dataclasses.dataclass
class TargetDTO:
    id: int
    name: str
    enable_notifications: bool
    is_active: bool

    @classmethod
    def from_orm(cls, target: ScrappingTarget) -> TargetDTO:
        return cls(
            id=target.id,
            name=target.name,
            enable_notifications=target.enable_notifications,
            is_active=target.is_active,
        )


def get_target(query: GetTargetQuery, actor: Actor) -> TargetDTO | None:
    try:
        target = ScrappingTarget.objects.get(id=query.id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist:
        return None
    return TargetDTO.from_orm(target)
