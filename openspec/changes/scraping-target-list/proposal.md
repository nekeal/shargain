## Why

Users with multiple scraping targets (configured via Django admin) have no way to see or switch between them in the frontend. The dashboard currently assumes a single target per user — it loads one implicit target and never reveals that others exist.

## What Changes

**Backend — New endpoint:**
- `GET /api/public/targets` — returns a lightweight list of all scraping targets belonging to the authenticated user (id, name, is_active, enable_notifications, url count). No URLs, no deep data.

**Frontend — Target selection:**
- The dashboard entry point checks how many targets the user has.
- If 1 target: current behavior unchanged (auto-select, no list visible).
- If >1 target: show a target list / selector before the current dashboard content.
- Selecting a target loads its full data (URLs, filters, settings) and displays the existing dashboard UI scoped to that target.
- Optional enhancement: persist the selected target ID in `localStorage` so the user's choice survives page reloads.

**No changes to:**
- Target creation (still Django-admin only, out of scope).
- DRF batch-create API or external scraper integration.
- Per-target quota display — already works per-target-id.

## Capabilities

### New Capabilities
- `target-list`: Listing all scraping targets for the authenticated user, returning summary data (no URLs).

### Modified Capabilities
*(None — no existing capability specs to update.)*

## Impact

| Area | Impact |
|------|--------|
| **API** | New `GET /api/public/targets` endpoint. Lightweight response schema (no URL list). |
| **Application layer** | `list_targets` query already exists in `shargain/offers/application/queries/list_targets.py`. Wrap it in a Ninja endpoint. |
| **Frontend components** | `dashboard.tsx` route entry point — add target-count check + optional selector. `MonitoredWebsites`, `MonitorSettings`, `DashboardSidebar` — receive selected target instead of hardcoded single target. New `TargetSelector` component (shown only when >1 target). |
| **Frontend data fetching** | New query hook `useMyTargets()` for list. Existing `useGetMyTarget()` may need to become `useGetTarget(id)` or adapt. Mutations invalidate the specific target key, not the generic `'myTarget'` key. |
| **API SDK** | Regenerate from OpenAPI spec to pick up new endpoint. |
| **localStorage** | Optional: store `selectedTargetId` key for persistence. |
