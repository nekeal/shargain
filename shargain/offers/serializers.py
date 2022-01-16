from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from shargain.offers.models import Offer, ScrappingTarget


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
        slug_field="url", queryset=ScrappingTarget.objects.all()
    )

    class Meta:
        model = Offer
        exclude = ()

    def create(self, validated_data):
        url = validated_data.pop("url")
        offer, _ = Offer.objects.get_or_create(url=url, defaults=validated_data)
        return offer


class ScrappingTargetSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ScrappingTarget
        fields = ("id", "name", "url", "enable_notifications", "notification_config")

    def get_url(self, obj):
        return obj.url


class AddTargetUrlSerializer(serializers.ModelSerializer):
    url = serializers.URLField()

    class Meta:
        model = ScrappingTarget
        fields = ("url",)
