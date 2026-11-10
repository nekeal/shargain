from typing import Literal

from django.db.models import Exists, OuterRef

from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import (
    OfferAttribute,
    OfferLocation,
    PublicOffer,
    PublicOfferPage,
)
from shargain.offers.application.exceptions import TargetDoesNotExist
from shargain.offers.application.offer_state import get_offer_states
from shargain.offers.field_extraction import (
    ListUrl,
    OfferFieldResolver,
    RichValue,
    clean_html_description,
)
from shargain.offers.location_parsers import LocationParserFactory
from shargain.offers.models import Offer, OfferQueryset, ScrapingUrl, ScrappingTarget, UserOfferState


def _build_attributes(offer: Offer) -> list[OfferAttribute]:
    if not offer.list_url:
        return []
    list_url = ListUrl(offer.list_url)
    field_specs = OfferFieldResolver.get_fields(list_url)
    extracted = OfferFieldResolver.extract(offer, list_url)

    attributes: list[OfferAttribute] = []
    specs = field_specs.values() if isinstance(field_specs, dict) else field_specs
    for spec in specs:
        name = spec.name
        if name in ("title", "price", "description"):
            continue
        val = extracted.get(name)
        if val is None:
            continue

        if isinstance(val, RichValue):
            raw_val = val.value
            display = val.display
        else:
            raw_val = val
            display = None

        if raw_val is None:
            continue

        field_type_str = spec.field_type.value if hasattr(spec.field_type, "value") else str(spec.field_type)
        unit_str = str(spec.unit) if spec.unit is not None else None

        attributes.append(
            OfferAttribute(
                name=name,
                label=str(spec.label),
                type=field_type_str,
                unit=unit_str,
                value=raw_val,
                display=display,
            )
        )
    return attributes


def _build_location(offer: Offer) -> OfferLocation | None:
    parser = LocationParserFactory.get_parser(offer.domain, offer.metadata)
    coords = parser.get_coordinates()
    map_url = parser.get_map_url()
    loc_name = parser.get_location_name()
    is_exact = parser.is_location_exact()

    if not loc_name and not map_url and not coords:
        return None

    return OfferLocation(
        name=loc_name,
        map_url=map_url,
        latitude=coords.lat if coords else None,
        longitude=coords.lon if coords else None,
        is_exact=bool(is_exact),
    )


def _extract_image_url(item: object) -> str | None:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        url = item.get("large") or item.get("medium") or item.get("small") or item.get("url")
        if url:
            return str(url)
    return None


def _build_images(offer: Offer) -> list[str]:
    extra = (offer.metadata or {}).get("extra") or {}
    raw_list = extra.get("images") or extra.get("photos")
    images: list[str] = []
    if isinstance(raw_list, list):
        for item in raw_list:
            url = _extract_image_url(item)
            if url:
                images.append(url)

    if not images and offer.main_image_url:
        images.append(offer.main_image_url)
    return images


def _build_description(offer: Offer) -> str | None:
    if offer.list_url:
        extracted = OfferFieldResolver.extract(offer, ListUrl(offer.list_url))
        desc = extracted.get("description")
        if desc:
            val = desc.value if isinstance(desc, RichValue) else desc
            if val and str(val).strip():
                return str(val)
    extra = (offer.metadata or {}).get("extra") or {}
    raw = (
        extra.get("description")
        or extra.get("shortDescription")
        or extra.get("description_clean")
        or (offer.metadata or {}).get("description")
    )
    if raw:
        cleaned = clean_html_description(str(raw))
        if cleaned and cleaned.strip():
            return cleaned
    return None


def _apply_filters_and_ordering(
    qs: OfferQueryset,
    user_id: int,
    seen: bool | None,
    liked: bool | None,
    ordering: Literal["oldest", "newest"],
) -> OfferQueryset:
    state_subquery = UserOfferState.objects.filter(user_id=user_id, offer_id=OuterRef("pk"))

    if seen is True:
        qs = qs.filter(Exists(state_subquery.filter(seen_at__isnull=False)))
    elif seen is False:
        qs = qs.exclude(Exists(state_subquery.filter(seen_at__isnull=False)))

    if liked is True:
        qs = qs.filter(Exists(state_subquery.filter(liked_at__isnull=False)))
    elif liked is False:
        qs = qs.exclude(Exists(state_subquery.filter(liked_at__isnull=False)))

    if ordering == "oldest":
        return qs.order_by("created_at", "id")
    return qs.order_by("-created_at", "-id")


def _resolve_scraping_url_name(list_url: str | None, scraping_url_map: dict[str, str]) -> str | None:
    if not list_url:
        return None
    if list_url in scraping_url_map:
        return scraping_url_map[list_url]
    base_list_url = list_url.split("?")[0]
    for su_url, su_name in scraping_url_map.items():
        if su_url.split("?")[0] == base_list_url:
            return su_name
    return None


def list_public_offers(
    actor: Actor,
    target_id: int,
    seen: bool | None = None,
    liked: bool | None = None,
    ordering: Literal["oldest", "newest"] = "oldest",
    limit: int = 20,
    offset: int = 0,
) -> PublicOfferPage:
    if not ScrappingTarget.objects.filter(pk=target_id, owner_id=actor.user_id).exists():
        raise TargetDoesNotExist()

    qs = Offer.objects.filter(target_id=target_id, passed_filters=True).defer("source_html")
    qs = _apply_filters_and_ordering(qs, actor.user_id, seen, liked, ordering)

    limit = max(1, limit)
    offset = max(0, offset)

    total_count = qs.count()
    page_offers = list(qs[offset : offset + limit])

    offer_ids = [o.id for o in page_offers]
    state_map = get_offer_states(actor, offer_ids)

    scraping_urls = list(ScrapingUrl.objects.filter(scraping_target_id=target_id).values("url", "name"))
    scraping_url_map = {su["url"]: su["name"] for su in scraping_urls if su["url"]}

    items = [
        PublicOffer(
            id=o.id,
            url=o.url,
            title=o.title,
            price=o.price,
            main_image_url=o.main_image_url or None,
            published_at=o.published_at,
            created_at=o.created_at,
            closed_at=o.closed_at,
            list_url=o.list_url,
            is_seen=state_map[o.id].is_seen,
            seen_at=state_map[o.id].seen_at,
            is_liked=state_map[o.id].is_liked,
            liked_at=state_map[o.id].liked_at,
            attributes=_build_attributes(o),
            location=_build_location(o),
            images=_build_images(o),
            scraping_url_name=_resolve_scraping_url_name(o.list_url, scraping_url_map),
            description=_build_description(o),
        )
        for o in page_offers
    ]

    return PublicOfferPage(count=total_count, items=items)
