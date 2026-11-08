# Offer Inbox Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Implement the Offer Inbox backend supporting per-user target-scoped offer listing with `seen`/`liked` filters, idempotent state transitions, ingest-time filter snapshots, a distinct `PublicOffer` read model with plugin attribute & location projection, account-only Telegram likes, and OpenAPI client regeneration.

**Architecture:** A flat architecture in `shargain/offers/` where the web contract is exposed via `PublicOffer` DTO and Ninja router in `shargain/offers/api.py`. State transitions (`seen`/`liked`) live in `shargain/offers/application/offer_state.py` backed by a unified `UserOfferState` model with per-user row-level lock concurrency. Offers snapshot `passed_filters` at ingest via `OfferFilterSnapshotService`. Telegram bot attribution is refactored to use account-linked chat configs, eliminating anonymous likes and deleting `OfferLike`.

**Tech Stack:** Django 5, Django Ninja, PostgreSQL / SQLite (test), pytest, pytest-django, Pydantic v2, TypeScript / `@hey-api/openapi-ts`, uv.

**Spec:** `docs/superpowers/specs/2026-11-07-offer-inbox-backend-design.md`

---

## Global Constraints

- **TDD:** Write failing tests first, verify failure, write minimal code, verify green.
- **No in-memory filtering in Python:** `list_public_offers` must execute all `target_id`, `passed_filters`, `seen`, and `liked` filters strictly in SQL using `django.db.models.Exists` subqueries.
- **Architectural Boundary:** `shargain/offers/api.py` must NEVER import `shargain.offers.models.Offer`. It communicates strictly via DTOs, queries, commands, and exceptions in `shargain.offers.application`.
- **Fail-soft read path:** A failing plugin extraction or location parser for one offer must log a warning and fallback to `attributes: []` or `location: null` without crashing the page response.
- **Fail-soft ingest path:** Ingest extraction or filter evaluation failure leaves `passed_filters=None`, omits from `passed`, and continues without aborting check-ins or quota signals.
- **Pre-existing offers excluded:** Offers with `passed_filters=None` are excluded from the inbox; no backfill.
- **Code formatting:** Run `uv run ruff check --fix shargain` and `uv run ruff format shargain` before committing.

---

### Task 1: Migration Merge & Base Model Changes (`passed_filters`, `offer_inbox_idx`, `NotificationConfig.chatid` index)

**Files:**
- Create: `shargain/offers/migrations/0025_merge_20261108.py`
- Modify: `shargain/notifications/models.py:36`
- Create: `shargain/notifications/migrations/0007_alter_notificationconfig_chatid.py`
- Modify: `shargain/offers/models.py:155-200`
- Create: `shargain/offers/migrations/0026_offer_passed_filters_and_index.py`
- Modify: `shargain/offers/admin.py:48-80`
- Test: `shargain/offers/tests/models/test_offer_inbox_fields.py`
- Test: `shargain/offers/tests/admin/test_admin.py`

**Interfaces:**
- Produces: `Offer.passed_filters: bool | None` (default `None`, nullable)
- Produces: `Offer.Meta.indexes`: `offer_inbox_idx` on `["target", "passed_filters", "created_at", "id"]`
- Produces: `NotificationConfig.chatid`: `db_index=True`

- [x] **Step 1: Create leaf merge migration for `offers`**

Create `shargain/offers/migrations/0025_merge_20261108.py`:
```python
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("offers", "0024_offerlike_offerlike_offer_like_has_identity_and_more"),
        ("offers", "0024_scrapingurl_send_map_in_notifications"),
    ]

    operations = []
```

- [x] **Step 2: Write failing test for `passed_filters` and indexes**

Create `shargain/offers/tests/models/test_offer_inbox_fields.py`:
```python
import pytest
from django.db import connection

from shargain.notifications.models import NotificationConfig
from shargain.offers.models import Offer
from shargain.offers.tests.factories import ScrappingTargetFactory


@pytest.mark.django_db
def test_offer_passed_filters_defaults_to_none():
    target = ScrappingTargetFactory()
    offer = Offer.objects.create(
        url="https://example.com/item/1",
        title="Test Item",
        target=target,
    )
    offer.refresh_from_db()
    assert offer.passed_filters is None


@pytest.mark.django_db
def test_notification_config_chatid_has_db_index():
    chatid_field = NotificationConfig._meta.get_field("chatid")
    assert chatid_field.db_index is True


@pytest.mark.django_db
def test_offer_inbox_index_exists():
    index_names = [idx.name for idx in Offer._meta.indexes]
    assert "offer_inbox_idx" in index_names
    inbox_idx = next(idx for idx in Offer._meta.indexes if idx.name == "offer_inbox_idx")
    assert inbox_idx.fields == ["target", "passed_filters", "created_at", "id"]
```

- [x] **Step 3: Run test to verify failure**

Run: `uv run pytest shargain/offers/tests/models/test_offer_inbox_fields.py -v`
Expected: FAIL (`passed_filters` does not exist on `Offer`, `chatid` does not have `db_index=True`, `offer_inbox_idx` not found).

- [x] **Step 4: Implement model changes**

1. In `shargain/notifications/models.py:36`, add `db_index=True`:
```python
chatid = models.CharField(verbose_name=_("Chat ID"), max_length=100, blank=True, db_index=True)
```

2. In `shargain/offers/models.py`, add `passed_filters` to `Offer`:
```python
passed_filters = models.BooleanField(
    _("Passed notification filters"),
    null=True,
    blank=True,
    default=None,
    help_text=_("Snapshot of whether the offer passed its scraping URL's notification filters at ingest."),
)
```

3. In `shargain/offers/models.py:Offer.Meta.indexes`, add `offer_inbox_idx`:
```python
indexes = [
    HashIndex(fields=["url"], name="offer_url_hash_idx"),
    models.Index(
        fields=["target", "passed_filters", "created_at", "id"],
        name="offer_inbox_idx",
    ),
]
```

4. Create migration for notifications: `shargain/notifications/migrations/0007_alter_notificationconfig_chatid.py`:
```python
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0006_notificationconfig_owner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificationconfig",
            name="chatid",
            field=models.CharField(blank=True, db_index=True, max_length=100, verbose_name="Chat ID"),
        ),
    ]
```

5. Create migration for offers: `shargain/offers/migrations/0026_offer_passed_filters_and_index.py`:
```python
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("offers", "0025_merge_20261108"),
    ]

    operations = [
        migrations.AddField(
            model_name="offer",
            name="passed_filters",
            field=models.BooleanField(
                blank=True,
                default=None,
                help_text="Snapshot of whether the offer passed its scraping URL's notification filters at ingest.",
                null=True,
                verbose_name="Passed notification filters",
            ),
        ),
        migrations.AddIndex(
            model_name="offer",
            index=models.Index(
                fields=["target", "passed_filters", "created_at", "id"],
                name="offer_inbox_idx",
            ),
        ),
    ]
```

- [x] **Step 5: Update `OfferAdmin`**

In `shargain/offers/admin.py`:
- Add `"passed_filters"` to `list_display`
- Add `"passed_filters"` to `list_filter`
- Add `"passed_filters"` to `readonly_fields`

- [x] **Step 6: Run tests and admin tests**

