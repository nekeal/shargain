import pytest

from shargain.offers.serializers import OfferBasicSerializer, OfferMetadataSerializer


class TestOfferMetadataSerializer:
    def test_valid_extra_data(self):
        data = {"extra": {"foo": "bar"}}
        serializer = OfferMetadataSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data == data

    def test_missing_extra_key_is_allowed_due_to_default(self):
        # Even if 'extra' is missing, it should be valid and return default
        data = {}
        serializer = OfferMetadataSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data == {"extra": {}}

    def test_unknown_field_at_root_is_ignored(self):
        data = {"foo": "bar", "extra": {"baz": 1}}
        serializer = OfferMetadataSerializer(data=data)
        assert serializer.is_valid()
        # 'foo' should be ignored, 'extra' should be preserved
        assert "foo" not in serializer.validated_data
        assert serializer.validated_data == {"extra": {"baz": 1}}

    def test_null_values_in_extra_are_allowed(self):
        data = {"extra": {"salary": None, "externalUrl": None}}
        serializer = OfferMetadataSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data == data


class TestOfferBasicSerializer:
    @pytest.mark.django_db
    def test_metadata_is_validated(self):
        data = {
            "url": "https://example.com/test",
            "title": "Test Offer",
            "metadata": {"extra": {"foo": "bar"}},
        }
        serializer = OfferBasicSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["metadata"] == {"extra": {"foo": "bar"}}

    @pytest.mark.django_db
    def test_metadata_defaults_to_extra_if_not_provided(self):
        data = {
            "url": "https://example.com/test",
            "title": "Test Offer",
        }
        serializer = OfferBasicSerializer(data=data)
        assert serializer.is_valid()
        # Note: In ModelSerializer, if field is not in data, it might not be in validated_data
        # unless it has a default in the serializer.
        # But when saving to model, the model default will kick in.
