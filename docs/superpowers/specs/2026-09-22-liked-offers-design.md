# Liked Offers — Design

- **Date:** 2026-09-22
- **Status:** Approved (pending user review after writing)
- **Scope:** Backend-only. No web/frontend surface in this iteration.

## Goal

Allow offers discovered by Shargain to be marked as **liked** from a Telegram
channel (and, in the future, from a web interface). Likes group under the
same scraping target automatically via the offer's existing target
relationship knowledge chain, are attributable to `who` liked them, and are
visible in the backend admin.

## Non-Goal

- No dashboard/frontend UI for likes.
- No Telegram `username` / account resolution guarantee — a liker may or may
  not map to a Shargain account.
- No per-user reaction-to-offer button mappings (no new `message_id → offers`
  table rails. Identity is channel-agnostic.

## Context

Offers are scraped and grouped under a `ScrappingTarget` (via `Offer.target`).
New offers are sent to a Telegram chat as notification cards
(`NewOfferNotificationService`). A card is a plain text message containing one
or more offer URLs (batched into a single message when length allows, and
sent as single messages **with a location pin** when coordinates are present).

Shargain accounts and Telegram accounts are **not** guaranteed to be linked:
the `/configure` flow exists but is optional, so the bot cannot always resolve
a reacting Telegram user to a Shargain account.

## Decisions

| Question | Decision |
| --- | --- |
| Like trigger | Telegram **reaction with the ❤️ (heart) emoji** on the offer notification message |
| Identity of liker | Channel-agnostic. Store either an authenticated account (**account FK**, for future web use) or a free-form identity **label string** (for Telegram, this is the liker's Telegram user id as a string) |
| Reaction on a non-offer message | Silent no-op |
| Heart on non-card offer sent as single with-pin | Still likable (reaction parsed via message text URLs) |
| Unreact (remove ❤️) | Deletes the like(s) — like is a toggle |
| Repeated heart on already-liked offer | No-op (idempotent via unique constraints) |
| Batched multi-offer card, single ❤️ | Likes **all** offers in that card (one row per offer) |
| Notification config with pinned/waypoint pattern (exact map) | Like at message level (no `waypoints[]`) |
| Admin surface | `OfferLike` full CRUD admin page; **no inline on `Offer`** |
| Web "allow adding liked offer" in admin | Supported: standard Django add view (pick offer + label), plus full change/delete |

## Data Model

New app `shargain/offers/models.py` addition (no new app, no channel-specific
field names).

```python
class OfferLike(TimeStampedModel):
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name=_("Offer"),
    )
    # Authenticated surface (future web). Either this or liker_label is set.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="offer_likes",
        null=True,
        blank=True,
        verbose_name=_("Owner"),
    )
    # Anonymous surface (e.g. Telegram). Free-form identity label string.
    liker_label = models.CharField(_("Liker label"), max_length=255, blank=True)

    class Meta:
        ordering = ["offer_id", "pk"]
        verbose_name = _("Offer like")
        verbose_name_plural = _("Offer likes")
        constraints = [
            # Exactly one identity source: an account or a label string.
            models.CheckConstraint(
                check=Q(owner__isnull=False) | ~Q(liker_label=""),
                name="offer_like_has_identity",
            ),
            # Idempotent per (offer, account).
            models.UniqueConstraint(
                fields=["offer", "owner"],
                name="uniq_offer_like_owner",
                condition=Q(owner__isnull=False),
            ),
            # Idempotent per (offer, label).
            models.UniqueConstraint(
                fields=["offer", "liker_label"],
                name="uniq_offer_like_label",
                condition=~Q(liker_label=""),
            ),
        ]
```

### Rationale

- **Channel-agnostic identity.** `liker_label` is a free-form string, not a
  `telegram_id` FK and not a `username str` — so the same model supports
  Telegram reactions (label = the liker's Telegram user id as a string) and
  future web likes (label = a display label) with zero schema change.
  `owner` covers the case where a real, authenticated account exists (future
  web dashboard with a real user).
- **Grouping under a scraping target is free.** `Offer.target` already points
  at the `ScrappingTarget`, so likes are grouped under the correct target
  without an extra column. A "liked offers for target T" query is
  `OfferLike.objects.filter(offer__target=T)`.
- **Batched cards, split into rows.** A single ❤️ on a multi-offer card
  creates one `OfferLike` row **per offer** in that card flagged the same
  liker label, so each like groups under its correct target and is
  deduplicated individually.
- **Toggle-safe (constraints enforce clean history).** Unreact deletes all
  like rows for that liker + those offers; the partial unique constraints make
  repeated hearts / re-hearts idempotent.

### Telegram identity format

For Telegram-originated likes, the stored `liker_label` is the liker's
**Telegram user id** as a string (e.g. `"123456789"`). User ids are stable and
never collide, unlike usernames that can be renamed or absentheicker's identity
is channel-agnostic.

## Telegram Wiring

In `shargain/telegram/bot.py`:

1. Require `message_reaction` updates:
   `TelegramBot.get_bot().set_webhook(url, allowed_updates=[..., "message_reaction"])`.
2. Register a message-reaction handler:

```python
@TelegramBot.get_bot().message_reaction_handler(func=lambda _: True)
def handle_like_reaction(reaction_update: MessageReactionUpdated):
    # If ❤️ is newly present -> like all offers in that message.
    # If ❤️ was just removed -> unlike those offers.
    # Non-offer messages (menu/list/delete prompt) -> silent no-op.
```

### Reaction → offers mapping

On a reaction, the handler:

1. Fetches the reacted message by `chat_id + message_id`
   (`bot.get_message`), reading the offer URLs directly from the message text.
2. Resolves those URLs to `Offer` rows (match on `offer.url`).
3. Toggles: on heart → `get_or_create` an `OfferLike` per offer with
   `liker_label = str(reaction_user id)`; on unheart → delete the matching
   `OfferLike` rows.
4. If the message contains **no** offer URLs (e.g. a menu/list/delete-prompt
   card), it is a **silent no-op**.

All other reactions (👎, 👍, 😄, …) are ignored — only ❤️ counts as a like.

## Admin Surface

`shargain/offers/admin.py`:

- Register `OfferLike` with full Django CRUD (add / change / delete), so web
  "add liked offer" works via the standard add form.
  `list_display = (offer, liker_label, owner, created_at)`,
  `list_filter = ("offer__target",)`, `search_fields = ("offer__url",
  "offer__title", "liker_label")`.
- No inline on `Offer`, and no Offer admin modifications.

## Edge Cases

| Case | Behavior |
| --- | --- |
| Heart on batch card with many offers | One `OfferLike` per offer, grouped under each offer's target |
| Heart on single with-pin offer (coordinates) | Liked (parsed from message text URLs) |
| Heart on menu/list/delete message | Silent no-op |
| Unheart (remove ❤️) | Deletes the likes for that liker + offers |
| Repeat heart on already-liked offer | No-op (unique constraints) |
| Heart on a message that's since been re-sent/edited | Heart re-parses current message text; URLs de-duplicated via constraints |
| Reaction from a second user | Separate `OfferLike` row (distinct `liker_label`), no overwrite |

## Error Handling

- Any Telegram API failure (message fetch, chat id unknown) is caught by the
  existing bot exception middleware logging; likes simply don't record and a
  warning is emitted. No crash, no user-visible error reply (matches the
  "silent no-op" contract for non-sensical reactions).
- Reaction identity that cannot be resolved still records a `liker_label`
  fallback (chat id string), never blocking the like.

## Testing

Django tests (`shargain/offers/tests/...`), using factories:

- `OfferLike` model: identity check constraint (allows owner, allows
  `liker_label`, rejects neither), unique constraints (dedup per offer+label,
  per offer+owner), target grouping free via `offer.target`.
- Handler-level: reaction on an offer card creates one row per offer with
  correct `liker_label`; unreact deletes them idempotently; reaction on a
  menu/list message is a silent no-op (no rows, no side-effects); only ❤️
  counts, other emojis ignored.
- Admin: `OfferLikeAdmin` supports add/change/delete; no dependency on an
  `Offer` inline.

## Out of Scope / Future Work

- Web/dashboard UI for liking or viewing liked offers.
- Telegram username parsing fallback beyond user-id identity.
- Reactions on message formats that don't embed URLs (parse-only cards).
- Notification tidying / "unlike" across renamed usernames.

## Open Items (deferred intentionally)

None for MVP. Liked-offer counts, per-user "liked by me while logged in", and
any dashboard views are follow-ups, not part of this spec.
</content>
