from dataclasses import dataclass

from shargain.subscriptions.models import Plan


@dataclass(frozen=True)
class PlanLimitsDTO:
    max_urls: int
    max_offers_per_target: int
    plan_slug: str

    @classmethod
    def from_plan(cls, plan: Plan) -> "PlanLimitsDTO":
        return cls(
            max_urls=plan.max_urls,
            max_offers_per_target=plan.max_offers_per_target,
            plan_slug=plan.slug,
        )
