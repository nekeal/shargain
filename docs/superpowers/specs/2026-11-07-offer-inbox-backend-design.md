# Offer Inbox — Backend Design

- **Date:** 2026-11-07
- **Status:** Draft — pending user approval
- **Scope:** Backend only. The web inbox UI, embedded map, and i18n are a separate frontend iteration.
- **Supersedes:** the anonymous-like part of `2026-09-22-liked-offers-design.md`. `OfferLike` is removed.

## Why

Today the user reads scraped offers in Telegram. Each notification contains offer details,
a link to the source, and often a Google Maps link. Checking locations one by one is slow,
and Telegram's implicit "seen" state cannot be undone after an accidental scroll.

This feature replaces that browsing workflow with a per-user, per-target offer inbox in
the web app. It keeps the useful parts of the Telegram feed (offers arrive automatically,
newest items are visible) and adds explicit state:

- **liked** — a shortlist of interesting offers, shareable with the future web UI;
- **seen / unseen** — explicit, reversible, and never changed by scrolling;
- **location inline** — normalized location data returned with each offer so the frontend
  can render a map without sending the user to Google Maps.

The inbox is the primary place to triage offers. Telegram remains the delivery channel.

## Goals

1. List offers for one scraping target owned by the authenticated user.
2. Support the inbox tabs `all`, `liked`, `unseen` through composable filter parameters.
3. Default to oldest-first so the inbox behaves like a queue; allow newest-first.
4. Mark an offer seen only on an explicit user action; allow marking it unseen again.
5. Like/unlike an offer per account, idempotently.
6. Return enough location data for the frontend to render a map inline.
7. Show only offers that passed the scraping URL's notification filters at ingest time.
8. Keep the backend contract ready for the generated TypeScript client.

## Non-goals

- Frontend routes, components, embedded map, i18n.
- Notes on offers (roadmap; the state table is designed to accept a `notes` column later).
- Location-based filtering or distance sorting.
- A combined inbox across all of a user's targets.
- Mark-all-seen or bulk selection.
- Real-time push/websocket updates.
- Auto-marking seen on scroll, impression, or page view.
- Syncing seen state back to Telegram.
- Supporting group chats for like attribution.
- Verifying that a user-supplied Telegram `chatid` really belongs to that account.
- Re-evaluating old offers when notification filters change.
- Changing the existing quota behaviour.

## Anti-goals

- A second source of truth for per-user offer state.
- Treating "notification delivered" as "offer passed filters". An offer can pass filters
  while notifications are disabled or the quota is exhausted.
- Hiding filter-passing offers because Telegram delivery failed.
- Recomputing notification filters on every inbox request.

## Decisions From Discovery

| Topic | Decision |
| --- | --- |
| Inbox scope | Per `ScrappingTarget`; API nested under the target. |
| Offer set | Only offers with `passed_filters = true`. |
| Filter snapshot | Persisted at ingest time; old offers keep the snapshot from when they were scraped. |
| Seen model | One record per `(user, offer)` with `seen_at` timestamp; no global watermark. |
| Seen trigger | Explicit frontend action only; scrolling never marks seen. |
| Unseen | `seen_at IS NULL` or no state row. |
| Like terminology | Keep existing domain word **liked** (`liked_at`, `/like`); do not introduce "favorite". |
| Like identity | Authenticated account only. Anonymous Telegram labels are removed. |
| Telegram identity | Resolve the user from the offer's `NotificationConfig.owner` when the chat id matches. |
| Existing anonymous likes | Dropped; not matched to accounts. |
| Endpoint style | Separate `seen` and `like` action endpoints, not a generic `PATCH /state`. |
| Default ordering | Oldest first; `newest` via query parameter. |
| State model | Single `UserOfferState` table for liked + seen (+ future notes). |

## Current State

- `Offer` belongs to `ScrappingTarget`; target ownership is `ScrappingTarget.owner`.
- Offers are created in `OfferBatchCreateService` (`shargain/offers/services/batch_create.py`).
- Notification filters live on `ScrapingUrl.filters` and are applied to `ExtractedOffer`
  objects in Python via `OfferFilterService`.
