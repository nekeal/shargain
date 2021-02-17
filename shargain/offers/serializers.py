from rest_framework import serializers

from shargain.offers.models import Offer, ScrappingTarget


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
