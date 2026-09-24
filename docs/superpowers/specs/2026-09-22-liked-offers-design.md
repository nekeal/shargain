# Liked Offers — Design

- **Date:** 2026-09-22
- **Status:** Approved (pending user review)
- **Scope:** Backend-only. No web/frontend UI in this iteration.

## Why

Offer cards in a Telegram channel currently only inform — you can't act on a
good deal. This adds the ability to **like** offers from a Telegram channel,
persist those likes in the backend, and surface them in admin, so liked offers
remain attributable and discoverable even though the bot can't reliably link a
Telegram account to a Shargain account.

## Channel-Agnostic Likes

A like can originate from either surface, and the two may not be linkable:

1. **Telegram** — identity is a free-form string (no guaranteed account link).
2. **Web/dashboard (future)** — identity is a real authenticated account.

The like model must therefore store *either* an account FK *or* a free-form
label string, never both. This keeps the schema channel-agnostic: no
`telegram_id` column, no Telegram-specific naming, no forced account FK.

## Data Model

New model in `shargain/offers/models.py`:

```python
import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from shargain.commons.models import TimeStampedModel
from shargain.offers.models import Offer


class OfferLike(TimeStampedModel):
    """A user marked an offer as liked, from any channel."""

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name=_("Offer"),
    )

    # Authenticated surface (e.g. web dashboard). Either this or label is set.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="offer_likes",
        null=True,
        blank=True,
        verbose_name=_("Owner"),
    )

    # Anonymous surface (e.g. Telegram). Free-form identity string.
    liker_label = models.CharField(_("Liker label"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("Offer like")
        verbose_name_plural = _("Offer likes")
        ordering = ["offer_id", "pk"]
        constraints = [
            # Exactly one identity source: an account or a descriptive label.
            models.CheckConstraint(
                check=Q(owner__isnull=False) | ~Q(liker_label=""),
                name="offer_like_has_identity",
            ),
            # A liker can like an offer at most once (web account).
            models.UniqueConstraint(
                fields=["offer", "owner"],
                name="uniq_offer_like_owner",
                condition=Q(owner__isnull=False),
            ),
            # A liker can like an offer at most once (anonymous label).
            models.UniqueConstraint(
                fields=["offer", "liker_label"],
                name="uniq_offer_like_label",
                condition=~Q(liker_label=""),
            ),
        ]
```

**Semantics:**

- **Grouping under the same `ScrappingTarget` is free.** `Offer.target`
  already points at the scraping target, so `OfferLike.offer.target` gives you
  the target without any extra column or join.
- **Telegram liker label** is the liker's **Telegram user id** as a string
  (e.g. `"123456789"`). Telegram user ids are stable and never collide —
  unlike usernames, which can be renamed or absent. Identity label is generic /
  channel-agnostic: the same column supports any anonymous surface.
- **Dedup via partial unique constraints** — a like is idempotent per
  `(offer, owner)` and per `(offer, liker_label)`.
- **Toggle-friendly** — the same constraints make unreact → delete and re-react
  → recreate safe.

## Telegram Wiring

In `shargain/telegram/bot.py`:

1. **Require `message_reaction` updates**: `TelegramBot.get_bot().set_webhook(
   url, allowed_updates=[..., "message_reaction"])` (and similarly include
   `message_reaction` in `allowed_updates` for polling).
2. **Register a reaction handler**, responding to `MessageReactionUpdated`
   events. Telebot exposes `message_reaction_handler` and the bot instance
   supports `register_message_reaction_handler`. The handler:

   - Filters to the **❤️ (heart) emoji** — all other reactions (👍, 👎, ✅,
     ❗, ?) are ignored.
   - For a **heart added**: fetches the reacted message by
     `chat_id + message_id` via `get_message`, parses the offer URLs from the
     message text, resolves them to `Offer` rows, and creates one `OfferLike`
     per offer with `liker_label = str(reaction user id)`.
   - For a **heart removed**: deletes the matching `OfferLike` rows
     (toggle → unlikes).
   - If the message contains **no offer URLs** (e.g. a menu/list/delete-prompt
     card), it is a **silent no-op**.