- `OfferLike` stores either an account FK (`owner`) or an anonymous label (`liker_label`).
  Telegram handlers currently use `AnonymousLiker`.
- The frontend uses the Django Ninja API at `/api/public/`; its client is generated from
  `frontend/openapi.json` via `@hey-api/openapi-ts`.
- Location data already exists in `Offer.metadata` and is parsed by
  `LocationParserFactory`; it is currently computed only while building notifications.

## Approaches Considered

### 1. Separate tables (`OfferSeen` + `OfferLike`) — rejected

Smallest diff, but leaves per-user state in two tables and makes future notes another
table. Not chosen because notes and liked/seen are all per-user, per-offer state.

### 2. Single `UserOfferState` table — chosen

One row per `(user, offer)` with nullable `seen_at` and `liked_at`. More future-proof,
one application service, and a simpler read path (one state lookup for the page).

### 3. Extend the legacy DRF `OfferViewSet` — rejected

The frontend is generated from the Ninja API. Response shapes, camelCase aliases, and
auth would diverge from the existing client.

## Data Model

### `UserOfferState`

New model in `shargain/offers/models.py`:

```python
class UserOfferState(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="offer_states",
        verbose_name=_("User"),
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="user_states",
        verbose_name=_("Offer"),
    )
    seen_at = models.DateTimeField(_("Seen at"), null=True, blank=True)
    liked_at = models.DateTimeField(_("Liked at"), null=True, blank=True)

    class Meta:
        verbose_name = _("User offer state")
        verbose_name_plural = _("User offer states")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "offer"],
                name="uniq_user_offer_state",
            ),
            models.CheckConstraint(
                condition=Q(seen_at__isnull=False) | Q(liked_at__isnull=False),
                name="user_offer_state_has_state",
            ),
        ]
```

Semantics:

- `seen_at IS NULL` means unseen. `seen_at` is the first/current explicit "seen" time.
- `liked_at IS NULL` means not liked.
- `isSeen` and `isLiked` are API fields derived from the timestamps.
- Marking seen when already seen is idempotent and keeps the existing timestamp.
- Marking unseen: if `liked_at` is already `NULL` (and, later, no notes), delete the row;
  otherwise clear `seen_at` and keep the row.
- Unliking: if `seen_at` is already `NULL` (and, later, no notes), delete the row;
  otherwise clear `liked_at` and keep the row.
- A row with only `liked_at` is valid and means "liked but unseen".
- If an offer is both liked and seen, one row holds both.

Future notes: add a nullable/blank `notes` column. The deletion rule becomes "delete only
when `seen_at`, `liked_at`, and `notes` are all empty".

### `Offer.passed_filters`

Add to `Offer`:

```python
passed_filters = models.BooleanField(
    _("Passed notification filters"),
    null=True,
    blank=True,
    default=None,
    help_text=_("Snapshot of whether the offer passed its scraping URL's notification filters at ingest."),
)
filters_evaluated_at = models.DateTimeField(
    _("Filters evaluated at"),
    null=True,
    blank=True,
    help_text=_("When the notification-filter snapshot was last written."),
)
```

- `True` — the offer passed the filters of its `ScrapingUrl` at ingest.
- `False` — the offer was scraped but did not pass the filters.
- `NULL` — never evaluated (pre-feature offer, offer created outside the batch
  pipeline, or extraction/filter-evaluation failure). An offer whose `list_url` has no
  matching `ScrapingUrl` is evaluated as passing (`True`).
- The inbox includes only `passed_filters=True`.
- Existing offers are backfilled; offers that cannot be evaluated stay `NULL` and are
  excluded until a later backfill succeeds.
- The value is a snapshot. Changing filters later does not rewrite old offers.

### Indexes

```python
# Offer.Meta.indexes
models.Index(
    fields=["target", "passed_filters", "created_at", "id"],
    name="offer_inbox_idx",
)
```

`(target, passed_filters, created_at, id)` matches the default oldest-first order and its
exact `(created_at, id)` tie-break; PostgreSQL can scan it backwards for `newest`.

