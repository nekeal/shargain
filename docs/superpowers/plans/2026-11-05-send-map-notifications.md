# Send Map Notifications Toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a per-URL `send_map_in_notifications` toggle (default `True`) that disables the Telegram location pin while keeping map link, location name and waypoint distances, and restores normal notification batching.

**Architecture:** The flag lives on `ScrapingUrl`, flows through DTO and Ninja API into `NotificationMessageContext.send_map`. `NewOfferNotificationService.run()` splits an offer into its own card + pin only when `coordinates and send_map`; coordinates stay in the context so distances still render. Frontend adds a nested switch under the existing location toggle.

**Tech Stack:** Django, Django Ninja, pytest, React, TanStack Query, Vitest, i18next, `@hey-api/openapi-ts`.

**Spec:** Decisions from the planning conversation (no separate spec file).

## Global Constraints

- New field `send_map_in_notifications`, `default=True`; no data migration.
- Pin is sent only when `show_location_map_in_notifications=True` and coordinates exist and `send_map=True`.
- Keep `coordinates` in the context regardless of `send_map` (distances depend on them).
- PL label: `Wysyłaj mapę w powiadomieniach`; EN label: `Send map in notifications`.
- PL description: `Dodaje osobną wiadomość z lokalizacją oferty na mapie`; EN description: `Adds a separate message with the offer's location on the map.`
- PL and EN translations land in the same commit.
- Do not add tests for plain field defaults or per-field setters; test observable behaviour and contracts.
- TDD: failing test first, then minimal implementation, then green suite, then commit.

## Review Focus

1. Pin off + OLX offer with coordinates: no `send_location`, offer joins the batch, map link and distances remain.
2. Pin on + coordinates: separate card + pin, map link still present in the card.
3. `show_location_map=False` + `send_map=True`: no location block, no pin, no errors.
4. PATCH without the field leaves the stored value unchanged; migrated rows keep `True`.
5. Frontend: location master off hides the map switch; save sends `sendMapInNotifications`; missing field in an API response behaves as `True`.

---

### Task 1: Model, migration and application layer

**Files:**
- Modify: `shargain/offers/models.py:68-79`
- Create: `shargain/offers/migrations/0024_scrapingurl_send_map_in_notifications.py`
- Modify: `shargain/offers/application/dto.py:21-48`
- Modify: `shargain/offers/application/commands/add_scraping_url.py:11-43`
- Modify: `shargain/offers/application/commands/update_scraping_url.py:13-41`
- Test: `shargain/offers/tests/application/commands/test_add_scraping_url.py`
- Test: `shargain/offers/tests/application/commands/test_update_scraping_url.py`

**Interfaces:**
- Produces: `ScrapingUrl.send_map_in_notifications: bool`
- Produces: `ScrapingUrlDTO.send_map_in_notifications: bool = True`
- Produces: `add_scraping_url(..., send_map_in_notifications: bool = True)`
- Produces: `update_scraping_url(..., send_map_in_notifications: bool | None = None)`

- [ ] **Step 1: Write failing tests**

Add to `TestAddScrapingUrl`:

```python
def test_add_scraping_url_with_send_map_disabled(self, scraping_target):
    actor = Actor(user_id=scraping_target.owner_id)

    result_dto = add_scraping_url(
        actor=actor, target_id=scraping_target.id, url="https://example.com", send_map_in_notifications=False
    )

    assert result_dto.send_map_in_notifications is False
```

Add to `TestUpdateScrapingUrl`:

```python
def test_update_scraping_url_send_map_succeeds(self, scraping_target):
    scraping_url = ScrapingUrlFactory(scraping_target=scraping_target, send_map_in_notifications=True)
    actor = Actor(user_id=scraping_target.owner_id)

    result_dto = update_scraping_url(actor=actor, url_id=scraping_url.id, send_map_in_notifications=False)

    assert result_dto.send_map_in_notifications is False


def test_update_scraping_url_preserves_send_map_when_omitted(self, scraping_target):
    scraping_url = ScrapingUrlFactory(scraping_target=scraping_target, send_map_in_notifications=False)
    actor = Actor(user_id=scraping_target.owner_id)

    result_dto = update_scraping_url(actor=actor, url_id=scraping_url.id, name="New name")

    assert result_dto.send_map_in_notifications is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest shargain/offers/tests/application/commands/test_add_scraping_url.py shargain/offers/tests/application/commands/test_update_scraping_url.py -v`