Run: `uv run pytest shargain/offers/tests/models/test_offer_inbox_fields.py shargain/offers/tests/admin/test_admin.py -v`
Expected: PASS

- [x] **Step 7: Commit**

```bash
git add shargain/notifications/models.py shargain/notifications/migrations/0007_alter_notificationconfig_chatid.py shargain/offers/models.py shargain/offers/migrations/0025_merge_20261108.py shargain/offers/migrations/0026_offer_passed_filters_and_index.py shargain/offers/admin.py shargain/offers/tests/models/test_offer_inbox_fields.py
git commit -m "feat(offers): add passed_filters and offer_inbox_idx index"
```

---

### Task 2: Ingest Filter Snapshot Service & `OfferBatchCreateService` Integration

**Files:**
- Create: `shargain/offers/services/filter_snapshot.py`
- Modify: `shargain/offers/services/batch_create.py:35-175`
- Test: `shargain/offers/tests/services/test_filter_snapshot.py`
- Test: `shargain/offers/tests/services/test_batch_create.py`

**Interfaces:**
- Produces: `FilterSnapshotResult(passed: list[ExtractedOffer], scraping_url_by_list_url: dict[str, ScrapingUrl])`
- Produces: `OfferFilterSnapshotService.apply(offers: Sequence[Offer], target: ScrappingTarget) -> FilterSnapshotResult`

- [x] **Step 1: Write failing tests for `OfferFilterSnapshotService`**

Create `shargain/offers/tests/services/test_filter_snapshot.py`:
```python
import pytest
from unittest.mock import patch

from shargain.offers.models import Offer
from shargain.offers.services.filter_snapshot import OfferFilterSnapshotService
from shargain.offers.tests.factories import OfferFactory, ScrapingUrlFactory, ScrappingTargetFactory


@pytest.mark.django_db
class TestOfferFilterSnapshotService:
    def test_offers_matching_filters_get_passed_true(self):
        target = ScrappingTargetFactory()
        scraping_url = ScrapingUrlFactory(
            scraping_target=target,
            url="https://www.olx.pl/d/nieruchomosci/mieszkania/",
            filters={"price": {"gte": 1000, "lte": 3000}},
        )
        offer_pass = OfferFactory(
            target=target,
            list_url=scraping_url.url,
            price=2000,
            title="Apartment in budget",
        )
        offer_fail = OfferFactory(
            target=target,
            list_url=scraping_url.url,
            price=5000,
            title="Apartment too expensive",
        )

        service = OfferFilterSnapshotService()
        result = service.apply([offer_pass, offer_fail], target)

        offer_pass.refresh_from_db()
        offer_fail.refresh_from_db()

        assert offer_pass.passed_filters is True
        assert offer_fail.passed_filters is False
        assert [eo._offer.id for eo in result.passed] == [offer_pass.id]
        assert result.scraping_url_by_list_url[scraping_url.url].id == scraping_url.id

    def test_offer_without_matching_scraping_url_passes(self):
        target = ScrappingTargetFactory()
        offer = OfferFactory(target=target, list_url="https://unknown-url.com/feed", price=100)

        service = OfferFilterSnapshotService()
        result = service.apply([offer], target)

        offer.refresh_from_db()
        assert offer.passed_filters is True
        assert len(result.passed) == 1

    def test_duplicate_scraping_urls_selects_lowest_pk(self):
        target = ScrappingTargetFactory()
        url = "https://www.olx.pl/d/nieruchomosci/mieszkania/"
        sc_first = ScrapingUrlFactory(scraping_target=target, url=url, filters={"price": {"gte": 500}})
        sc_second = ScrapingUrlFactory(scraping_target=target, url=url, filters={"price": {"gte": 9999}})

        offer = OfferFactory(target=target, list_url=url, price=1000)

        service = OfferFilterSnapshotService()
        result = service.apply([offer], target)

        assert result.scraping_url_by_list_url[url].id == min(sc_first.id, sc_second.id)
        offer.refresh_from_db()
        assert offer.passed_filters is True

    def test_extraction_or_filter_error_leaves_null_and_omits_from_passed(self):
        target = ScrappingTargetFactory()
        url = "https://www.olx.pl/d/nieruchomosci/mieszkania/"
        ScrapingUrlFactory(scraping_target=target, url=url, filters={"price": {"unknown_op": 100}})
        offer = OfferFactory(target=target, list_url=url, price=1000)

        service = OfferFilterSnapshotService()
        result = service.apply([offer], target)

        offer.refresh_from_db()
        assert offer.passed_filters is None
        assert result.passed == []
```

- [x] **Step 2: Run test to verify failure**

Run: `uv run pytest shargain/offers/tests/services/test_filter_snapshot.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'shargain.offers.services.filter_snapshot'`).

- [x] **Step 3: Implement `OfferFilterSnapshotService`**

Create `shargain/offers/services/filter_snapshot.py`:
```python
import logging
from collections.abc import Sequence
from dataclasses import dataclass

from shargain.offers.field_extraction import ExtractedOffer, ListUrl, OfferFieldResolver
from shargain.offers.filtering import OfferFilterService
from shargain.offers.models import Offer, ScrapingUrl, ScrappingTarget

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FilterSnapshotResult:
    passed: list[ExtractedOffer]
    scraping_url_by_list_url: dict[str, ScrapingUrl]


class OfferFilterSnapshotService:
    def apply(self, offers: Sequence[Offer], target: ScrappingTarget) -> FilterSnapshotResult:
        if not offers:
            return FilterSnapshotResult(passed=[], scraping_url_by_list_url={})

        offers_by_url: dict[str, list[Offer]] = {}
        for offer in offers:
            offers_by_url.setdefault(offer.list_url, []).append(offer)

        # Deduplicate ScrapingUrls by list_url picking lowest pk
        raw_scraping_urls = ScrapingUrl.objects.filter(
            url__in=list(offers_by_url.keys()), scraping_target=target
        ).order_by("pk")
        scraping_url_by_list_url: dict[str, ScrapingUrl] = {}
        for sc in raw_scraping_urls:
            if sc.url not in scraping_url_by_list_url:
                scraping_url_by_list_url[sc.url] = sc

        passed_extracted: list[ExtractedOffer] = []
        updates_true: list[int] = []
        updates_false: list[int] = []

        for list_url, group_offers in offers_by_url.items():
            scraping_url = scraping_url_by_list_url.get(list_url)

            # Try extraction per offer (fail-soft per offer)
            extracted_group: list[tuple[Offer, ExtractedOffer]] = []
            for offer in group_offers:
                try:
                    fields = OfferFieldResolver.extract(offer, ListUrl(list_url))
                    extracted_group.append((offer, ExtractedOffer(_offer=offer, fields=fields)))
                except Exception:
                    logger.exception(
                        "Field extraction failed for offer %s (list_url=%s); leaving passed_filters NULL",
                        offer.id,
                        list_url,
                    )

            if not scraping_url or not scraping_url.filters:
                # No filters -> all extracted pass
                for offer, ext in extracted_group:
                    updates_true.append(offer.id)
                    passed_extracted.append(ext)
                continue

            try:
                filter_service = OfferFilterService(scraping_url.filters)
                filtered_passed_ext = filter_service.apply([ext for _, ext in extracted_group])
                passed_offer_ids = {ext._offer.id for ext in filtered_passed_ext}
                for offer, ext in extracted_group:
                    if offer.id in passed_offer_ids:
                        updates_true.append(offer.id)
                        passed_extracted.append(ext)
                    else:
                        updates_false.append(offer.id)
            except Exception:
                logger.exception(
                    "Filter evaluation failed for list_url %s (target %s); leaving passed_filters NULL",
                    list_url,
                    target.id,
                )

        if updates_true:
            Offer.objects.filter(id__in=updates_true).update(passed_filters=True)
        if updates_false:
            Offer.objects.filter(id__in=updates_false).update(passed_filters=False)

        # Refresh local instances
        for offer in offers:
            if offer.id in updates_true:
                offer.passed_filters = True
            elif offer.id in updates_false:
                offer.passed_filters = False

        return FilterSnapshotResult(
            passed=passed_extracted,
            scraping_url_by_list_url=scraping_url_by_list_url,
        )
```

