from shargain.offers.application.actor import Actor
from shargain.offers.application.dto import TargetDTO
from shargain.offers.models import ScrappingTarget


def toggle_target_active(actor: Actor, target_id: int, is_active: bool) -> TargetDTO | None:
    try:
        target = ScrappingTarget.objects.get(id=target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist:
        return None

    target.is_active = is_active
    target.save(update_fields=["is_active"])

    return TargetDTO.from_orm(target)