Expected: FAIL — unexpected keyword argument `send_map_in_notifications` / missing attribute.

- [ ] **Step 3: Implement the flag**

Add to `ScrapingUrl` after `show_location_map_in_notifications`:

```python
send_map_in_notifications = models.BooleanField(
    _("Send map in notifications"),
    help_text=_("If True, a separate Telegram message with the offer location on a map is sent."),
    default=True,
)
```

Run: `uv run python manage.py makemigrations offers -n scrapingurl_send_map_in_notifications`

Add `send_map_in_notifications: bool = True` to `ScrapingUrlDTO` and map it in `from_orm`.

Add the parameter and pass-through to `add_scraping_url`, and the `None`-guarded update block to `update_scraping_url`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest shargain/offers/tests/application/commands -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add shargain/offers/models.py shargain/offers/migrations/0024_scrapingurl_send_map_in_notifications.py shargain/offers/application/dto.py shargain/offers/application/commands/add_scraping_url.py shargain/offers/application/commands/update_scraping_url.py shargain/offers/tests/application/commands
git commit -m "feat: add send map flag to scraping url"
```

---

### Task 2: Public API

**Files:**
- Modify: `shargain/public_api/api.py:183-193`
- Modify: `shargain/public_api/api.py:348-361`
- Modify: `shargain/public_api/api.py:379-390`
- Modify: `shargain/public_api/api.py:460-465`
- Test: `shargain/public_api/tests/test_update_scraping_url_endpoint.py`

**Interfaces:**
- Consumes: Task 1 command parameters.
- Produces: JSON alias `sendMapInNotifications` on request and response schemas.

- [ ] **Step 1: Write the failing test**

```python
def test_updates_send_map_flag(self):
    user = UserFactory()
    target = ScrappingTargetFactory(owner=user)
    url = ScrapingUrlFactory(scraping_target=target, send_map_in_notifications=True)

    client = Client()
    client.force_login(user)
    response = client.patch(
        f"/api/public/targets/{target.id}/urls/{url.id}",
        data={"sendMapInNotifications": False},
        content_type="application/json",
    )

    assert response.status_code == 200
    url.refresh_from_db()
    assert url.send_map_in_notifications is False
    assert response.json()["sendMapInNotifications"] is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest shargain/public_api/tests/test_update_scraping_url_endpoint.py::TestUpdateScrapingUrlEndpoint::test_updates_send_map_flag -v`
Expected: FAIL.

- [ ] **Step 3: Implement schemas and pass-through**

- `ScrapingUrlResponse`: `send_map_in_notifications: bool = True`
- `AddUrlRequest`: `send_map_in_notifications: bool = True`
- `UpdateScrapingUrlRequest`: `send_map_in_notifications: bool | None = None`
- Pass `send_map_in_notifications=payload.send_map_in_notifications` in both endpoint handlers.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest shargain/public_api/tests -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add shargain/public_api/api.py shargain/public_api/tests/test_update_scraping_url_endpoint.py
git commit -m "feat: expose send map flag in public api"
```

---

### Task 3: Notification service logic

**Files:**
- Modify: `shargain/notifications/services/notifications.py:10-18`
- Modify: `shargain/notifications/services/notifications.py:61-68`
- Test: `shargain/notifications/tests/services/test_notifications.py`

**Interfaces:**
- Produces: `NotificationMessageContext.send_map: bool = True`

- [ ] **Step 1: Write the failing test**

