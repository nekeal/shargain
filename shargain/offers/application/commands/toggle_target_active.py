from shargain.commons.application.actor import Actor
from shargain.offers.application.access import can_manage_target
from shargain.offers.application.dto import TargetDTO
from shargain.offers.application.exceptions import TargetDoesNotExist, TargetPermissionDenied
from shargain.offers.models import ScrappingTarget


def toggle_target_active(actor: Actor, target_id: int, is_active: bool) -> TargetDTO:
    try:
        target = ScrappingTarget.objects.for_user(actor.user_id).get(id=target_id)
    except ScrappingTarget.DoesNotExist as e:
        raise TargetDoesNotExist() from e

    if not can_manage_target(actor.user_id, target):
        raise TargetPermissionDenied()

    target.is_active = is_active
    target.save(update_fields=["is_active"])

    return TargetDTO.from_orm(target)
