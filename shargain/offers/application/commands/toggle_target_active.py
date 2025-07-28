from dataclasses import dataclass
from typing import Self

from shargain.offers.application.actor import Actor
from shargain.offers.models import ScrappingTarget


@dataclass
class TargetDTO:
    id: int
    is_active: bool

    @classmethod
    def from_orm(cls, target: ScrappingTarget) -> Self:
        return cls(id=target.pk, is_active=target.is_active)


def toggle_target_active(actor: Actor, target_id: int, is_active: bool) -> TargetDTO | None:
    try:
        target = ScrappingTarget.objects.get(id=target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist:
        return None

    target.is_active = is_active
    target.save(update_fields=["is_active", "updated_at"])

    return TargetDTO.from_orm(target)