```python
def test_send_map_disabled_batches_offers_with_coordinates(self):
    first = NotificationMessageContext(
        offer=OfferFactory.build(),
        coordinates=Coordinates(lat=52.1, lon=21.1),
        map_url="https://maps.google.com/?q=52.1,21.1",
        distances=[("Metro Centrum", 1.2)],
        send_map=False,
    )
    second = NotificationMessageContext(
        offer=OfferFactory.build(),
        coordinates=Coordinates(lat=52.2, lon=21.2),
        map_url="https://maps.google.com/?q=52.2,21.2",
        send_map=False,
    )
    service = self._make_service([first, second])

    service.run()

    self.sender_instance.send_with_pin.assert_not_called()
    self.sender_instance.send.assert_called_once()
    message = self.sender_instance.send.call_args.args[0]
    assert first.offer.title in message
    assert second.offer.title in message
    assert "maps.google.com" in message
    assert "1.2 km from Metro Centrum" in message
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest shargain/notifications/tests/services/test_notifications.py::TestRunPinSplitting::test_send_map_disabled_batches_offers_with_coordinates -v`
Expected: FAIL — `send_map` is not a valid argument.

- [ ] **Step 3: Implement**

Add `send_map: bool = True` to `NotificationMessageContext` and change `run()`:

```python
if context.coordinates and context.send_map:
    self._send_single_with_pin(context)
    continue
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest shargain/notifications/tests/services -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add shargain/notifications/services/notifications.py shargain/notifications/tests/services/test_notifications.py
git commit -m "feat: allow disabling map pin per notification"
```

---

### Task 4: Pass the URL flag into the notification context

**Files:**
- Modify: `shargain/offers/services/batch_create.py:184-216`
- Test: `shargain/offers/tests/services/test_batch_create.py`

**Interfaces:**
- Consumes: `ScrapingUrl.send_map_in_notifications`, `NotificationMessageContext.send_map`.

- [ ] **Step 1: Write the failing test**

```python
def test_offer_batch_create_with_send_map_disabled(self):
    notification_config = NotificationConfigFactory()
    scraping_target = ScrappingTargetFactory(notification_config=notification_config, enable_notifications=True)
    scraping_url = ScrapingUrlFactory(
        scraping_target=scraping_target,
        show_location_map_in_notifications=True,
        send_map_in_notifications=False,
        waypoints=[{"name": "Metro Centrum", "lat": 52.23, "lon": 21.00}],
    )
    offer_data = {
        "target": scraping_target.id,
        "offers": [
            {
                "url": "https://olx.pl/offer-with-coords",
                "title": "Apartment near metro",
                "list_url": scraping_url.url,
                "metadata": {
                    "extra": {
                        "map": {"lat": 52.22, "lon": 21.01},
                        "location": {"cityName": "Warsaw", "districtName": "Centrum"},
                    }
                },
            }
        ],
    }

    with patch("shargain.offers.services.batch_create.NewOfferNotificationService") as mock_notification:
        mock_notification.return_value.run.return_value = None
        service = OfferBatchCreateService(serializer_kwargs={"data": offer_data})
        service.notification_service_class = mock_notification
        service.run()

        context = mock_notification.call_args[0][0][0]
        assert context.send_map is False
        assert context.coordinates == Coordinates(lat=52.22, lon=21.01)
        assert context.distances
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest shargain/offers/tests/services/test_batch_create.py::TestOfferBatchCreateService::test_offer_batch_create_with_send_map_disabled -v`
Expected: FAIL — missing `send_map`.

- [ ] **Step 3: Implement**

In `_build_contexts`:

```python
send_map = scraping_url.send_map_in_notifications if scraping_url else True
```

Pass `send_map=send_map` to `NotificationMessageContext(...)`. Do not change coordinate or distance calculations.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest shargain/offers/tests/services/test_batch_create.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add shargain/offers/services/batch_create.py shargain/offers/tests/services/test_batch_create.py
git commit -m "feat: pass send map flag into notification context"
```

---

### Task 5: Regenerate API contract and client

**Files:**
- Modify: `frontend/openapi.json`
- Modify: `frontend/src/lib/api/types.gen.ts`, `frontend/src/lib/api/sdk.gen.ts` (generated)

- [ ] **Step 1: Regenerate `frontend/openapi.json`**

```bash
uv run python - <<'PY'
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shargain.settings.local")
django.setup()

from django.test import Client

response = Client().get("/api/public/openapi.json")
assert response.status_code == 200, response.status_code
with open("frontend/openapi.json", "wb") as f:
    f.write(response.content)
