# Shargain — Multi-Channel Notifications

## What This Is

A feature enhancement to Shargain (a deal/offer scraping and notification system) that allows users to configure multiple notification channels per scraping target. Currently limited to one notification config per target, this change enables sending alerts to Telegram and webhooks simultaneously when new offers are discovered.

## Core Value

**Users can receive offer notifications on all their preferred channels from a single scraping target.**

If everything else fails, this must work: when a target finds new offers, all configured channels get notified.

## Requirements

### Validated

<!-- Existing capabilities inferred from codebase -->

- ✓ Scraping targets with grouped URLs — existing
- ✓ Telegram notifications for new offers — existing
- ✓ Per-URL filtering before notification — existing
- ✓ Enable/disable notifications per target — existing
- ✓ Notification config management via API — existing

### Active

<!-- New capabilities for this milestone -->

- [ ] Associate multiple notification channels with a single scraping target
- [ ] Polymorphic channel interface — each channel type (Telegram, Webhook) implements common send behavior
- [ ] All configured channels receive same notifications (no per-channel filtering)
- [ ] API endpoints to manage channel associations (add/remove channels from target)
- [ ] Frontend UI to select multiple channels per target
- [ ] Add Webhook channel type for extensibility

### Out of Scope

- Discord integration — broken, not fixing in this milestone
- Per-channel filtering rules — all channels get same notifications, simplifies UX
- Channel-specific message formatting — use same format across all channels for now
- Notification delivery confirmation/retry — future enhancement
- Rate limiting per channel — defer unless issues arise

## Context

**Existing notification flow:**
1. `OfferBatchCreateService._notify()` checks `scrapping_target.notification_config` (singular)
2. Applies per-URL filters via `OfferFilterService`
3. Calls `NewOfferNotificationService(filtered_offers, scrapping_target).run()`
4. Service dispatches to configured channel (Telegram or Discord webhook)

**Current limitation:** `ScrappingTarget.notification_config` is a single foreign key, limiting to one channel per target.

**Architecture patterns in use:**
- Command/Query separation in application layer
- Service classes with `run()` method
- DTOs for API responses (Pydantic models)
- Django Ninja for public API
- React + TanStack Query frontend

**Relevant files:**
- `shargain/offers/services/batch_create.py` — triggers notifications
- `shargain/notifications/services/notifications.py` — `NewOfferNotificationService`
- `shargain/notifications/senders.py` — channel-specific send logic
- `shargain/notifications/models.py` — `NotificationConfig` model
- `shargain/offers/models.py` — `ScrappingTarget` model

## Constraints

- **Tech stack**: Must use existing Django/Ninja backend and React frontend
- **Backwards compatibility**: Existing single-channel configs should continue to work
- **Database**: PostgreSQL — can use M2M relationships
- **API style**: Follow existing command/query patterns in application layer

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Polymorphic channel interface | Each channel type handles its own sending logic while sharing common interface | — Pending |
| M2M relationship for target→channels | Simpler than intermediate table with extra fields since all channels get same notifications | — Pending |
| Same notifications to all channels | Simplifies UX, avoids complex per-channel filter configuration | — Pending |

---
*Last updated: 2026-01-24 after initialization*
