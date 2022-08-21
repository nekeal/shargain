from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from shargain.offers.models import Offer, ScrapingUrl, ScrappingTarget


class OfferBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ("url", "title", "price", "published_at", "main_image_url")


class OfferBatchCreateSerializer(serializers.Serializer):
    target = serializers.SlugRelatedField(
        slug_field="name", queryset=ScrappingTarget.objects.all()
    )
    offers = OfferBasicSerializer(many=True)

    class Meta:
        model = Offer

    def validate_offers(self, value):
        if not value:
            raise ValidationError("List of offers cannot be empty")
        return value


class OfferSerializer(serializers.ModelSerializer):
    target = serializers.SlugRelatedField(
        slug_field="name", queryset=ScrappingTarget.objects.all()
    )

    class Meta:
        model = Offer
        exclude = ()

    def create(self, validated_data):
        url = validated_data.pop("url")
        offer, _ = Offer.objects.get_or_create(url=url, defaults=validated_data)
        return offer


class ScrapingUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapingUrl
        fields = ("id", "name", "url")


class ScrappingTargetSerializer(serializers.ModelSerializer):
    urls = serializers.SerializerMethodField(method_name="get_scraping_urls")

    class Meta:
        model = ScrappingTarget
        fields = (
            "id",
            "name",
            "url",
            "urls",
            "enable_notifications",
            "notification_config",
        )

    @staticmethod
    def get_scraping_urls(obj: ScrappingTarget):
        return [scraping_url.url for scraping_url in obj.scrapingurl_set.all()]


class AddTargetUrlSerializer(serializers.ModelSerializer):
    url = serializers.URLField()

    class Meta:
        model = ScrappingTarget
        fields = ("url",)
