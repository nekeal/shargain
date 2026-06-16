## Context

The frontend dashboard currently assumes a single target per user. The query `get_target_by_user` returns the most recent target, and the dashboard renders its URLs, filters, and settings directly. There is no endpoint to discover other targets, and no UI to switch between them.

Users with multiple targets (assigned via Django admin) have no way to manage them. This design adds a lightweight target list endpoint and a conditional target selector in the frontend.

## Goals / Non-Goals

**Goals:**
- Expose a lightweight list endpoint (`GET /api/public/targets`) returning all user targets.
- Show a target selector on the dashboard when the user has >1 target.
- Keep single-target flow unchanged (no selector, no extra clicks).
- All existing dashboard components (MonitoredWebsites, MonitorSettings, DashboardSidebar) work unchanged once a target is selected.
- Persist the last selected target in localStorage so it survives page reloads.
- Keep the mount architecture simple and unified so the resolution strategy can be swapped later without restructuring.

**Non-Goals:**
- Target creation — still Django-admin only.
- Target deletion from the frontend — out of scope.
- Multi-target batch operations — each target remains independently managed.

## Decisions

### 1. List endpoint returns summary only (no URLs)
- **Why:** The full target response includes all URLs, filters, waypoints — heavy data. The list is for discovery/selection only, so send a lightweight payload.
- **Schema:** `TargetSummaryResponse` with fields: id, name, is_active, enable_notifications, url_count.
- **Query:** Reuse existing `list_targets` from `shargain/offers/application/queries/list_targets.py` — it returns `TargetDto` without URLs. Add `url_count` to the DTO.

### 2. Frontend: localStorage-driven with my-target fallback (Option C)
- **Mount flow (all three fetches run in parallel):**

```
Dashboard mount
  storedId = localStorage('selectedTargetId')

  Parallel:
    ├── GET /targets                  (list — validate + count)
    ├── GET /targets/{storedId}      (if storedId exists)
    └── GET /targets/my-target       (default fallback — as today)

  Once list resolves:

    storedId exists AND in list:
      → render target from GET /targets/{storedId}
      → selector available if list.length > 1

    storedId exists AND NOT in list:
      → render my-target (already loaded)
      → clear stale storedId from localStorage

    no storedId AND list.length > 1:
      → render my-target (already loaded)
      → show selector

    no storedId AND list.length === 1:
      → render my-target (already loaded)
      → no selector (same as today)
```

- **Loading UX:** Show the existing skeleton — one smooth resolve. No visible swap because `my-target` is always loading in parallel. If the stored target resolves first, it replaces the skeleton. If my-target resolves first while waiting for the list, still no swap — the stored target fetch was already initiated.
- **Why my-target is always fetched:** It's the authoritative fallback. No need for extra logic to pick "first from list" — the backend already defines the default ordering.
- **Simplicity constraint:** The mount resolution logic lives in a single hook (`useResolveTarget` or similar) that returns `{ target, isMultiTarget, isLoading }`. The rest of the dashboard doesn't care about localStorage, list length, or fallback strategy — it just receives a target. This makes it trivial to change the resolution strategy later (e.g., remove localStorage, use user preference from backend, always show selector).

### 3. Mutations adapt to dynamic target ID
- **Why:** Currently mutations like `useAddUrlMutation`, `useRemoveUrlMutation` are instantiated with `offerMonitor.id` from the parent. With dynamic target selection, target ID comes from state.
- **Approach:** Keep mutation hooks accepting targetId as parameter (already they do). The parent component provides the selected target's ID.
- **Query key structure:** Parameterized `['target', targetId]`. Mutations invalidate by target ID.

### 4. SDK regeneration
- **Why:** The frontend uses an auto-generated SDK (`frontend/src/lib/api/sdk.gen.ts`). The new endpoint needs to be included. Regenerate after adding the endpoint.
- **Tooling:** Check existing generation command in package.json.

### 5. localStorage — required, not optional
- Store key `shargain_selected_target_id` on every selector change.
- On mount, read it eagerly (before any fetch) to drive the parallel fetch strategy.
- If stored ID is stale (target deleted in admin), clear it and fall through to my-target.
- No expiry — targets persist indefinitely unless explicitly removed.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Three parallel fetches on dashboard mount. | Two of them (my-target + stored target by ID) are lightweight fetches with no URL expansion. The list is also lightweight (summary only). In practice the server returns all three in one connection. Worth measuring but unlikely to be an issue. |
| Stored target ID deleted in admin → 404 on the parallel fetch. | Handle 404 gracefully: ignore the stored target result, let my-target be the render value, clear stale localStorage. |
| localStorage cleared by user or browser. | Falls through to my-target path. No data loss, just one extra reload's worth of "wrong default." |
| Existing mutations invalidate `'myTarget'` which no longer matches the parameterized key. | Migrate all mutation `onSuccess` handlers to invalidate `['target', targetId]`. Single-target and multi-target paths use the same key shape. |