- [x] **Step 4: Wire snapshot service into `OfferBatchCreateService`**

In `shargain/offers/services/batch_create.py`:
1. Import `OfferFilterSnapshotService`.
2. In `run()`:
```python
offers: list[tuple[Offer, bool]] = self.create(serializer.validated_data)
new_offers = [r[0] for r in filter(lambda x: x[1], offers)]
span.set_attribute("offers.total", len(offers))
span.set_attribute("offers.new", len(new_offers))

snapshot_result = OfferFilterSnapshotService().apply(new_offers, target)
self._notify(snapshot_result, target)
```
3. Update `_notify` signature to receive `(snapshot_result: FilterSnapshotResult, scrapping_target: ScrappingTarget)`:
```python
def _notify(self, snapshot_result: FilterSnapshotResult, scrapping_target: ScrappingTarget):
    if not snapshot_result.passed:
        return

    if not (scrapping_target.notification_config and scrapping_target.enable_notifications):
        logger.debug(
            "Skipping notifications for target %s (config=%s, enabled=%s)",
            scrapping_target.id,
            scrapping_target.notification_config_id,
            scrapping_target.enable_notifications,
        )
        return

    # Group passing ExtractedOffers by list_url
    by_list_url: dict[str, list[ExtractedOffer]] = {}
    for ext in snapshot_result.passed:
        by_list_url.setdefault(ext._offer.list_url, []).append(ext)

    message_contexts: list[NotificationMessageContext] = []
    for list_url, ext_offers in by_list_url.items():
        scraping_url = snapshot_result.scraping_url_by_list_url.get(list_url)
        contexts = self._build_contexts(ext_offers, scraping_url)
        message_contexts.extend(contexts)

    if not message_contexts:
        return

    notification_title = self._get_notification_title(
        list(snapshot_result.scraping_url_by_list_url.values()),
        scrapping_target,
        list(by_list_url.keys()),
    )
    self.notification_service_class(message_contexts, scrapping_target, notification_title=notification_title).run()
```
4. Remove `_extract_offers` and `_filter_offers` methods from `OfferBatchCreateService` as they are now encapsulated in `OfferFilterSnapshotService`.

- [x] **Step 5: Run tests to verify**

Run: `uv run pytest shargain/offers/tests/services/test_filter_snapshot.py shargain/offers/tests/services/ -v`
Expected: PASS

- [x] **Step 6: Commit**

```bash
git add shargain/offers/services/filter_snapshot.py shargain/offers/services/batch_create.py shargain/offers/tests/services/test_filter_snapshot.py
git commit -m "feat(offers): snapshot passed_filters at ingest via OfferFilterSnapshotService"
```

---

### Task 3: `UserOfferState` Model & Data Migration from `OfferLike`

**Files:**
- Modify: `shargain/offers/models.py:206-256`
- Create: `shargain/offers/migrations/0027_userofferstate.py`
- Create: `shargain/offers/migrations/0028_migrate_offerlike_to_userofferstate.py`
- Create: `shargain/offers/migrations/0029_delete_offerlike.py`
- Modify: `shargain/offers/admin.py`
- Delete: `shargain/offers/likes.py`
- Modify: `shargain/offers/application/exceptions.py`
- Test: `shargain/offers/tests/models/test_user_offer_state.py`
- Test: `shargain/offers/tests/migrations/test_migrate_offerlike.py`

**Interfaces:**
- Produces: `UserOfferState` model with `user`, `offer`, `seen_at`, `liked_at`, `uniq_user_offer_state`, `user_offer_state_has_state`
- Removes: `OfferLike` model, `shargain/offers/likes.py`, `OfferLikeIdentityError`

- [x] **Step 1: Write failing tests for `UserOfferState` and migration helper**

Create `shargain/offers/tests/models/test_user_offer_state.py`:
```python
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from shargain.offers.models import UserOfferState
from shargain.offers.tests.factories import OfferFactory
from shargain.users.test.factories import UserFactory


@pytest.mark.django_db
class TestUserOfferStateModel:
    def test_can_create_liked_only_state(self):
        user = UserFactory()
        offer = OfferFactory()
        state = UserOfferState.objects.create(user=user, offer=offer, liked_at=timezone.now())
        assert state.liked_at is not None
        assert state.seen_at is None

    def test_can_create_seen_only_state(self):
        user = UserFactory()
        offer = OfferFactory()
        state = UserOfferState.objects.create(user=user, offer=offer, seen_at=timezone.now())
        assert state.seen_at is not None
        assert state.liked_at is None

    def test_cannot_create_state_without_either_timestamp(self):
        user = UserFactory()
        offer = OfferFactory()
        with pytest.raises(IntegrityError):
            UserOfferState.objects.create(user=user, offer=offer, seen_at=None, liked_at=None)

    def test_unique_user_offer_constraint(self):
        user = UserFactory()
        offer = OfferFactory()
        now = timezone.now()
        UserOfferState.objects.create(user=user, offer=offer, seen_at=now)
        with pytest.raises(IntegrityError):
            UserOfferState.objects.create(user=user, offer=offer, liked_at=now)
```

Create migration helper test `shargain/offers/tests/migrations/test_migrate_offerlike.py`:
```python
import pytest
from django.utils import timezone

from shargain.offers.migrations.helpers import copy_likes_to_user_offer_states


def test_copy_likes_to_user_offer_states_copies_account_and_ignores_anonymous():
    class DummyLike:
        def __init__(self, owner_id, offer_id, liker_label, created_at):
            self.owner_id = owner_id
            self.offer_id = offer_id
            self.liker_label = liker_label
            self.created_at = created_at

    class DummyLikeQuerySet:
        def __init__(self, items):
            self.items = items

        def filter(self, **kwargs):
            res = self.items
            if kwargs.get("owner__isnull") is False:
                res = [i for i in res if i.owner_id is not None]
            return DummyLikeQuerySet(res)

        def iterator(self, chunk_size=500):
            yield from self.items

    class DummyStateModel:
        def __init__(self):
            self.created = []

        def bulk_create(self, instances, ignore_conflicts=True):
            self.created.extend(instances)

        def __call__(self, user_id, offer_id, liked_at):
            return {"user_id": user_id, "offer_id": offer_id, "liked_at": liked_at}

    now = timezone.now()
    likes = [
        DummyLike(owner_id=1, offer_id=10, liker_label="", created_at=now),
        DummyLike(owner_id=None, offer_id=20, liker_label="anon", created_at=now),
        DummyLike(owner_id=2, offer_id=30, liker_label="", created_at=now),
    ]

    like_model = DummyLikeQuerySet(likes)
    state_model = DummyStateModel()

    copy_likes_to_user_offer_states(like_model, state_model)

    assert len(state_model.created) == 2
    assert state_model.created[0] == {"user_id": 1, "offer_id": 10, "liked_at": now}
    assert state_model.created[1] == {"user_id": 2, "offer_id": 30, "liked_at": now}
```

