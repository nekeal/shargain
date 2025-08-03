from shargain.offers.application.actor import Actor
from shargain.offers.models import ScrappingTarget


def delete_target(actor: Actor, target_id: int) -> None:
    """Delete a target by ID if the actor has permission.

    Args:
        actor: The actor performing the action
        target_id: ID of the target to delete
    """
    try:
        target = ScrappingTarget.objects.get(id=target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist:
        return
    target.delete()
