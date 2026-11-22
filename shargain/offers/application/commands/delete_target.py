from shargain.commons.application.actor import Actor
from shargain.offers.application.access import can_delete_target
from shargain.offers.application.exceptions import TargetPermissionDenied
from shargain.offers.models import ScrappingTarget


def delete_target(actor: Actor, target_id: int) -> None:
    """Delete a target by ID if the actor has permission.

    Args:
        actor: The actor performing the action
        target_id: ID of the target to delete
    """
    try:
        target = ScrappingTarget.objects.for_user(actor.user_id).get(id=target_id)
    except ScrappingTarget.DoesNotExist:
        return

    if not can_delete_target(actor.user_id, target):
        raise TargetPermissionDenied()

    target.delete()