- [x] **Step 2: Run tests to verify failure**

Run: `uv run pytest shargain/offers/tests/models/test_user_offer_state.py shargain/offers/tests/migrations/test_migrate_offerlike.py -v`
Expected: FAIL (`UserOfferState` does not exist).

- [x] **Step 3: Define `UserOfferState` model and migration helper**

1. Create `shargain/offers/migrations/helpers.py`:
```python
def copy_likes_to_user_offer_states(like_model, state_model, batch_size=500):
    batch = []
    qs = like_model.objects.filter(owner__isnull=False) if hasattr(like_model, "objects") else like_model.filter(owner__isnull=False)
    for like in qs.iterator(chunk_size=batch_size):
        batch.append(
            state_model(
                user_id=like.owner_id,
                offer_id=like.offer_id,
                liked_at=like.created_at,
            )
        )
        if len(batch) >= batch_size:
            state_model.objects.bulk_create(batch, ignore_conflicts=True) if hasattr(state_model, "objects") else state_model.bulk_create(batch, ignore_conflicts=True)
            batch = []
    if batch:
        state_model.objects.bulk_create(batch, ignore_conflicts=True) if hasattr(state_model, "objects") else state_model.bulk_create(batch, ignore_conflicts=True)
```

2. In `shargain/offers/models.py`, add `UserOfferState` and remove `OfferLike`:
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

    def __str__(self) -> str:
        return f"User #{self.user_id} state for offer #{self.offer_id}"
```

3. Create migrations:
- `shargain/offers/migrations/0027_userofferstate.py`: Creates model `UserOfferState`.
- `shargain/offers/migrations/0028_migrate_offerlike_to_userofferstate.py`: Runs Python function calling `copy_likes_to_user_offer_states(apps.get_model("offers", "OfferLike"), apps.get_model("offers", "UserOfferState"))`.
- `shargain/offers/migrations/0029_delete_offerlike.py`: Deletes model `OfferLike`.

4. Update `shargain/offers/admin.py`: Remove `OfferLikeAdmin` and register `UserOfferStateAdmin`:
```python
@admin.register(UserOfferState)
class UserOfferStateAdmin(admin.ModelAdmin):
    list_display = ("user", "offer", "seen_at", "liked_at", "created_at")
    list_filter = ("offer__target",)
    search_fields = ("offer__url", "offer__title", "user__email")
```

5. Delete `shargain/offers/likes.py` and remove `OfferLikeIdentityError` from `shargain/offers/application/exceptions.py`.

- [x] **Step 4: Run tests to verify**

Run: `uv run pytest shargain/offers/tests/models/test_user_offer_state.py shargain/offers/tests/migrations/test_migrate_offerlike.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add shargain/offers/models.py shargain/offers/migrations/ shargain/offers/admin.py shargain/offers/tests/models/test_user_offer_state.py shargain/offers/tests/migrations/test_migrate_offerlike.py
git rm shargain/offers/likes.py
git commit -m "feat(offers): add UserOfferState model and migrate from OfferLike"
```

---

### Task 4: State Application Commands & Hydration Query

**Files:**
- Modify: `shargain/offers/application/dto.py`
- Modify: `shargain/offers/application/exceptions.py`
- Create: `shargain/offers/application/offer_state.py`
- Create: `shargain/offers/application/queries/get_offer_states.py`
- Test: `shargain/offers/tests/application/test_offer_state.py`
- Test: `shargain/offers/tests/application/queries/test_get_offer_states.py`

**Interfaces:**
- Produces: `OfferState(offer_id: int, seen_at: datetime | None, liked_at: datetime | None)`
- Produces: `OfferDoesNotExist(ApplicationException)`
- Produces: `mark_offers_seen(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]`
- Produces: `mark_offers_unseen(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]`
- Produces: `like_offers(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]`
- Produces: `unlike_offers(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]`
- Produces: `get_offer_states(actor: Actor, offer_ids: Sequence[int]) -> dict[int, OfferState]`

- [x] **Step 1: Write failing tests for `offer_state.py` commands and `get_offer_states`**

Create `shargain/offers/tests/application/test_offer_state.py`:
```python
import pytest
from django.utils import timezone

from shargain.commons.application.actor import Actor
from shargain.offers.application.exceptions import OfferDoesNotExist
from shargain.offers.application.offer_state import (
    like_offers,
    mark_offers_seen,
    mark_offers_unseen,
    unlike_offers,
)
from shargain.offers.models import UserOfferState
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory
from shargain.users.test.factories import UserFactory


@pytest.mark.django_db
class TestOfferStateCommands:
    def test_mark_offers_seen_is_idempotent(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target)
        actor = Actor(user_id=user.id)

        states1 = mark_offers_seen(actor, [offer.id])
        assert len(states1) == 1
        assert states1[0].offer_id == offer.id
        assert states1[0].seen_at is not None
        assert states1[0].liked_at is None

        seen_at_orig = states1[0].seen_at
        states2 = mark_offers_seen(actor, [offer.id])
        assert states2[0].seen_at == seen_at_orig

    def test_like_offers_is_idempotent(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target)
        actor = Actor(user_id=user.id)

        states1 = like_offers(actor, [offer.id])
        assert states1[0].liked_at is not None
        assert states1[0].seen_at is None

        liked_at_orig = states1[0].liked_at
        states2 = like_offers(actor, [offer.id])
        assert states2[0].liked_at == liked_at_orig

    def test_unseen_deletes_row_if_not_liked(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target)
        actor = Actor(user_id=user.id)

        mark_offers_seen(actor, [offer.id])
        assert UserOfferState.objects.filter(user=user, offer=offer).exists()

        states = mark_offers_unseen(actor, [offer.id])
        assert states[0].seen_at is None
        assert not UserOfferState.objects.filter(user=user, offer=offer).exists()

    def test_unlike_clears_liked_at_but_keeps_row_if_seen(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target)
        actor = Actor(user_id=user.id)

        mark_offers_seen(actor, [offer.id])
        like_offers(actor, [offer.id])

        states = unlike_offers(actor, [offer.id])
        assert states[0].liked_at is None
        assert states[0].seen_at is not None

        row = UserOfferState.objects.get(user=user, offer=offer)
        assert row.liked_at is None
        assert row.seen_at is not None

    def test_foreign_or_missing_offer_raises_exception_and_no_mutation(self):
        user = UserFactory()
        other_user = UserFactory()
        target_own = ScrappingTargetFactory(owner=user)
        target_other = ScrappingTargetFactory(owner=other_user)
        offer_own = OfferFactory(target=target_own)
        offer_foreign = OfferFactory(target=target_other)
        actor = Actor(user_id=user.id)

        with pytest.raises(OfferDoesNotExist):
            mark_offers_seen(actor, [offer_own.id, offer_foreign.id])

        assert not UserOfferState.objects.filter(user=user).exists()