The unique `(user, offer)` index on `UserOfferState` already serves both the `liked` and
`unseen` `EXISTS`/`NOT EXISTS` lookups; no additional state index is needed for the MVP.

Add `db_index=True` to `NotificationConfig.chatid` (a `notifications` migration), because
Telegram identity resolution and `/liked` filter on it.

For a large `Offer` table, create `offer_inbox_idx` with `AddIndexConcurrently` in a
non-atomic migration. The backfill without `--target-id` scans on
`passed_filters IS NULL`; that is acceptable for a one-off operational command.

## Ingest: Filter Snapshot

New service in `shargain/offers/services/filter_snapshot.py`:

```python
@dataclass(frozen=True)
class FilterSnapshotResult:
    passed: list[ExtractedOffer]
    scraping_url_by_list_url: dict[str, ScrapingUrl]


class OfferFilterSnapshotService:
    def apply(self, offers: Sequence[Offer], target: ScrappingTarget) -> FilterSnapshotResult:
        """Evaluate filters for newly created offers, persist the snapshot,
        and return the passing extracted offers for notifications."""
```

The result carries the `ExtractedOffer` objects (not just ids), because the
notification builder needs their extracted `fields`. The notification path must not
extract or filter a second time.

Behaviour:

1. Group offers by `list_url`.
2. Fetch matching `ScrapingUrl` rows for the target, deduplicated by `list_url`:
   when several rows share a `list_url`, choose the **lowest `pk`** (the same rule
   as `_record_checkins`'s `.first()`). `_notify` must use this same selection
   instead of its current last-row-wins dict.
3. Build `ExtractedOffer` objects with `OfferFieldResolver.extract`.
4. Apply `OfferFilterService(scraping_url.filters)` per group.
5. For every input offer set `passed_filters` to `True`/`False`, and set
   `filters_evaluated_at`; update in bulk.
6. If there is no matching `ScrapingUrl`, or it has no filters, the offer passes.
7. If extraction raises for an offer, or filter evaluation raises for a `list_url` group
   (unknown operator, malformed stored filter JSON), log it, leave the affected offers'
   snapshots `NULL`, omit them from `passed`, and continue. Snapshot failures must never
   abort ingest, check-in recording, or quota signals.

Wiring in `OfferBatchCreateService`:

- Run the snapshot for **newly created** offers after `create()`.
- Run it regardless of `notification_config` or `enable_notifications`; only the
  notification step is conditional.
- `_notify` receives `FilterSnapshotResult.passed` and the matching `ScrapingUrl`
  map; it no longer calls `_extract_offers` or `_filter_offers`.
- Existing offers are never re-evaluated by ingest.
- `OfferBatchCreateService` is the only creation path that writes the snapshot.
  The legacy DRF `OfferSerializer.create` path is currently broken and out of scope;
  offers created manually in Django admin stay `NULL` and are covered by the backfill
  command. Any future creation path must call the snapshot service.

Constraint: `OfferBatchCreateService.run()` currently returns early when the per-target
offer quota is reached, before creating offers. That stays unchanged. The inbox therefore
pauses when the quota is exhausted. Decoupling offer storage from the notification quota
is a separate product decision.

## Backfill

Management command in `shargain/offers/management/commands/backfill_offer_filters.py`:

```bash
python manage.py backfill_offer_filters [--target-id ID] [--batch-size 500] [--dry-run]
```

- Selects offers with `passed_filters IS NULL`.
- Evaluates them against the current matching `ScrapingUrl.filters`, using the same
  lowest-`pk` deduplication rule as ingest.
- Writes `passed_filters` and `filters_evaluated_at`.
- Logs extraction or filter-evaluation failures and leaves those offers `NULL`.
- Idempotent; can be run repeatedly.

This is a one-time operational step after deploying the model and ingest change.

## Application Layer

New module `shargain/offers/application/offer_state.py`. The API and the Telegram bot are
thin adapters; all state transitions live here.

```python
@dataclass(frozen=True)
class OfferState:
    offer_id: int
    seen_at: datetime | None
    liked_at: datetime | None

def mark_offers_seen(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]: ...
def mark_offers_unseen(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]: ...
def like_offers(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]: ...
def unlike_offers(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]: ...
def get_offer_states(actor: Actor, offer_ids: Sequence[int]) -> dict[int, OfferState]: ...
```

Rules:

- Every command runs inside `transaction.atomic()` and starts by locking the actor's user
  row (`User.objects.select_for_update().get(pk=actor.user_id)`). This serializes state
  changes per user (not across users) and removes the create/clear race.
- Set operations (`mark_offers_seen`, `like_offers`) create missing rows with
  `get_or_create` (or `bulk_create(ignore_conflicts=True)`), then update only where the
  relevant timestamp is `NULL`. They never overwrite the other timestamp.
- Clear operations (`mark_offers_unseen`, `unlike_offers`) never create rows. To respect
  the check constraint, they first delete rows where the **other** timestamp is already
  `NULL`, then clear their own timestamp on the remaining rows. They delete only the ids
  selected and validated in the same transaction.
- Both operations are idempotent: repeating them returns the current state.
- A `CheckConstraint` on `UserOfferState` requires at least one timestamp
  (`seen_at IS NOT NULL OR liked_at IS NOT NULL`). When `notes` is added, the condition
  extends to include a non-empty note.
- Every mutating function verifies the offers belong to the actor
  (`offer.target.owner_id`). Missing/foreign offers raise `OfferDoesNotExist`; the API
  maps it to 404.
- The API also scopes by `target_id`: it resolves the offer with
  `Offer.objects.get(pk=offer_id, target_id=target_id, target__owner=actor.user_id)`
  before calling the service, so an offer in another target of the same user is a 404
  through a mismatched URL.
- Multi-offer calls validate **all** ids before mutating anything; one missing or foreign
  id rejects the whole call (no partial updates).
- The bot may pass several offers at once (a batched notification card).

`get_offer_states` is a read, not a command: it filters by `user_id=actor.user_id` and
`offer_id__in=page_ids`. It does not raise for offers deleted between the list and
hydration queries; a missing row means "no state". One query per page, no N+1.

Add `OfferDoesNotExist(ApplicationException)` to
`shargain/offers/application/exceptions.py` (`code = "offer_does_not_exist"`).

Remove `shargain/offers/likes.py`, `AnonymousLiker`, `AccountLiker`, `Liker`,
`OfferLikeIdentityError`, and the `OfferLike` model. Update tests and factories.

## API

All routes are on the authenticated Ninja router (`shargain/public_api/api.py`) and use
camelCase aliases.

### List

```
GET /api/public/targets/{target_id}/offers
    ?filter=all|liked|unseen
    &ordering=oldest|newest
    &limit=20
    &offset=0
```

"all / liked / unseen" are **frontend tabs**, not backend resources. The backend
exposes one list endpoint with composable `filter` + `ordering` parameters; the frontend
composes the request, e.g. `filter=unseen&ordering=oldest` for the default inbox tab.
Because the page is filtered and ordered before pagination, this must happen server-side;
filtering an already-fetched page in the frontend would break `count` and page boundaries.

- `filter` defaults to `all`; `ordering` defaults to `oldest`.
- `oldest` sorts by `(created_at, id)` ascending; `newest` by descending.
- Only offers with `passed_filters=True` for the target are considered.
- `filter=liked`: only `UserOfferState.liked_at IS NOT NULL` for the actor.
- `filter=unseen`: no state row, or `seen_at IS NULL`, for the actor.
- Returns Ninja `LimitOffsetPagination` shape: `{ "count": N, "items": [...] }`.
- 404 when the target is not found or not owned by the actor.
- Listing **never** changes seen state.

`OfferInboxItem`:

```text
id, url, title, price, mainImageUrl, publishedAt, createdAt, closedAt, listUrl
isSeen, seenAt, isLiked, likedAt
location: { name, mapUrl, latitude, longitude, isExact } | null
```

- `mainImageUrl` is `str | None`; normalize the model's empty string to `null` in the
  response (a schema field typed `HttpUrl` would reject `""`).
- `location` is `null` when the parser finds no location. When present, all members are
  set; `latitude`/`longitude` are `null` when the source exposes no coordinates.
- `price`, `publishedAt`, `closedAt` are nullable.

Closed offers are included and expose `closedAt`; the frontend can style them. Hiding
closed offers is out of scope for MVP.

### Actions

```
POST   /api/public/targets/{target_id}/offers/{offer_id}/seen
DELETE /api/public/targets/{target_id}/offers/{offer_id}/seen
POST   /api/public/targets/{target_id}/offers/{offer_id}/like
DELETE /api/public/targets/{target_id}/offers/{offer_id}/like
```

- All return `200` with `OfferStateResponse`
  `{ offerId, isSeen, seenAt, isLiked, likedAt }`.
- Idempotent: repeating POST or DELETE returns the current state.
- 404 when the target/offer does not exist, the offer does not belong to that target, or
  the target is not owned by the actor.
- Separate action endpoints are preferred over `PATCH /state`: they express intent,
  keep the transport independent of internal columns, and each maps to one command.
  Notes will get their own endpoint later.

### Location in the inbox

`OfferInboxItem.location` is computed on read from `offer.metadata` using
`LocationParserFactory`:

- `name` — city/district/street label from the parser.
- `mapUrl` — parser's map URL. For MVP it is not centred on a waypoint; the frontend can
  still use it directly.
- `latitude`, `longitude` — when the source provides coordinates (OLX).
- `isExact` — whether the source exposes an exact pin.

This keeps parser details out of the frontend and costs a few microseconds per page item.
No database schema change is needed.

## Telegram Integration

Remove anonymous identity from the like flow. In `shargain/telegram/bot.py`:

- Scope `resolve_offers_from_message` to the chat: filter `Offer` by
  `target__notification_config__chatid=str(chat_id)` and
  `target__notification_config__owner__isnull=False`, with
  `select_related("target__notification_config")`. Without this, a URL monitored by
  another user resolves to that user's `Offer` rows too, the attribution check fails, and
  every reply-like is rejected in the multi-tenant case.
- Add a helper `resolve_user_for_offer_chat(offer, chat_id) -> int | None`:
  - `config = offer.target.notification_config`
  - return `config.owner_id` only when `config` exists, `config.owner_id` is set, and
    `str(chat_id) == config.chatid`; otherwise `None`.
- Add a helper `resolve_user_for_chat(chat_id) -> int | None` for commands without offer
  context: collect the distinct non-null owners of configs with `chatid == str(chat_id)`
  that are referenced by at least one `ScrappingTarget`. Return the single owner; return
  `None` when there are zero or more than one (ambiguous chat).
- `handle_like_reply` resolves every offer already scoped to the chat. If any offer cannot
  be attributed to the chat's owner, reject the **whole** message with an explicit error
  and change nothing; otherwise call `like_offers` / `unlike_offers` once for the batch.
  Toggle semantics are deterministic for a batch: an explicit `unlike` unlikes all; a
  `like` unlikes all only when **all** offers are already liked, otherwise it likes all.
- `/liked` calls `resolve_user_for_chat(message.chat.id)`. When resolved, list
  `UserOfferState` rows filtered explicitly by `user_id=resolved_user_id` and
  `liked_at__isnull=False`, scoped to targets whose `NotificationConfig.chatid` matches
  the chat. When the chat is ambiguous or unregistered, reply with an explicit error
  instead of listing.
- `/unlike_{offer_id}` loads the offer scoped to the chat (same filter as
  `resolve_offers_from_message`) and attributes the action through
  `resolve_user_for_offer_chat`. A missing offer or mismatched chat replies with an error.
- Existing `AnonymousLiker` imports, `liker_label`, and `OfferLike` queries are removed.
- The current bot implements likes through replies; `is_heart_reaction_added` is not
  wired. If a reaction handler is added later, it must use the same identity helper.

Caveats:

- Group chats are not supported: a reaction from any member would be attributed to the
  config owner. If group support is needed later, map `from_user.id` through
  `TelegramUser` instead.
- Messages in a chat that no longer matches the target's current `NotificationConfig`
  cannot be attributed and are rejected.
- **Known limitation:** chat-id ownership is trusted as today. `NotificationConfig.chatid`
  is user-supplied and not unique, so a malicious account could register another user's
  chat id and make `/liked` ambiguous. This is a pre-existing notification-trust issue;
  verifying chat ownership at registration (or a unique `(channel, chatid)` constraint) is
  out of scope for this feature. Scoping `resolve_user_for_chat` to configs referenced by
  targets and requiring owner agreement limits the impact, but does not eliminate it.

## Data Migration

The `offers` app currently has two sibling leaf migrations
(`0024_offerlike_...` and `0024_scrapingurl_send_map_in_notifications`). `migrate` itself
can still run, but `makemigrations` and `--check` are ambiguous and the app is not in a
clean state. This change starts with a merge migration:

1. `0025_merge_...` depending on both `0024` leaves.

Then the feature migrations:

2. Add `Offer.passed_filters` / `filters_evaluated_at` and the `offer_inbox_idx` index.
3. Create `UserOfferState` with the unique and check constraints.
4. `RunPython`:
   - For every `OfferLike` with `owner_id IS NOT NULL`, create
     `UserOfferState(user_id=owner_id, offer_id=offer_id, liked_at=created_at)`;
     ignore conflicts.
   - Iterate with `.iterator()` and `bulk_create` in batches; do not load all likes at once.
   - Do **not** copy rows with `liker_label` (anonymous likes are intentionally dropped).
5. Delete the `OfferLike` model/table.

Owner backfill is a management command, not a migration, to avoid a dependency cycle
(`notifications` already depends on `offers`, while `ScrappingTarget.owner` lives in
`offers`):

```bash
python manage.py backfill_notification_config_owners [--dry-run]
```

It sets `NotificationConfig.owner` from the attached `ScrappingTarget.owner` when all
targets sharing that config have the same non-null owner; ambiguous or ownerless configs
stay `NULL` and are logged. Without this, existing Telegram chats cannot attribute likes
even though the code is correct. The rollout must report how many configs remain without
an owner.

The forward migration is destructive for anonymous likes and cannot restore them. The
reverse migration can recreate account-based `OfferLike` rows from `liked_at`, but the
dropped anonymous rows are gone. Document this in the migration and release notes.

**Deploy safety:** do not use a rolling deploy. Old workers import `shargain.offers.likes`
and `OfferLike`, so they can write likes after the copy and then crash once the table is
dropped. Use a maintenance window: stop all application processes (workers and web),
deploy the new code and run migrations, then start them. If zero-downtime is required,
split into two releases (dual-write, then drop `OfferLike`) instead.

Remove `OfferLikeAdmin`; add `UserOfferStateAdmin` with:
`list_display = ("user", "offer", "seen_at", "liked_at", "created_at")`,
`list_filter = ("offer__target",)`, and search on offer URL/title and user email.
Make `passed_filters` and `filters_evaluated_at` read-only in `OfferAdmin` so manual edits
cannot diverge from the ingest snapshot.

## Performance

- Row volume: a `UserOfferState` row exists only after a user likes or sees an offer.
  Browsing without interaction does not create rows.
- List query: `Offer` filtered by `target_id`, `passed_filters=True`, ordered by
  `(created_at, id)`. Covered by `offer_inbox_idx`.
- `liked` filter: `EXISTS` on `UserOfferState` `(user, offer, liked_at)`, using the unique
  index.
- `unseen` filter: `NOT EXISTS` on `UserOfferState` `(user, offer, seen_at IS NOT NULL)`.
- Page hydration: one query
  `UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=page_ids)`.
- Count query for pagination is acceptable at the expected scale; use cursor pagination
  later if the inbox grows large.
- Location parsing is in-memory per page item; no extra DB query in the MVP.
- Removing `OfferLike` removes a second per-offer relation and its anonymous-label
  constraints.

## Testing

Backend tests with `pytest`:

- Model: unique `(user, offer)`; at-least-one-timestamp check constraint; timestamps
  nullable; row deletion rule.
- Application service: like/unlike and seen/unseen are idempotent; multi-offer calls;
  cross-user access is rejected; a mixed valid/foreign batch changes nothing; clearing
  both states deletes the row; clear operations never create rows; two commands for the
  same user run serialized (per-user lock).
- API: auth required; target ownership 404; offer-in-another-target 404; `all`/`liked`/
  `unseen`; ordering; pagination; `passed_filters` exclusion; nullable
  `mainImageUrl`/`location`; list does not mark seen; actions return state and 404 for
  foreign offers.
- Ingest: passing/failing filters; notifications disabled still writes the snapshot;
  no filters passes; no matching `ScrapingUrl` passes; duplicate `ScrapingUrl` rows use
  the lowest `pk` for both snapshot and notifications; extraction or filter-evaluation
  failure stays `NULL`, does not abort ingest, and is not notified; existing offers are
  not rewritten.
- Backfill command: sets flags for `NULL` offers; leaves failures `NULL`; target filter;
  dry run.
- Telegram: reply like resolves owner by chat id; offers from other users' targets with
  the same URL are not resolved; a batch with any unattributable offer is rejected
  entirely; mixed-batch toggle semantics; mismatched chat/no owner is rejected; `/liked`
  filters by the resolved `user_id` and `liked_at__isnull=False` (seen-only rows are
  excluded), rejects an ambiguous chat, and scopes to the chat's targets; no anonymous
  rows are created.
- Notifications: owner backfill sets unambiguous configs and leaves ambiguous ones null.
- Migration: account likes copied; anonymous likes dropped. `pytest` runs with
  `--nomigrations`, so extract the copy logic into a function taking the historical
  models (or add `django-test-migrations`) instead of relying on the normal test DB.
- Regenerate `frontend/openapi.json` and the TypeScript client after the API change.

## Rollout

1. Stop all application processes that import the bot/offer-like code — background
   workers and the web/webhook process (maintenance window; no rolling deploy).
2. Deploy code and run migrations (merge → feature → `OfferLike` drop).
3. Run `backfill_notification_config_owners` and report remaining null owners.
4. Run `backfill_offer_filters` for existing targets.
5. Start the application processes.
6. Regenerate `frontend/openapi.json` and `frontend/src/lib/api`.
7. Frontend inbox UI and embedded map ship separately.

Backfilled `passed_filters` values are evaluated against the filters current at backfill
time, not at original ingest time; only new offers get a true ingest-time snapshot. Say
this in the release notes.

Operational note: quota gating is unchanged. When a target's offer quota is exhausted,
new offers are not stored, so the inbox pauses along with notifications.

## Open Questions / Builder Calls

These are my calls; the builder may change them without changing the product intent:

- **Closed offers** — included in all views, exposed via `closedAt`. Hiding them is a
  later UI filter.
- **Map centring** — `mapUrl` is not centred on waypoints in the MVP; coordinates are
  returned when the source has them.
- **Notes** — no `notes` column yet; the table and delete rule are designed to accept it.
- **Quota** — unchanged; decoupling storage from notification quota is out of scope.
- **Group chats** — unsupported for like attribution.
- **Reaction handler** — not wired in the current bot; reply-based likes are the surface.
- **Offer uniqueness** — `(target, url)` is not constrained today; a create race can
  produce duplicate offers and therefore duplicate inbox rows. Deduplicating existing
  rows and adding the constraint is a separate cleanup, not part of this feature.
- **Chat-id verification** — trusting user-supplied `NotificationConfig.chatid` is a
  pre-existing limitation; see the Telegram caveat.
- **Index creation** — use `AddIndexConcurrently` for `offer_inbox_idx` if the `Offer`
  table is large; otherwise a normal migration is fine.
- **Migration test tooling** — extract the copy function and test it directly, or add
  `django-test-migrations`; the default `--nomigrations` test run does not execute it.
