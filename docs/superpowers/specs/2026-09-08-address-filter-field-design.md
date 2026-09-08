# Address Filter Field — Design Spec

## Status

Under review.

## Problem

Users want to filter offers by address/location (especially street) in the existing notification Smart Filters. Currently:

- Address data lives unstructured in `metadata["extra"]` and is only used for generating map URLs and notification location display.
- The field plugin system exposes no address/location fields, so address is not filterable.
- OLX provides city + district (and coordinates); Otodom provides city + street (no coordinates). The two sources expose different components, so there is no shared field.

## Solution Overview

Add a single unified `address` string field, filterable by `contains` / `not_contains` / `equals`, built from the most specific available location components per source:

- **OLX**: `"City, District"` (falls back to City only or District only)
- **Otodom**: `"City, Street"` (falls back to City only)

Implemented as **two separate field plugins** (one for OLX, one for Otodom), both emitting the same `address` field name. Neither plugin re-implements address construction — both delegate to the existing `LocationParserFactory.get_parser(domain, metadata).get_location_name()`, which is the single source of truth and is already exercised by the notification location display. This guarantees the filterable field and the notification location string can never diverge.

The field automatically appears in the `available-fields` API and the Smart Filters dropdown because it is an extractable plugin field; no serializer, API, or frontend changes are required.

## Architecture

### New Plugin Files

Located in `shargain/offers/field_extraction/plugins/`.

**`olx_address.py` — `OlxAddressPlugin`**

```python
class OlxAddressPlugin(BaseFieldPlugin):
    def matches(self, url: ListUrl) -> bool:
        host = urlparse(url).netloc.lower()
        return host.endswith(".olx.pl")

    @property
    def fields(self) -> list[FieldDefinition]:
        return [FieldDefinition("address", _("Address"), FieldType.STRING)]

    def extract(self, offer, url) -> dict:
        parser = LocationParserFactory.get_parser(offer.domain, offer.metadata)
        return {"address": parser.get_location_name()}
```

- Matches all OLX hosts (`www.olx.pl`, subdomains) regardless of listing type — apartment and non-apartment alike (same host-matching pattern as `olx_delivery`).
- For OLX, `get_location_name()` reads `extra["location"]["cityName"]` / `["districtName"]` and returns `"City, District"`.

**`otodom_address.py` — `OtodomAddressPlugin`**

```python
class OtodomAddressPlugin(BaseFieldPlugin):
    def matches(self, url: ListUrl) -> bool:
        host = urlparse(url).netloc.lower()
        return host.endswith(".otodom.pl")

    @property
    def fields(self) -> list[FieldDefinition]:
        return [FieldDefinition("address", _("Address"), FieldType.STRING)]

    def extract(self, offer, url) -> dict:
        parser = LocationParserFactory.get_parser(offer.domain, offer.metadata)
        return {"address": parser.get_location_name()}
```

- Matches all Otodom hosts.
- For Otodom, `get_location_name()` reads `extra["location"]["address"]["city"]["name"]` and optional `street["name"]`, returning `"City, Street"`.

### Registry

In `shargain/offers/field_extraction/plugins/__init__.py`, register the two new plugins:

```python
from .core_fields import core_fields
from .olx_address import olx_address
from .olx_apartment import olx_apartment
from .olx_delivery import olx_delivery
from .otodom_address import otodom_address
from .otodom_apartment import otodom_apartment

registered_plugins = [core_fields, olx_delivery, olx_apartment, otodom_apartment, olx_address, otodom_address]
```

Order is irrelevant for correctness because both plugins emit unique field names and only one matches a given URL.

### Data Flow

- No model, serializer, API, or frontend changes.
- `address` appears in `OfferFieldResolver.get_fields(url)` → `GET /urls/{id}/available-fields` → the Smart Filters field dropdown, because it is a declared plugin field.
- `OfferFilterService.apply()` evaluates `address` rules like any other STRING field (`contains`, `not_contains`, `equals`).
- Address construction reuses `shargain/offers/services/location_parsers.py`; there is no duplicate parsing logic.

### Edge Cases / Behavior

- Missing/absent location data → `get_location_name()` returns `None` → the field value is `None` (no match).
- OLX city-only → `"City"`; district-only → `"District"`.
- Otodom city-only → `"City"`.
- Non-apartment listings on either domain still get an `address` value (domain-wide matching).
- The two plugins emit the field name `address`; the resolver dedups by name, and since only one domain matches a given URL, there is no collision in practice.

## Testing

Follow the existing plugin test pattern in `shargain/offers/tests/services/`. Use `OfferFactory.build()` per the repo convention.

**`test_olx_address_plugin.py`** — `TestOlxAddressPluginMatches`:
- matches `https://www.olx.pl/...`, a subdomain host, and a non-apartment listing URL
- does not match `otodom.pl` or `example.com` (and lookalike/evil domains)

`TestOlxAddressPluginFields`:
- fields listed are exactly `["address"]`; field is `FieldType.STRING` with label `"Address"` and no unit

`TestOlxAddressPluginExtract`:
- city + district → `"Warsaw, Centrum"`
- city only → `"Warsaw"`
- district only → `"Centrum"`
- no location data → `None`
- missing `extra` (metadata `{}`) → `None`

**`test_otodom_address_plugin.py`** — analogous:
- `matches` for `otodom.pl` hosts (calendar, non-apartment); no match for `olx.pl`/other
- fields listed are exactly `["address"]`; STRING
- city + street → `"Kraków, ul. Jana Dekerta"`
- city only → `"Kraków"`
- no location / missing `extra` → `None`

**Integration** (optional, one test): assert that `OfferFieldResolver.get_fields()` for an OLX URL includes `address`, and that `extract()` populates it in `ExtractedOffer.fields`.

## Scope & Constraints

- **In scope**: two new address plugins, registry registration, tests.
- **Out of scope**: no model changes, no API/serializer changes, no frontend changes, no changes to notification display logic, no new address-parsing logic (reuses the location parser).
- **Backward compatibility**: no existing behavior changes; the new field is additive.