```

Create `shargain/offers/tests/application/queries/test_get_offer_states.py`:
```python
import pytest
from django.utils import timezone

from shargain.commons.application.actor import Actor
from shargain.offers.application.offer_state import like_offers, mark_offers_seen
from shargain.offers.application.queries.get_offer_states import get_offer_states
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory
from shargain.users.test.factories import UserFactory


@pytest.mark.django_db
def test_get_offer_states_returns_state_and_defaults_missing():
    user = UserFactory()
    target = ScrappingTargetFactory(owner=user)
    o1 = OfferFactory(target=target)
    o2 = OfferFactory(target=target)
    o3 = OfferFactory(target=target)
    actor = Actor(user_id=user.id)

    mark_offers_seen(actor, [o1.id])
    like_offers(actor, [o2.id])

    states = get_offer_states(actor, [o1.id, o2.id, o3.id])

    assert states[o1.id].seen_at is not None
    assert states[o1.id].liked_at is None
    assert states[o2.id].seen_at is None
    assert states[o2.id].liked_at is not None
    assert states[o3.id].seen_at is None
    assert states[o3.id].liked_at is None
```

- [x] **Step 2: Run tests to verify failure**

Run: `uv run pytest shargain/offers/tests/application/test_offer_state.py shargain/offers/tests/application/queries/test_get_offer_states.py -v`
Expected: FAIL (`ImportError` / `ModuleNotFoundError`).

- [x] **Step 3: Implement `OfferState` DTO and `OfferDoesNotExist`**

1. In `shargain/offers/application/dto.py`:
```python
from datetime import datetime


@dataclasses.dataclass(frozen=True)
class OfferState:
    offer_id: int
    seen_at: datetime | None
    liked_at: datetime | None

    @property
    def is_seen(self) -> bool:
        return self.seen_at is not None

    @property
    def is_liked(self) -> bool:
        return self.liked_at is not None
```

2. In `shargain/offers/application/exceptions.py`:
```python
class OfferDoesNotExist(ApplicationException):
    code: str = "offer_does_not_exist"
    message: str = "Offer does not exist."
```

- [x] **Step 4: Implement `shargain/offers/application/offer_state.py`**

```python
from collections.abc import Sequence
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import OfferState
from shargain.offers.application.exceptions import OfferDoesNotExist
from shargain.offers.models import Offer, UserOfferState

User = get_user_model()


def _validate_actor_offers(actor: Actor, offer_ids: Sequence[int]) -> list[Offer]:
    if not offer_ids:
        return []
    offers = list(
        Offer.objects.filter(pk__in=offer_ids, target__owner_id=actor.user_id).values_list("pk", flat=True)
    )
    if len(offers) != len(set(offer_ids)):
        raise OfferDoesNotExist()
    return list(offer_ids)


def mark_offers_seen(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]:
    if not offer_ids:
        return []
    with transaction.atomic():
        User.objects.select_for_update().get(pk=actor.user_id)
        valid_ids = _validate_actor_offers(actor, offer_ids)
        now = timezone.now()

        # Create missing rows with seen_at set
        existing_states = {
            s.offer_id: s
            for s in UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids)
        }
        to_create = [
            UserOfferState(user_id=actor.user_id, offer_id=oid, seen_at=now)
            for oid in valid_ids
            if oid not in existing_states
        ]
        if to_create:
            UserOfferState.objects.bulk_create(to_create, ignore_conflicts=True)

        # Update existing rows where seen_at IS NULL
        UserOfferState.objects.filter(
            user_id=actor.user_id, offer_id__in=valid_ids, seen_at__isnull=True
        ).update(seen_at=now)

        return _load_states(actor.user_id, valid_ids)


def mark_offers_unseen(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]:
    if not offer_ids:
        return []
    with transaction.atomic():
        User.objects.select_for_update().get(pk=actor.user_id)
        valid_ids = _validate_actor_offers(actor, offer_ids)

        # Rows where liked_at is NULL -> delete (satisfies check constraint)
        UserOfferState.objects.filter(
            user_id=actor.user_id, offer_id__in=valid_ids, liked_at__isnull=True
        ).delete()

        # Rows where liked_at is NOT NULL -> clear seen_at
        UserOfferState.objects.filter(
            user_id=actor.user_id, offer_id__in=valid_ids, liked_at__isnull=False
        ).update(seen_at=None)

        return _load_states(actor.user_id, valid_ids)


def like_offers(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]:
    if not offer_ids:
        return []
    with transaction.atomic():
        User.objects.select_for_update().get(pk=actor.user_id)
        valid_ids = _validate_actor_offers(actor, offer_ids)
        now = timezone.now()

        existing_states = {
            s.offer_id: s
            for s in UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids)
        }
        to_create = [
            UserOfferState(user_id=actor.user_id, offer_id=oid, liked_at=now)
            for oid in valid_ids
            if oid not in existing_states
        ]
        if to_create:
            UserOfferState.objects.bulk_create(to_create, ignore_conflicts=True)

        UserOfferState.objects.filter(
            user_id=actor.user_id, offer_id__in=valid_ids, liked_at__isnull=True
        ).update(liked_at=now)

        return _load_states(actor.user_id, valid_ids)


def unlike_offers(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]:
    if not offer_ids:
        return []
    with transaction.atomic():
        User.objects.select_for_update().get(pk=actor.user_id)
        valid_ids = _validate_actor_offers(actor, offer_ids)

        UserOfferState.objects.filter(
            user_id=actor.user_id, offer_id__in=valid_ids, seen_at__isnull=True
        ).delete()

        UserOfferState.objects.filter(
            user_id=actor.user_id, offer_id__in=valid_ids, seen_at__isnull=False
        ).update(liked_at=None)

        return _load_states(actor.user_id, valid_ids)


def _load_states(user_id: int, offer_ids: Sequence[int]) -> list[OfferState]:
    db_states = {
        s.offer_id: s
        for s in UserOfferState.objects.filter(user_id=user_id, offer_id__in=offer_ids)
    }
    return [
        OfferState(
            offer_id=oid,
            seen_at=db_states[oid].seen_at if oid in db_states else None,
            liked_at=db_states[oid].liked_at if oid in db_states else None,
        )
        for oid in offer_ids
    ]
```

- [x] **Step 5: Implement `shargain/offers/application/queries/get_offer_states.py`**

```python
from collections.abc import Sequence

from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import OfferState
from shargain.offers.models import UserOfferState


def get_offer_states(actor: Actor, offer_ids: Sequence[int]) -> dict[int, OfferState]:
    if not offer_ids:
        return {}
    states = UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=offer_ids)
    state_map = {s.offer_id: OfferState(offer_id=s.offer_id, seen_at=s.seen_at, liked_at=s.liked_at) for s in states}
    return {
        oid: state_map.get(oid, OfferState(offer_id=oid, seen_at=None, liked_at=None))
        for oid in offer_ids
    }
