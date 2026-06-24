## Why

Source-specific notification behavior is currently split between `LocationParserFactory`, hardcoded location parser classes, and the batch notification pipeline. This makes OLX and Otodom behavior harder to extend independently and keeps source-specific knowledge inside generic notification orchestration.

This change moves backend source-specific extraction and notification formatting into cohesive source plugins while keeping the existing frontend filtering and notification settings unchanged for this iteration.

## What Changes

- Introduce a backend source plugin abstraction for source-specific metadata extraction and notification line creation.
- Add a static backend plugin registry that selects the correct plugin from an offer or scraping URL using explicit URL matching logic.
- Move OLX location extraction and notification details into an OLX plugin.
- Move Otodom location extraction and notification details into an Otodom plugin.
- Keep Otomoto on a minimal fallback/no-extra-details plugin path until its metadata format is known.
- Refactor `OfferBatchCreateService._notify()` so it no longer directly imports or calls `LocationParserFactory`.
- Refactor notification rendering so source-specific lines are supplied by plugins, while the shared header remains owned by the notification service.
- Preserve existing frontend behavior: no changes to filter UI, filter fields, notification settings UI, or generated frontend API types.
- Preserve existing `ScrapingUrl.show_location_map_in_notifications` and `ScrapingUrl.waypoints` fields for this iteration.
- Do not add plugin fields to filtering in this change.

## Capabilities

### New Capabilities
- `backend-source-plugins`: Backend selection and execution of source-specific plugins for notification metadata extraction, location details, and notification lines.

### Modified Capabilities

None. No existing OpenSpec capability specs are present in this repository.

## Impact

- Affected backend code:
  - `shargain/offers/services/location_parsers.py`
  - `shargain/offers/services/batch_create.py`
  - `shargain/notifications/services/notifications.py`
  - new backend plugin modules under the offers or sources area
- Affected tests:
  - location parser tests will move or be rewritten as plugin extraction/formatting tests
  - batch notification tests should assert plugin-produced message context behavior
- Unchanged systems:
  - frontend filter UI
  - frontend notification settings UI
  - public API request/response schemas
  - scraper integration contract
  - notification filtering behavior
- Operational impact:
  - no new external services
  - no database migration required for the first iteration
  - no dynamic plugin discovery; plugins are first-party and statically registered
