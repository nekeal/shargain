from shargain.accounts.models import CustomUser
from shargain.offers.models import ScrappingTarget, TargetAccess, TargetRole
from shargain.offers.tests.factories import TargetAccessFactory


def grant_access(
    target: ScrappingTarget,
    user: CustomUser,
    role: TargetRole = TargetRole.EDITOR,
) -> TargetAccess:
    """Grant a named user access to a target in tests."""
    return TargetAccessFactory(target=target, user=user, role=role)