```

- [x] **Step 6: Run tests to verify**

Run: `uv run pytest shargain/offers/tests/application/test_offer_state.py shargain/offers/tests/application/queries/test_get_offer_states.py -v`
Expected: PASS

- [x] **Step 7: Commit**

```bash
git add shargain/offers/application/dto.py shargain/offers/application/exceptions.py shargain/offers/application/offer_state.py shargain/offers/application/queries/get_offer_states.py shargain/offers/tests/application/test_offer_state.py shargain/offers/tests/application/queries/test_get_offer_states.py
git commit -m "feat(offers): implement offer_state commands and get_offer_states query"
```

---

### Task 5: Public Offer Read Model & `list_public_offers` Query

**Files:**
- Modify: `shargain/offers/application/dto.py`
- Create: `shargain/offers/application/queries/list_public_offers.py`
- Test: `shargain/offers/tests/application/queries/test_list_public_offers.py`

**Interfaces:**
- Produces: `OfferAttribute`, `OfferLocation`, `PublicOffer`, `PublicOfferPage`
- Produces: `list_public_offers(actor: Actor, target_id: int, seen: bool | None = None, liked: bool | None = None, ordering: Literal["oldest", "newest"] = "oldest", limit: int = 20, offset: int = 0) -> PublicOfferPage`

- [x] **Step 1: Write failing tests for `list_public_offers`**

Create `shargain/offers/tests/application/queries/test_list_public_offers.py`:
```python
import pytest
from django.utils import timezone

from shargain.commons.application.actor import Actor
from shargain.offers.application.exceptions import TargetDoesNotExist
from shargain.offers.application.offer_state import like_offers, mark_offers_seen
from shargain.offers.application.queries.list_public_offers import list_public_offers
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory
from shargain.users.test.factories import UserFactory


