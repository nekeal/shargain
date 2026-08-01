"""Tests for OlxApartmentPlugin."""

from shargain.offers.field_extraction import FieldType, ListUrl, RichValue
from shargain.offers.field_extraction.plugins.olx_apartment import olx_apartment
from shargain.offers.tests.factories import OfferFactory

OLX_URL = ListUrl("https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/krakow/")


def _params(*entries):
    return {"extra": {"params": list(entries)}}


class TestOlxApartmentPluginMatches:
    def test_matches_olx_apartment_url(self):
        assert olx_apartment.matches(OLX_URL) is True

    def test_matches_olx_mieszkania_wojewodztwo(self):
        assert olx_apartment.matches(ListUrl("https://www.olx.pl/nieruchomosci/mieszkania/")) is True

    def test_not_matches_other_olx(self):
        assert olx_apartment.matches(ListUrl("https://www.olx.pl/sport-hobby/pojazdy-elektryczne/")) is False

    def test_not_matches_otodom(self):
        assert olx_apartment.matches(ListUrl("https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie")) is False


class TestOlxApartmentPluginFields:
    def test_fields_listed(self):
        names = [f.name for f in olx_apartment.fields]
        assert set(names) == {"price_per_m2", "area", "floor", "rooms", "winda", "parking", "builttype", "market"}

    def test_number_fields_have_units(self):
        fields = {f.name: f for f in olx_apartment.fields}
        assert fields["price_per_m2"].field_type == FieldType.NUMBER
        assert fields["price_per_m2"].unit == "z\u0142/m\u00b2"
        assert fields["area"].unit == "m\u00b2"
        assert fields["winda"].field_type == FieldType.BOOLEAN
        assert fields["parking"].field_type == FieldType.BOOLEAN


class TestOlxApartmentPluginExtract:
    def test_full_params(self):
        offer = OfferFactory.build(
            metadata={
                "extra": {
                    "params": [
                        {"key": "price_per_m", "value": "15605 zł/m²", "normalizedValue": "15605"},
                        {"key": "m", "value": "49,40 m²", "normalizedValue": "49.4"},
                        {"key": "floor_select", "value": "2", "normalizedValue": "floor_2"},
                        {"key": "rooms", "value": "2 pokoje", "normalizedValue": "two"},
                        {"key": "winda", "value": "Tak", "normalizedValue": "Tak"},
                        {
                            "key": "parking",
                            "value": "przynależne na ulicy",
                            "normalizedValue": ["przynależne na ulicy"],
                        },
                        {"key": "builttype", "value": "Blok", "normalizedValue": "blok"},
                        {"key": "market", "value": "Wtórny", "normalizedValue": "secondary"},
                    ]
                }
            }
        )
        result = olx_apartment.extract(offer, OLX_URL)
        assert result["price_per_m2"] == 15605.0
        assert result["area"] == 49.4
        assert result["floor"] == 2
        assert result["rooms"] == 2
        assert result["winda"] is True
        assert result["parking"] == RichValue(True, "przynależne na ulicy")
        assert result["builttype"] == "blok"
        assert result["market"] == "secondary"

    def test_ground_floor_and_single_room(self):
        offer = OfferFactory.build(
            metadata=_params(
                {"key": "floor_select", "value": "0", "normalizedValue": "floor_0"},
                {"key": "rooms", "value": "1 pokój", "normalizedValue": "one"},
            )
        )
        result = olx_apartment.extract(offer, OLX_URL)
        assert result["floor"] == 0
        assert result["rooms"] == 1

    def test_negative_floor_is_parsed(self):
        offer = OfferFactory.build(
            metadata=_params({"key": "floor_select", "value": "-1", "normalizedValue": "floor_-1"})
        )
        assert olx_apartment.extract(offer, OLX_URL)["floor"] == -1

    def test_missing_params_return_none(self):
        offer = OfferFactory.build(metadata={"extra": {}})
        result = olx_apartment.extract(offer, OLX_URL)
        assert all(value is None for value in result.values())

    def test_missing_extra_returns_none(self):
        offer = OfferFactory.build(metadata={})
        result = olx_apartment.extract(offer, OLX_URL)
        assert all(value is None for value in result.values())

    def test_bad_number_format_returns_none(self):
        offer = OfferFactory.build(metadata=_params({"key": "price_per_m", "value": "n/a", "normalizedValue": "n/a"}))
        assert olx_apartment.extract(offer, OLX_URL)["price_per_m2"] is None

    def test_winda_yes_no_and_missing(self):
        yes = OfferFactory.build(metadata=_params({"key": "winda", "value": "Tak", "normalizedValue": "Tak"}))
        no = OfferFactory.build(metadata=_params({"key": "winda", "value": "Nie", "normalizedValue": "Nie"}))
        missing = OfferFactory.build(metadata={"extra": {}})
        assert olx_apartment.extract(yes, OLX_URL)["winda"] is True
        assert olx_apartment.extract(no, OLX_URL)["winda"] is False
        assert olx_apartment.extract(missing, OLX_URL)["winda"] is None

    def test_parking_brak_is_false(self):
        offer = OfferFactory.build(metadata=_params({"key": "parking", "value": "brak", "normalizedValue": ["brak"]}))
        assert olx_apartment.extract(offer, OLX_URL)["parking"] == RichValue(False)

    def test_parking_brak_with_other_choices_is_true(self):
        offer = OfferFactory.build(
            metadata=_params(
                {"key": "parking", "value": "brak, identyfikator", "normalizedValue": ["brak", "identyfikator"]}
            )
        )
        assert olx_apartment.extract(offer, OLX_URL)["parking"] == RichValue(True, "identyfikator")

    def test_parking_multiple_choices_joined_in_display(self):
        offer = OfferFactory.build(
            metadata=_params(
                {
                    "key": "parking",
                    "value": "przynależne na ulicy, w garażu",
                    "normalizedValue": ["przynależne na ulicy", "w garażu"],
                }
            )
        )
        assert olx_apartment.extract(offer, OLX_URL)["parking"] == RichValue(True, "przynależne na ulicy, w garażu")

    def test_parking_scalar_choice(self):
        offer = OfferFactory.build(
            metadata=_params({"key": "parking", "value": "parking strzeżony", "normalizedValue": "parking strzeżony"})
        )
        assert olx_apartment.extract(offer, OLX_URL)["parking"] == RichValue(True, "parking strzeżony")

    def test_parking_missing_is_none(self):
        offer = OfferFactory.build(metadata={"extra": {}})
        assert olx_apartment.extract(offer, OLX_URL)["parking"] is None
