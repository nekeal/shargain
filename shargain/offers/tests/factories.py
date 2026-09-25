import factory
from django.utils import timezone
from faker import Faker

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.models import Offer, OfferLike, ScrapingUrl, ScrappingTarget

fake = Faker()


class ScrappingTargetFactory(factory.django.DjangoModelFactory):
    name = factory.LazyFunction(lambda: f"Target - {fake.word().title()}")
    enable_notifications = True
    is_active = True
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = ScrappingTarget


class ScrapingUrlFactory(factory.django.DjangoModelFactory):
    url = factory.LazyFunction(lambda: f"https://example.com/{fake.word()}")
    scraping_target = factory.SubFactory(ScrappingTargetFactory)

    class Meta:
        model = ScrapingUrl


class OfferFactory(factory.django.DjangoModelFactory):
    url = factory.LazyFunction(lambda: f"https://example.com/{fake.slug()}")
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=5))
    target = factory.SubFactory(ScrappingTargetFactory)
    list_url = factory.LazyAttribute(
        lambda o: o.target.url[0] if o.target.url else f"https://example.com/{fake.slug()}"
    )
    published_at = factory.LazyFunction(timezone.now)

    class Meta:
        model = Offer


class OfferLikeFactory(factory.django.DjangoModelFactory):
    offer = factory.SubFactory(OfferFactory)
    liker_label = factory.LazyFunction(lambda: str(fake.random_int()))

    class Meta:
        model = OfferLike
        django_get_or_create = ("offer", "liker_label")
