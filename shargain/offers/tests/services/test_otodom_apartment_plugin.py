"""Tests for OtodomApartmentPlugin."""

from shargain.offers.field_extraction import FieldType, ListUrl
from shargain.offers.field_extraction.plugins.otodom_apartment import otodom_apartment
from shargain.offers.tests.factories import OfferFactory

OTODOM_URL = ListUrl("https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie")
OTODOM_KRAKOW_URL = ListUrl("https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/malopolskie/krakow/krakow/krakow")


def _extra(**kwargs):
    return {"extra": kwargs}


class TestOtodomApartmentPluginMatches:
    def test_matches_otodom_apartment_url(self):
        assert otodom_apartment.matches(OTODOM_URL) is True

    def test_matches_otodom_krakow_url(self):
        assert otodom_apartment.matches(OTODOM_KRAKOW_URL) is True

    def test_not_matches_otodom_rent(self):
        assert otodom_apartment.matches(ListUrl("https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie")) is False

    def test_not_matches_olx(self):
        assert otodom_apartment.matches(ListUrl("https://www.olx.pl/nieruchomosci/mieszkania/")) is False


class TestOtodomApartmentPluginFields:
    def test_fields_listed(self):
        names = [f.name for f in otodom_apartment.fields]
        assert set(names) == {"price_per_m2", "area", "floor", "rooms", "parking", "balcony"}

    def test_field_types(self):
        fields = {f.name: f for f in otodom_apartment.fields}
        assert fields["price_per_m2"].field_type == FieldType.NUMBER
        assert fields["price_per_m2"].unit == "z\u0142/m\u00b2"
        assert fields["area"].unit == "m\u00b2"
        assert fields["parking"].field_type == FieldType.BOOLEAN
        assert fields["balcony"].field_type == FieldType.BOOLEAN


class TestOtodomApartmentPluginExtract:
    def test_full_extra(self):
        offer = OfferFactory.build(
            metadata=_extra(
                pricePerSquareMeter={"value": 13700, "currency": "PLN"},
                areaInSquareMeters=82.27,
                floorNumber="SECOND",
                roomsNumber="FOUR",
                tags=[{"value": "BALCONY"}, {"value": "PARKING_SPOT"}, {"value": "SECURE_BUILDING"}],
            )
        )
        result = otodom_apartment.extract(offer, OTODOM_URL)
        assert result["price_per_m2"] == 13700.0
        assert result["area"] == 82.27
        assert result["floor"] == 2
        assert result["rooms"] == 4
        assert result["parking"] is True
        assert result["balcony"] is True

    def test_floor_enum_mapping(self):
        cases = {
            "GROUND": 0,
            "FIRST": 1,
            "EIGHTH": 8,
            "NINTH": 9,
            "ABOVE_TENTH": 0,
        }
        for enum_value, expected in cases.items():
            offer = OfferFactory.build(metadata=_extra(floorNumber=enum_value))
            assert otodom_apartment.extract(offer, OTODOM_URL)["floor"] == expected

    def test_rooms_enum_mapping(self):
        cases = {"ONE": 1, "FOUR": 4, "SIX": 6}
        for enum_value, expected in cases.items():
            offer = OfferFactory.build(metadata=_extra(roomsNumber=enum_value))
            assert otodom_apartment.extract(offer, OTODOM_URL)["rooms"] == expected

    def test_missing_extra_returns_none(self):
        offer = OfferFactory.build(metadata={})
        result = otodom_apartment.extract(offer, OTODOM_URL)
        assert all(value is None for value in result.values())

    def test_explicit_null_returns_none(self):
        offer = OfferFactory.build(
            metadata=_extra(
                pricePerSquareMeter=None,
                areaInSquareMeters=None,
                floorNumber=None,
                roomsNumber=None,
                tags=[],
            )
        )
        result = otodom_apartment.extract(offer, OTODOM_URL)
        assert result["price_per_m2"] is None
        assert result["area"] is None
        assert result["floor"] is None
        assert result["rooms"] is None

    def test_tags_absent_and_empty(self):
        no_tags = OfferFactory.build(metadata=_extra(tags=[{"value": "SECURE_BUILDING"}]))
        empty_tags = OfferFactory.build(metadata=_extra(tags=[]))
        missing_tags = OfferFactory.build(metadata={})
        assert otodom_apartment.extract(no_tags, OTODOM_URL)["parking"] is False
        assert otodom_apartment.extract(empty_tags, OTODOM_URL)["balcony"] is False
        assert otodom_apartment.extract(missing_tags, OTODOM_URL)["parking"] is None

    def test_bad_number_value_returns_none(self):
        offer = OfferFactory.build(metadata=_extra(areaInSquareMeters="dużo"))
        assert otodom_apartment.extract(offer, OTODOM_URL)["area"] is None
