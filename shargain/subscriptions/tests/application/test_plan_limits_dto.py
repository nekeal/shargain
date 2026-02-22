from dataclasses import FrozenInstanceError, fields

import pytest

from shargain.subscriptions.dto import PlanLimitsDTO


@pytest.mark.django_db
def test_plan_limits_dto_is_frozen_and_has_expected_contract():
    dto = PlanLimitsDTO(max_urls=3, max_offers_per_target=50, plan_slug="free")

    assert [field.name for field in fields(dto)] == ["max_urls", "max_offers_per_target", "plan_slug"]

    with pytest.raises(FrozenInstanceError):
        dto.max_urls = 10
