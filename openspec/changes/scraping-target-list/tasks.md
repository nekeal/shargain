## 1. Backend — Add list endpoint

- [x] 1.1 Update `list_targets` DTO to include `url_count` (annotate via `ScrapingUrl` count on the target queryset)
- [x] 1.2 Add `TargetSummaryResponse` schema to `shargain/public_api/api.py` (id, name, is_active, enable_notifications, url_count)
- [x] 1.3 Add `GET /api/public/targets` endpoint in `shargain/public_api/api.py` calling `list_targets` and returning the summary list
- [x] 1.4 Add tests for the new list endpoint (happy path, empty list, auth required)
- [x] 1.5 Run backend tests: `just test`

## 2. Backend — Regenerate API SDK

- [x] 2.1 Ensure the OpenAPI schema includes the new endpoint (run dev server, check `/api/public/openapi.json`)
- [x] 2.2 Regenerate the frontend SDK: find the generation command (likely `npm --prefix frontend run generate-api` or similar in `package.json`)
- [x] 2.3 Verify `sdk.gen.ts` includes the new `getTargets` / `listTargets` function

## 3. Frontend — Data fetching layer

- [x] 3.1 Create `useGetTargets()` hook (calls new list endpoint, returns `TargetSummaryResponse[]`)
- [x] 3.2 Update `useGetMyTarget()` to use parameterized query key `['target', 'my']` instead of `'myTarget'`
- [x] 3.3 Add `useGetTarget(targetId)` hook (calls existing `GET /targets/{targetId}`)
- [x] 3.4 Update all mutation hooks (`useAddUrlMutation`, `useRemoveUrlMutation`, `useToggleUrlActiveMutation`, `useUpdateUrlMutation`) to invalidate `['target']` instead of `['myTarget']`

## 4. Frontend — Dashboard layout changes

- [x] 4.1 In `dashboard.tsx`, add initial fetch of target list via `useGetTargets()`
- [x] 4.2 Add branching logic: if 1 target → load it directly (existing flow); if >1 target → show `<TargetSelector>`
- [x] 4.3 Create new `<TargetSelector>` component showing a list/selection UI for targets (name, status badge, URL count)
- [x] 4.4 On target selection, fetch full target data via `GET /targets/{id}` and render existing dashboard components scoped to that target
- [x] 4.5 Add loading/error/empty states for the target list

## 5. Frontend — Optional localStorage persistence

- [x] 5.1 On target selection, store `shargain_selected_target_id` in localStorage
- [x] 5.2 On dashboard mount, check localStorage for stored ID; if it exists and is in the target list, auto-select that target
- [x] 5.3 Handle edge case: stored ID no longer exists in the list → fall back to first target

## 6. Quality & Polish

- [x] 6.1 Add i18n translations for new UI strings (all locale files)
- [x] 6.2 Run frontend tests: `npm --prefix frontend run test`
- [x] 6.3 Run frontend lint: `npm --prefix frontend run lint`
- [x] 6.4 Run backend quality: `just quality-check`
- [x] 6.5 Manual smoke test: single-target flow unchanged, multi-target flow works
