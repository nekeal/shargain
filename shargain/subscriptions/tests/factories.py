import factory
from django.utils import timezone

from shargain.subscriptions.models import Plan, UserSubscription


class PlanFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Plan {n}")
    slug = factory.Sequence(lambda n: f"plan-{n}")
    max_urls = 3
    max_offers_per_target = 50
    is_default = False
    is_active = True
    display_order = 0

    class Meta:
        model = Plan


class UserSubscriptionFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory("shargain.accounts.tests.factories.UserFactory")
    plan = factory.SubFactory(PlanFactory)
    started_at = factory.LazyFunction(timezone.now)
    expires_at = None
    is_active = True

    class Meta:
        model = UserSubscription
