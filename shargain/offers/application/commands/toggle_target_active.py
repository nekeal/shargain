from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import TargetDTO
from shargain.offers.application.exceptions import TargetDoesNotExist
from shargain.offers.models import ScrappingTarget


def toggle_target_active(actor: Actor, target_id: int, is_active: bool) -> TargetDTO:
    try:
        target = ScrappingTarget.objects.get(id=target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist as e:
        raise TargetDoesNotExist() from e

    target.is_active = is_active
    target.save(update_fields=["is_active"])

    return TargetDTO.from_orm(target)