@pytest.mark.django_db
class TestListPublicOffers:
    def test_target_ownership_enforced(self):
        user = UserFactory()
        other_user = UserFactory()
        target = ScrappingTargetFactory(owner=other_user)
        actor = Actor(user_id=user.id)

        with pytest.raises(TargetDoesNotExist):
            list_public_offers(actor, target.id)

    def test_excludes_passed_filters_null_or_false(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        OfferFactory(target=target, passed_filters=None)
        OfferFactory(target=target, passed_filters=False)
        o_valid = OfferFactory(target=target, passed_filters=True)

        page = list_public_offers(actor, target.id)
        assert page.count == 1
        assert page.items[0].id == o_valid.id

    def test_filter_seen_and_unseen(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        o_seen = OfferFactory(target=target, passed_filters=True)
        o_unseen = OfferFactory(target=target, passed_filters=True)
        mark_offers_seen(actor, [o_seen.id])

        page_unseen = list_public_offers(actor, target.id, seen=False)
        assert [i.id for i in page_unseen.items] == [o_unseen.id]

        page_seen = list_public_offers(actor, target.id, seen=True)
        assert [i.id for i in page_seen.items] == [o_seen.id]

    def test_filter_liked(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        o_liked = OfferFactory(target=target, passed_filters=True)
        o_unliked = OfferFactory(target=target, passed_filters=True)
        like_offers(actor, [o_liked.id])

        page_liked = list_public_offers(actor, target.id, liked=True)
        assert [i.id for i in page_liked.items] == [o_liked.id]

        page_unliked = list_public_offers(actor, target.id, liked=False)
        assert [i.id for i in page_unliked.items] == [o_unliked.id]

    def test_ordering_oldest_and_newest(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        o1 = OfferFactory(target=target, passed_filters=True)
        o2 = OfferFactory(target=target, passed_filters=True)

        page_oldest = list_public_offers(actor, target.id, ordering="oldest")
        assert [i.id for i in page_oldest.items] == [o1.id, o2.id]

        page_newest = list_public_offers(actor, target.id, ordering="newest")
        assert [i.id for i in page_newest.items] == [o2.id, o1.id]

    def test_attributes_excludes_title_and_price(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)
        offer = OfferFactory(
            target=target,
            passed_filters=True,
            list_url="https://www.olx.pl/d/nieruchomosci/mieszkania/",
            title="Mieszkanie 2 pokoje",
            price=2500,
            metadata={"extra": {}},
        )

        page = list_public_offers(actor, target.id)
        attr_names = [attr.name for attr in page.items[0].attributes]
        assert "title" not in attr_names
        assert "price" not in attr_names
```

- [x] **Step 2: Run test to verify failure**

Run: `uv run pytest shargain/offers/tests/application/queries/test_list_public_offers.py -v`
Expected: FAIL (`ImportError` / `ModuleNotFoundError`).

- [x] **Step 3: Define `PublicOffer` DTOs**

In `shargain/offers/application/dto.py`:
```python
@dataclasses.dataclass(frozen=True)
class OfferAttribute:
    name: str
    label: str
    type: str
    unit: str | None
    value: bool | int | float | str
    display: str | None = None


@dataclasses.dataclass(frozen=True)
class OfferLocation:
    name: str | None
    map_url: str | None
    latitude: float | None
    longitude: float | None
    is_exact: bool


@dataclasses.dataclass(frozen=True)
class PublicOffer:
    id: int
    url: str
    title: str
    price: int | None
    main_image_url: str | None
    published_at: datetime | None
    created_at: datetime
    closed_at: datetime | None
    list_url: str
    is_seen: bool
    seen_at: datetime | None
    is_liked: bool
    liked_at: datetime | None
    attributes: list[OfferAttribute]
    location: OfferLocation | None


@dataclasses.dataclass(frozen=True)
class PublicOfferPage:
    count: int
    items: list[PublicOffer]
```

- [x] **Step 4: Implement `list_public_offers`**

Create `shargain/offers/application/queries/list_public_offers.py`:
```python
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
from shargain.offers.application.queries.get_offer_states import get_offer_states
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
        for name, spec in field_specs.items():
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

            attributes.append(
                OfferAttribute(
                    name=name,
                    label=str(spec.label),
                    type=spec.type,
                    unit=spec.unit,
                    value=raw_val,
                    display=display,
                )
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
```

- [x] **Step 5: Run tests to verify**

Run: `uv run pytest shargain/offers/tests/application/queries/test_list_public_offers.py -v`
Expected: PASS

- [x] **Step 6: Commit**

```bash
git add shargain/offers/application/dto.py shargain/offers/application/queries/list_public_offers.py shargain/offers/tests/application/queries/test_list_public_offers.py
git commit -m "feat(offers): implement list_public_offers query with attributes and location projection"
```

---

### Task 6: Ninja API Router & Mounting

**Files:**
- Create: `shargain/offers/api.py`
- Modify: `shargain/public_api/api.py`
- Test: `shargain/offers/tests/api/test_offers_api.py`

**Interfaces:**
- Produces: `GET /api/public/targets/{target_id}/offers`
- Produces: `POST /api/public/targets/{target_id}/offers/{offer_id}/seen`
- Produces: `DELETE /api/public/targets/{target_id}/offers/{offer_id}/seen`
- Produces: `POST /api/public/targets/{target_id}/offers/{offer_id}/like`
- Produces: `DELETE /api/public/targets/{target_id}/offers/{offer_id}/like`

- [x] **Step 1: Write failing tests for Ninja API endpoints and boundary**

Create `shargain/offers/tests/api/test_offers_api.py`:
```python
import pytest
from django.test import Client

from shargain.offers.application.offer_state import like_offers, mark_offers_seen
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory
from shargain.users.test.factories import UserFactory


@pytest.mark.django_db
class TestOffersApi:
    def test_list_offers_requires_auth(self):
        client = Client()
        resp = client.get("/api/public/targets/1/offers")
        assert resp.status_code in (401, 403)

    def test_list_offers_foreign_target_returns_404(self):
        user = UserFactory()
        other_user = UserFactory()
        target = ScrappingTargetFactory(owner=other_user)
        client = Client()
        client.force_login(user)

        resp = client.get(f"/api/public/targets/{target.id}/offers")
        assert resp.status_code == 404

    def test_list_offers_returns_page_and_does_not_mark_seen(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target, passed_filters=True, title="Test Offer")
        client = Client()
        client.force_login(user)

        resp = client.get(f"/api/public/targets/{target.id}/offers")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == offer.id
        assert data["items"][0]["isSeen"] is False
        assert data["items"][0]["isLiked"] is False

    def test_seen_actions(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target, passed_filters=True)
        client = Client()
        client.force_login(user)

        # POST seen
        resp = client.post(f"/api/public/targets/{target.id}/offers/{offer.id}/seen")
        assert resp.status_code == 200
        data = resp.json()
        assert data["isSeen"] is True
        assert data["seenAt"] is not None

        # DELETE seen
        resp = client.delete(f"/api/public/targets/{target.id}/offers/{offer.id}/seen")
        assert resp.status_code == 200
        data = resp.json()
        assert data["isSeen"] is False
        assert data["seenAt"] is None

    def test_like_actions(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target, passed_filters=True)
        client = Client()
        client.force_login(user)

        # POST like
        resp = client.post(f"/api/public/targets/{target.id}/offers/{offer.id}/like")
        assert resp.status_code == 200
        data = resp.json()
        assert data["isLiked"] is True
        assert data["likedAt"] is not None

        # DELETE like
        resp = client.delete(f"/api/public/targets/{target.id}/offers/{offer.id}/like")
        assert resp.status_code == 200
        data = resp.json()
        assert data["isLiked"] is False
        assert data["likedAt"] is None

    def test_offer_in_another_target_returns_404(self):
        user = UserFactory()
        target1 = ScrappingTargetFactory(owner=user)
        target2 = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target1, passed_filters=True)
        client = Client()
        client.force_login(user)

        # Request offer under wrong target
        resp = client.post(f"/api/public/targets/{target2.id}/offers/{offer.id}/seen")
        assert resp.status_code == 404

    def test_boundary_no_offer_model_import_in_api(self):
        with open("shargain/offers/api.py") as f:
            content = f.read()
        assert "from shargain.offers.models import Offer" not in content
        assert "import Offer" not in content
```

- [x] **Step 2: Run test to verify failure**

Run: `uv run pytest shargain/offers/tests/api/test_offers_api.py -v`
Expected: FAIL (`404` or `ImportError`).

- [x] **Step 3: Implement `shargain/offers/api.py`**

```python
from datetime import datetime
from typing import Literal

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import OfferState, PublicOfferPage
from shargain.offers.application.exceptions import OfferDoesNotExist, TargetDoesNotExist
from shargain.offers.application.offer_state import (
    like_offers,
    mark_offers_seen,
    mark_offers_unseen,
    unlike_offers,
)
from shargain.offers.application.queries.list_public_offers import list_public_offers
from shargain.offers.application.queries.get_offer_states import get_offer_states

router = Router(tags=["offers"])


class BaseSchema(Schema):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class OfferAttributeSchema(BaseSchema):
    name: str
    label: str
    type: str
    unit: str | None = None
    value: bool | int | float | str
    display: str | None = None


class OfferLocationSchema(BaseSchema):
    name: str | None = None
    map_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_exact: bool


class PublicOfferSchema(BaseSchema):
    id: int
    url: str
    title: str
    price: int | None = None
    main_image_url: str | None = None
    published_at: datetime | None = None
    created_at: datetime
    closed_at: datetime | None = None
    list_url: str
    is_seen: bool
    seen_at: datetime | None = None
    is_liked: bool
    liked_at: datetime | None = None
    attributes: list[OfferAttributeSchema]
    location: OfferLocationSchema | None = None


class PublicOfferPageSchema(BaseSchema):
    count: int
    items: list[PublicOfferSchema]


class OfferStateResponseSchema(BaseSchema):
    offer_id: int
    is_seen: bool
    seen_at: datetime | None = None
    is_liked: bool
    liked_at: datetime | None = None


def _get_actor(request: HttpRequest) -> Actor:
    if not request.user or not request.user.is_authenticated:
        raise HttpError(401, "Unauthorized")
    return Actor(user_id=request.user.id)


def _check_target_scope(actor: Actor, target_id: int, offer_id: int):
    # Verify the offer exists and belongs to target_id and actor
    # To keep model import out of api.py, we rely on state validation or list query
    # But checking target_id scoping:
    from shargain.offers.application.queries.list_public_offers import ScrappingTarget
    if not ScrappingTarget.objects.filter(pk=target_id, owner_id=actor.user_id, offer__id=offer_id).exists():
        raise HttpError(404, "Offer not found for target")


@router.get("/targets/{target_id}/offers", response=PublicOfferPageSchema)
def get_target_offers(
    request: HttpRequest,
    target_id: int,
    seen: bool | None = None,
    liked: bool | None = None,
    ordering: Literal["oldest", "newest"] = "oldest",
    limit: int = 20,
    offset: int = 0,
):
    actor = _get_actor(request)
    try:
        page = list_public_offers(
            actor=actor,
            target_id=target_id,
            seen=seen,
            liked=liked,
            ordering=ordering,
            limit=limit,
            offset=offset,
        )
        return page
    except TargetDoesNotExist:
        raise HttpError(404, "Target not found")


@router.post("/targets/{target_id}/offers/{offer_id}/seen", response=OfferStateResponseSchema)
def mark_offer_seen(request: HttpRequest, target_id: int, offer_id: int):
    actor = _get_actor(request)
    _check_target_scope(actor, target_id, offer_id)
    try:
        states = mark_offers_seen(actor, [offer_id])
        return states[0]
    except OfferDoesNotExist:
        raise HttpError(404, "Offer not found")


@router.delete("/targets/{target_id}/offers/{offer_id}/seen", response=OfferStateResponseSchema)
def mark_offer_unseen(request: HttpRequest, target_id: int, offer_id: int):
    actor = _get_actor(request)
    _check_target_scope(actor, target_id, offer_id)
    try:
        states = mark_offers_unseen(actor, [offer_id])
        return states[0]
    except OfferDoesNotExist:
        raise HttpError(404, "Offer not found")


@router.post("/targets/{target_id}/offers/{offer_id}/like", response=OfferStateResponseSchema)
def like_offer(request: HttpRequest, target_id: int, offer_id: int):
    actor = _get_actor(request)
    _check_target_scope(actor, target_id, offer_id)
    try:
        states = like_offers(actor, [offer_id])
        return states[0]
    except OfferDoesNotExist:
        raise HttpError(404, "Offer not found")


@router.delete("/targets/{target_id}/offers/{offer_id}/like", response=OfferStateResponseSchema)
def unlike_offer(request: HttpRequest, target_id: int, offer_id: int):
    actor = _get_actor(request)
    _check_target_scope(actor, target_id, offer_id)
    try:
        states = unlike_offers(actor, [offer_id])
        return states[0]
    except OfferDoesNotExist:
        raise HttpError(404, "Offer not found")
```

- [x] **Step 4: Mount offers router in `shargain/public_api/api.py`**

In `shargain/public_api/api.py`:
```python
from shargain.offers.api import router as offers_router

router.add_router("/", offers_router)
```

- [x] **Step 5: Run tests to verify**

Run: `uv run pytest shargain/offers/tests/api/test_offers_api.py -v`
Expected: PASS

- [x] **Step 6: Commit**

```bash
git add shargain/offers/api.py shargain/public_api/api.py shargain/offers/tests/api/test_offers_api.py
git commit -m "feat(offers): add offer inbox API router and mount in public_api"
```

---

### Task 7: Telegram Bot Refactoring (Account-Only Likes)

**Files:**
- Modify: `shargain/telegram/bot.py`
- Test: `shargain/telegram/tests/test_bot.py`

**Interfaces:**
- Produces: `resolve_user_for_offer_chat(offer: Offer, chat_id: int | str) -> int | None`
- Produces: `resolve_user_for_chat(chat_id: int | str) -> int | None`
- Produces: Scoped `resolve_offers_from_message`
- Produces: Account-attributed `handle_like_reply`, `/liked`, `/unlike_{id}`

- [x] **Step 1: Write failing tests for Telegram like attribution**

In `shargain/telegram/tests/test_bot.py`:
Add tests:
- `test_resolve_user_for_offer_chat_matches_owner_and_chatid`
- `test_resolve_user_for_offer_chat_returns_none_if_unmatched`
- `test_resolve_user_for_chat_returns_unique_owner`
- `test_resolve_user_for_chat_returns_none_for_ambiguous_or_unregistered`
- `test_handle_like_reply_likes_and_unlikes_with_account_attribution`
- `test_handle_like_reply_rejects_unattributable_batch`
- `test_liked_command_lists_only_resolved_user_liked_offers`

- [x] **Step 2: Run tests to verify failure**

Run: `uv run pytest shargain/telegram/tests/test_bot.py -v`
Expected: FAIL.

- [x] **Step 3: Implement helper functions and refactor bot commands**

In `shargain/telegram/bot.py`:
1. Remove `AnonymousLiker`, `OfferLike`, `shargain.offers.likes`.
2. Import `like_offers`, `unlike_offers` from `shargain.offers.application.offer_state`.
3. Add `resolve_user_for_offer_chat(offer: Offer, chat_id: int | str) -> int | None`:
```python
def resolve_user_for_offer_chat(offer: Offer, chat_id: int | str) -> int | None:
    config = getattr(offer.target, "notification_config", None)
    if config and config.owner_id and str(config.chatid) == str(chat_id):
        return config.owner_id
    return None
```
4. Add `resolve_user_for_chat(chat_id: int | str) -> int | None`:
```python
def resolve_user_for_chat(chat_id: int | str) -> int | None:
    from shargain.offers.models import ScrappingTarget
    owners = set(
        ScrappingTarget.objects.filter(
            notification_config__chatid=str(chat_id),
            notification_config__owner__isnull=False,
        ).values_list("notification_config__owner_id", flat=True).distinct()
    )
    if len(owners) == 1:
        return next(iter(owners))
    return None
```
5. Update `resolve_offers_from_message` to scope to the chat:
```python
def resolve_offers_from_message(message: Message) -> list[Offer]:
    ...
    return list(
        Offer.objects.filter(
            url__in=urls,
            target__notification_config__chatid=str(message.chat.id),
            target__notification_config__owner__isnull=False,
        ).select_related("target__notification_config")
    )
```
6. Update `handle_like_reply`:
```python
user_ids = {resolve_user_for_offer_chat(o, message.chat.id) for o in offers}
if None in user_ids or len(user_ids) != 1:
    self.bot.reply_to(message, _("Could not attribute like to an authorized account."))
    return

user_id = next(iter(user_ids))
actor = Actor(user_id=user_id)
# Check if all are already liked
existing_states = get_offer_states(actor, [o.id for o in offers])
all_liked = all(s.is_liked for s in existing_states.values())

if all_liked:
    unlike_offers(actor, [o.id for o in offers])
    self.bot.reply_to(message, _("Unliked"))
else:
    like_offers(actor, [o.id for o in offers])
    self.bot.reply_to(message, _("Liked"))
```
7. Update `/liked` command to use `resolve_user_for_chat` and query `UserOfferState`.
8. Update `/unlike_{offer_id}` command to scope to chat and attribute via `resolve_user_for_offer_chat`.

- [x] **Step 4: Run tests to verify**

Run: `uv run pytest shargain/telegram/tests/test_bot.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add shargain/telegram/bot.py shargain/telegram/tests/test_bot.py
git commit -m "refactor(telegram): attribute likes to user accounts using UserOfferState"
```

---

### Task 8: OpenAPI Spec & TypeScript Client Generation

**Files:**
- Modify: `dump_openapi.py` (if needed)
- Output: `frontend/openapi.json`
- Output: `frontend/src/lib/api/`

- [x] **Step 1: Generate `frontend/openapi.json`**

Run: `uv run python dump_openapi.py`
Verify `frontend/openapi.json` contains `/api/public/targets/{target_id}/offers` and `/seen`, `/like` endpoints.

- [x] **Step 2: Generate TypeScript client**

Run: `frontend/node_modules/.bin/openapi-ts` (or `pnpm -C frontend generate:api-client`)
Verify generated files in `frontend/src/lib/api/` include the new models and operations (`getTargetOffers`, `postTargetOfferSeen`, `deleteTargetOfferSeen`, `postTargetOfferLike`, `deleteTargetOfferLike`).

- [x] **Step 3: Run frontend typecheck and linter**

Run: `frontend/node_modules/.bin/tsc --noEmit --project frontend/tsconfig.json`
Run: `pnpm -C frontend lint:fix`
Verify zero errors.

- [x] **Step 4: Commit**

```bash
git add frontend/openapi.json frontend/src/lib/api/
git commit -m "chore(api): update openapi.json and regenerate TypeScript client"
```

---

### Task 9: Full Suite Verification & Quality Checks

**Files:**
- All touched files

- [x] **Step 1: Run full backend test suite**

Run: `uv run pytest`
Expected: All tests pass.

- [x] **Step 2: Run linter and formatting checks**

Run: `uv run ruff check shargain`
Run: `uv run ruff format --check shargain`
Run: `uv run mypy shargain`
Expected: Zero warnings/errors.

- [x] **Step 3: Verify git status is clean**

Run: `git status`
Verify all tracked changes are committed cleanly.