```python
@TelegramBot.get_bot().message_reaction_handler(func=lambda u: True)
def handle_like_reaction(reaction_update: MessageReactionUpdated) -> None:
    heart_added = is_heart_reaction_added(reaction_update)   # old vs new
    offers = resolve_offers_from_reaction(reaction_update)   # fetch + parse URLs
    liker_label = str(reaction_update.user.id) if reaction_update.user else str(reaction_update.chat.id)
    if heart_added:
        OfferLike.objects.bulk_create_from_offers(offers, liker_label=liker_label, ignore_conflicts=True)
    else:
        OfferLike.objects.filter(offer__in=offers, liker_label=liker_label).delete()
```

`resolve_offers_from_reaction`:
- Fetches the message by `chat_id + message_id` via the bot API (`get_message`).
- Reads the offer URLs from the message text (same URL-extraction regex used by
  notification senders to build cards — reuse it rather than duplicating).
- Returns the matching `Offer` rows, deduplicated. Returns empty for messages
  without offer URLs (menu/list/delete cards, single-offer-with-location cards
  are fine since URLs are still in text).

Deferred (not in scope, no mapping table): resolving a `message_id` to offers
via a stored mapping. We rely on parsing the message body because cards embed
real offer URLs and the bot already has `get_message`. This keeps the MVP free
of a `message_id → offers` bookkeeping table.

## Admin Surface

In `shargain/offers/admin.py`:

- Register **`OfferLikeAdmin`** with standard Django **full CRUD** (add /
  change / delete via the admin's normal add form — pick a target+offer via the
  `offer` FK dropdown). This enables "allow adding a liked offer" from the
  admin, plus edit/delete for corrections.
  - `list_display = ("offer", "liker_label", "owner", "created_at")`
  - `list_filter = ("offer__target",)`
  - `search_fields = ("offer__url", "offer__title", "liker_label")`
- No inline on `Offer`, and no modification to `OfferAdmin`.

Given likes attach to offers (not to a "who liked" account in the Telegram
case), a per-offer inline would be misleading; the standalone `OfferLikeAdmin`
with full CRUD is the requested surface.

## Edge Cases

| Case | Behavior |
| --- | --- |
| ❤️ on multi-offer batched card | One `OfferLike` per offer in the card, all with same liker label (grouped via each offer's target) |
| ❤️ on menu/list/delete-prompt card | Silent no-op (no offer URLs in text) |
| ❤️ on single-offer-with-location card | Liked normally (URL present in text) |
| Un-react (remove ❤️) | Deletes matching `OfferLike` rows (toggle/unlike) |
| React again after remove | Recreates the like (idempotent via unique constraint) |
| Two users heart the same offer | Two separate `OfferLike` rows, one per liker label |
| Non-heart reactions (👍, ❗, …) | Ignored (no side effects) |
| Heart on a chat whose message can't be fetched | Silent no-op, logged |

## Testing

Django tests under `shargain/offers/tests/` and `shargain/telegram/tests/`:

- **Model** — `CheckConstraint` allows owner OR label, rejects neither/both;
  unique constraints dedup per `(offer, owner)` and per `(offer, liker_label)`.
- **Telegram handler** — heart on offer card creates correct `OfferLike` rows;
  heart removal deletes them; non-offer message is a silent no-op; non-heart
  reactions are ignored; idempotent re-like.
- **Admin** — `OfferLikeAdmin` registered, add/change/delete via normal
  Django admin views.

## Out of Scope / Future Work

- Web/dashboard UI (frontend) for liking offers or viewing likes.
- Web-originated likes via an `owner` FK (schema prepared, surface not built).
- `message_id → offers` mapping table (avoided by parsing message text).
- Notifications/aggregations ("top liked offers") dashboards.