PY
```

- [ ] **Step 2: Regenerate the client**

Run: `just frontend-generate-api-client`

- [ ] **Step 3: Verify types**

Run: `grep -n "sendMapInNotifications" frontend/src/lib/api/types.gen.ts`
Expected: field present in request and response types.

- [ ] **Step 4: Commit**

```bash
git add frontend/openapi.json frontend/src/lib/api
git commit -m "chore: regenerate api client for send map flag"
```

---

### Task 6: Frontend switch, save and translations

**Files:**
- Modify: `frontend/src/components/dashboard/monitored-websites/UrlNotificationSettings.tsx:28-34, 194-272, 307-348`
- Modify: `frontend/src/components/dashboard/monitored-websites/index.tsx:200-207`
- Modify: `frontend/src/components/dashboard/monitored-websites/useMonitors.ts:91-99`
- Modify: `frontend/src/locales/pl/translation.json:266-267`
- Modify: `frontend/src/locales/en/translation.json:266-267`
- Test: `frontend/src/components/dashboard/monitored-websites/UrlNotificationSettings.test.tsx`

**Interfaces:**
- Consumes: generated `sendMapInNotifications`.
- Produces: optional prop `initialSendMap?: boolean`, default `true`.

- [ ] **Step 1: Write the two failing tests**

```tsx
it('hides send map switch when location is disabled', () => {
  renderWithProviders(
    <UrlNotificationSettings targetId={1} urlId={1} initialShowLocationMap={false} />,
  )
  fireEvent.click(screen.getByRole('button', { name: /filters.notificationSettingsExpand/ }))
  expect(screen.queryByRole('switch', { name: 'filters.sendMapInNotifications' })).not.toBeInTheDocument()
})

it('saves sendMapInNotifications false when switch is turned off', async () => {
  renderWithProviders(
    <UrlNotificationSettings
      targetId={1}
      urlId={1}
      initialShowLocationMap={true}
      initialSendMap={true}
    />,
  )
  fireEvent.click(screen.getByRole('button', { name: /filters.notificationSettingsExpand/ }))
  fireEvent.click(screen.getByRole('switch', { name: 'filters.sendMapInNotifications' }))
  fireEvent.click(screen.getByRole('button', { name: /filters.save/ }))

  await waitFor(() => {
    expect(mockMutate).toHaveBeenCalledWith(
      expect.objectContaining({ sendMapInNotifications: false }),
    )
  })
})
```

Update the existing waypoint save expectation with `sendMapInNotifications: true`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `npm --prefix frontend run test -- UrlNotificationSettings`
Expected: FAIL.

- [ ] **Step 3: Implement**

- Add `initialSendMap?: boolean`; state `sendMap` defaulting to `initialSendMap ?? true`.
- Reset `sendMap` in the existing `useEffect`.
- Include `sendMapInNotifications: sendMap` in `handleSave`.
- Include the field in `hasChanges`.
- Inside `{showLocationMap && (...)}`, before waypoints, render a `Switch` with `id="send-map-settings"`, label and description from i18n keys `filters.sendMapInNotifications` and `filters.sendMapInNotificationsDescription`.
- `index.tsx`: `initialSendMap={url.sendMapInNotifications ?? true}`.
- `useMonitors.ts`: add `sendMapInNotifications?: boolean` to the payload type.
- Add PL and EN translations in the same commit.

- [ ] **Step 4: Run tests and lint**

Run: `npm --prefix frontend run test -- UrlNotificationSettings`
Expected: PASS.

Run: `npm --prefix frontend run lint`
Expected: no errors.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/dashboard/monitored-websites frontend/src/locales/pl/translation.json frontend/src/locales/en/translation.json
git commit -m "feat: add send map toggle to url notification settings"
```

---

### Task 7: Final verification

- [ ] **Step 1: Backend checks**

Run: `uv run python manage.py makemigrations --check --dry-run`
Expected: `No changes detected`.

Run: `just test`
Expected: PASS.

Run: `just quality-check`
Expected: PASS.

- [ ] **Step 2: Frontend checks**

Run: `just frontend-test`
Expected: PASS.

Run: `just frontend-build`
Expected: PASS.

- [ ] **Step 3: Commit any verification fixes**

```bash
git add -A
git commit -m "chore: finalize send map notifications feature"
```
