import logging
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
from shargain.offers.field_extraction import ListUrl, OfferFieldResolver, RichValue
from shargain.offers.location_parsers import LocationParserFactory
from shargain.offers.models import Offer, ScrappingTarget, UserOfferState

logger = logging.getLogger(__name__)


def _build_attributes(offer: Offer) -> list[OfferAttribute]:
    if not offer.list_url:
        return []
    try:
        list_url = ListUrl(offer.list_url)
        field_specs = OfferFieldResolver.get_fields(list_url)
        extracted = OfferFieldResolver.extract(offer, list_url)

        attributes: list[OfferAttribute] = []
        specs = field_specs.values() if isinstance(field_specs, dict) else field_specs
        for spec in specs:
            try:
                name = spec.name
                if name in ("title", "price"):
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
            except Exception:
                logger.exception(
                    "Failed to build attribute '%s' for offer %s", getattr(spec, "name", "unknown"), offer.id
                )
        return attributes
    except Exception:
        logger.exception("Failed to build attributes for offer %s", offer.id)
        return []


def _build_location(offer: Offer) -> OfferLocation | None:
    try:
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
    except Exception:
        logger.exception("Failed to build location for offer %s", offer.id)
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

    state_subquery = UserOfferState.objects.filter(user_id=actor.user_id, offer_id=OuterRef("pk"))

    if seen is True:
        qs = qs.filter(Exists(state_subquery.filter(seen_at__isnull=False)))
    elif seen is False:
        qs = qs.exclude(Exists(state_subquery.filter(seen_at__isnull=False)))

    if liked is True:
        qs = qs.filter(Exists(state_subquery.filter(liked_at__isnull=False)))
    elif liked is False:
        qs = qs.exclude(Exists(state_subquery.filter(liked_at__isnull=False)))

    if ordering == "oldest":
        qs = qs.order_by("created_at", "id")
    else:
        qs = qs.order_by("-created_at", "-id")

    limit = max(1, limit)
    offset = max(0, offset)

    total_count = qs.count()
    page_offers = list(qs[offset : offset + limit])

    offer_ids = [o.id for o in page_offers]
    state_map = get_offer_states(actor, offer_ids)

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
        )
        for o in page_offers
    ]

    return PublicOfferPage(count=total_count, items=items)
