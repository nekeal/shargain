from shargain.offers.models import ScrappingTarget, TargetRole


def get_user_role(user_id: int, target: ScrappingTarget) -> TargetRole | str | None:
    if target.owner_id == user_id:
        return "owner"
    access = target.accesses.filter(user_id=user_id).first()
    return TargetRole(access.role) if access else None


def can_view_target(user_id: int, target: ScrappingTarget) -> bool:
    return target.owner_id == user_id or target.accesses.filter(user_id=user_id).exists()


def can_manage_urls(user_id: int, target: ScrappingTarget) -> bool:
    if target.owner_id == user_id:
        return True
    return target.accesses.filter(
        user_id=user_id,
        role__in=[TargetRole.EDITOR, TargetRole.ADMIN],
    ).exists()


def can_manage_target(user_id: int, target: ScrappingTarget) -> bool:
    if target.owner_id == user_id:
        return True
    return target.accesses.filter(
        user_id=user_id,
        role=TargetRole.ADMIN,
    ).exists()


def can_delete_target(user_id: int, target: ScrappingTarget) -> bool:
    return target.owner_id == user_id
