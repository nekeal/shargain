# Subscriptions Feature — Test-First Implementation Plan

## Context

Shargain currently enforces quotas with a hardcoded free tier in `quotas` settings and models. This spec introduces subscription plans (Free/Plus/Pro) and wires plan changes into quota behavior using signals while preserving bounded-context rules.

This plan is explicitly **red → green**:
1. Write behavior and contract tests first (and confirm they fail for the right reasons)
2. Implement only what is needed to make tests pass, in vertical slices

**Standards applied:**
- `agent-os/specs/2026-02-16-1830-subscription-plans/standards.md` (DTO, custom querysets, signal/service patterns)
- `agent-os/specs/2026-02-16-1830-subscription-plans/references.md` (existing quota/auth/api integration points)

---

## Task 1: Freeze Spec Inputs

1. Confirm `shape.md`, `context-map.md`, `standards.md`, and `references.md` are final inputs.
2. Record unresolved assumptions at the top of this file before coding starts.
3. Lock test-writing heuristics for all tasks:
- Prefer assertions on externally observable behavior (API response, persisted state transitions, emitted signal payloads), not private implementation details.
- Keep test setup and verification at the same abstraction level (API-level setup with API-level assertions, service-level setup with service-level assertions).

Deliverable:
- This plan file is the execution source of truth for implementation order.

---

## Task 2: Write Failing Contract Tests (No Feature Code Yet)

Add/extend tests to lock external contracts before implementation.

1. **DTO Contract Tests**
- File: `shargain/subscriptions/tests/application/test_plan_limits_dto.py`
- Assert `PlanLimitsDTO` is immutable/frozen and carries exact fields:
  - `max_urls`
  - `max_offers_per_target`
  - `plan_slug`

2. **Signal Contract Tests**
- File: `shargain/subscriptions/tests/application/test_subscription_signals_contract.py`
- Assert `assign_plan` emits:
  - `subscription_upgraded` on upward tier change
  - `subscription_downgraded` on downward tier change
- Assert payload contract includes `user_id`, `previous_plan_slug`, and `plan_limits: PlanLimitsDTO`

3. **Public API Contract Test**
- File: `shargain/public_api/tests/test_subscription_current_api.py`
- Assert `GET /api/public/subscription/current` response schema includes only agreed fields:
  - `planName`, `planSlug`, `maxUrls`, `maxOffersPerTarget`, `expiresAt`
- Assert unauthorized access behavior matches current public API auth conventions.

4. **Signup Behavior Contract Test**
- File: `shargain/public_api/tests/test_signup_subscription_assignment.py`
- Assert signup assigns default free plan and creates active subscription row.
- Verify through observable outcomes (signup response + persisted active subscription), not by mocking internal service calls.

Expected result:
- New tests fail because subscriptions feature is not implemented yet.

---

## Task 3: Write Failing Quota Integration Behavior Tests (No Integration Code Yet)

Create tests in quotas to define exact downstream behavior on subscription events.

1. **Upgrade Behavior Tests**
- File: `shargain/quotas/tests/services/test_subscription_upgrade_handler.py`
- Assert on upgrade:
  - `ScrapingUrlQuota.max_urls` updates immediately
  - Active `OfferQuota` periods are closed (no longer auto-renew)
  - New `OfferQuota` period rows are created with reset usage and upgraded limits
  - `is_free_tier` reflects `plan_slug == "free"`
- Verify resulting quota rows and active period state; avoid assertions coupled to receiver internals.

2. **Downgrade Behavior Tests**
- File: `shargain/quotas/tests/services/test_subscription_downgrade_handler.py`
- Assert on downgrade:
  - `ScrapingUrlQuota.max_urls` updates immediately
  - Existing active `OfferQuota` period remains active until renewal
  - No immediate usage reset
- Verify period continuity and limits behavior from persisted state, not call-order internals.

3. **Legacy Safety Test**
- File: `shargain/subscriptions/tests/services/test_legacy_user_fallback.py`
- Assert user without subscription is automatically placed on default/free plan limits.

Expected result:
- Tests fail until signals and handlers are implemented.

---

## Task 4: Implement Subscription Domain (Minimal to Satisfy Tests)

1. Create `shargain/subscriptions/` app and register in `INSTALLED_APPS`.

2. Implement models:
```python
# Plan
class Plan(TimeStampedModel):
    name: str
    slug: str (unique)
    max_urls: int
    max_offers_per_target: int
    is_default: bool
    is_active: bool
    display_order: int  # Lower = higher tier (Free=0, Plus=10, Pro=20)

# UserSubscription
class UserSubscription(TimeStampedModel):
    user: FK(CustomUser)
    plan: FK(Plan)
    started_at: DateTimeField(auto_now_add=True)
    expires_at: DateTimeField(null=True)  # null = never expires (free tier)
    is_active: bool

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active'])  # optimize active lookup
        ]
```

3. Implement querysets/managers:
- `PlanQuerySet.active()` — filters `is_active=True`
- `PlanQuerySet.default()` — filters `is_default=True`
- `UserSubscriptionQuerySet.active()` — filters `is_active=True`

4. Add migrations for schema.

5. Implement `PlanLimitsDTO`:
```python
@dataclass(frozen=True)
class PlanLimitsDTO:
    max_urls: int
    max_offers_per_target: int
    plan_slug: str

    @classmethod
    def from_plan(cls, plan: Plan) -> "PlanLimitsDTO":
        return cls(
            max_urls=plan.max_urls,
            max_offers_per_target=plan.max_offers_per_target,
            plan_slug=plan.slug,
        )
```

6. Implement `SubscriptionService` methods:
- `get_user_plan_limits(user_id)` — returns `PlanLimitsDTO`, auto-assigns free plan if none exists
- `assign_plan(user_id, plan_slug)` — wrapped in `@transaction.atomic`, deactivates old subscriptions, emits signals
- `get_user_subscription(user_id)` — returns active `UserSubscription` or None

7. Signal emission logic in `assign_plan()`:
```python
# Determine upgrade vs downgrade by display_order (lower = higher tier)
if new_plan.display_order < old_plan.display_order:
    subscription_upgraded.send(
        sender=self.__class__,
        user_id=user_id,
        plan_limits=PlanLimitsDTO.from_plan(new_plan),
        previous_plan_slug=old_plan.slug,
    )
else:
    subscription_downgraded.send(
        sender=self.__class__,
        user_id=user_id,
        plan_limits=PlanLimitsDTO.from_plan(new_plan),
        previous_plan_slug=old_plan.slug,
    )
```

8. Define signals in `shargain/subscriptions/signals.py`:
```python
subscription_upgraded = django.dispatch.Signal()  # user_id, plan_limits, previous_plan_slug
subscription_downgraded = django.dispatch.Signal()  # user_id, plan_limits, previous_plan_slug
```

9. Wire signals in `apps.py`:
```python
def ready(self):
    import shargain.subscriptions.signals  # noqa
```

Acceptance:
- Contract tests from Task 2 (DTO + signal contract) pass.

---

## Task 5: Implement Quota Signal Handlers (Minimal to Satisfy Tests)

1. Add queryset helper in `shargain/quotas/querysets.py`:
```python
class OfferQuotaQuerySet(QuerySet):
    # ... existing methods ...

    def for_user(self, user_id: int):
        """Get all quotas for a user across all targets"""
        return self.filter(user_id=user_id)
```

2. Add quota-side receivers in `shargain/quotas/signals.py`:

**Upgrade handler:**
```python
from django.db import transaction
from shargain.subscriptions.signals import subscription_upgraded

@receiver(subscription_upgraded)
@transaction.atomic
def handle_subscription_upgraded(sender, user_id, plan_limits, previous_plan_slug, **kwargs):
    # 1. Update ScrapingUrlQuota (get_or_create pattern)
    url_quota, _ = ScrapingUrlQuota.objects.get_or_create(
        user_id=user_id,
        defaults={"max_urls": plan_limits.max_urls}
    )
    url_quota.max_urls = plan_limits.max_urls
    url_quota.save()

    # 2. Close all active OfferQuota periods (stop auto-renewal)
    OfferQuota.objects.for_user(user_id).active().update(auto_renew=False)

    # 3. Create new OfferQuota period for each target with fresh limits
    targets = ScrappingTarget.objects.filter(owner_id=user_id)
    for target in targets:
        period_start = timezone.now()
        period_end = period_start + timedelta(days=settings.QUOTA_PERIOD_DAYS)
        OfferQuota.objects.create(
            user_id=user_id,
            target_id=target.id,
            max_offers_per_period=plan_limits.max_offers_per_target,
            used_offers_count=0,
            period_start=period_start,
            period_end=period_end,
            auto_renew=True,
            is_free_tier=(plan_limits.plan_slug == "free"),
        )
```

**Downgrade handler:**
```python
from shargain.subscriptions.signals import subscription_downgraded

@receiver(subscription_downgraded)
@transaction.atomic
def handle_subscription_downgraded(sender, user_id, plan_limits, previous_plan_slug, **kwargs):
    # 1. Update ScrapingUrlQuota immediately (existing URLs kept, new creation blocked)
    url_quota, _ = ScrapingUrlQuota.objects.get_or_create(
        user_id=user_id,
        defaults={"max_urls": plan_limits.max_urls}
    )
    url_quota.max_urls = plan_limits.max_urls
    url_quota.save()

    # 2. DO NOT reset OfferQuota periods — lower limits apply on next auto-renewal
    # Existing active periods continue with current limits until period_end
```

3. Wire in `shargain/quotas/apps.py`:
```python
def ready(self):
    import shargain.quotas.signals  # noqa — registers receivers
```

Acceptance:
- Task 3 quota integration behavior tests pass.

---

## Task 6: Implement Public API + Signup Wiring (Minimal to Satisfy Tests)

1. Update signup flow in `shargain/public_api/auth.py:signup_view()`:
```python
# After line 80 (after ScrappingTarget.objects.create)
from shargain.subscriptions.services import SubscriptionService

ScrappingTarget.objects.create(owner=user)
SubscriptionService.assign_plan(user.id, "free")  # <-- ADD THIS
```

2. Add subscription endpoint in `shargain/public_api/subscription.py`:

**Response schema:**
```python
class SubscriptionResponse(BaseSchema):
    plan_name: str
    plan_slug: str
    max_urls: int
    max_offers_per_target: int
    started_at: str  # ISO datetime
    expires_at: str | None  # null for free plan

    class Config:
        alias_generator = to_camel
        populate_by_name = True
```

**Endpoint:**
```python
@router.get("/current", response=SubscriptionResponse, operation_id="get_current_subscription", by_alias=True)
def get_current_subscription(request: HttpRequest):
    subscription = SubscriptionService.get_user_subscription(request.user.id)
    if not subscription:
        # Fallback for legacy users
        SubscriptionService.assign_plan(request.user.id, "free")
        subscription = SubscriptionService.get_user_subscription(request.user.id)

    return SubscriptionResponse(
        plan_name=subscription.plan.name,
        plan_slug=subscription.plan.slug,
        max_urls=subscription.plan.max_urls,
        max_offers_per_target=subscription.plan.max_offers_per_target,
        started_at=subscription.started_at.isoformat(),
        expires_at=subscription.expires_at.isoformat() if subscription.expires_at else None,
    )
```

3. Register router in `shargain/public_api/api.py`:
```python
from shargain.public_api.subscription import router as subscription_router
api.add_router("/subscription/", subscription_router, tags=["subscription"])
```

Acceptance:
- Task 2 API/signup contract tests pass.

---

## Task 7: Data Migration + Backfill

1. Seed default `free` plan with exact values:
```python
Plan.objects.get_or_create(
    slug="free",
    defaults={
        "name": "Free",
        "max_urls": 3,  # from settings.QUOTA_FREE_TIER_MAX_URLS
        "max_offers_per_target": 50,  # from settings.QUOTA_FREE_TIER_OFFERS_PER_TARGET
        "is_default": True,
        "is_active": True,
        "display_order": 0,
    }
)
```

2. Backfill active free subscriptions for existing users:
```python
from django.contrib.auth import get_user_model

User = get_user_model()
free_plan = Plan.objects.get(slug="free")

# Batch process existing users
for user in User.objects.iterator(chunk_size=500):
    if not UserSubscription.objects.filter(user=user, is_active=True).exists():
        UserSubscription.objects.create(
            user=user,
            plan=free_plan,
            is_active=True,
            expires_at=None,  # never expires
        )
```

3. Sync existing quota records to match Free plan limits (safe because all existing users are free tier):
```python
# Update all ScrapingUrlQuota to match free plan
ScrapingUrlQuota.objects.update(max_urls=3)

# Update all OfferQuota to match free plan
OfferQuota.objects.update(max_offers_per_period=50, is_free_tier=True)
```

4. Use chunked iteration (`iterator(chunk_size=500)`) for user backfill to prevent memory issues.

Acceptance:
- Migration runs successfully on dev data
- All existing users have active free subscription
- All quota records have consistent limits

---

## Task 8: Admin & Operational Visibility

1. Register `PlanAdmin` with key limits/status columns.
2. Register `UserSubscriptionAdmin` with user/plan/active/started/expires columns.
3. Ensure list filters/search are present for basic support operations.

Acceptance:
- Admin pages load and reflect expected fields.

---

## Task 9: Verification Gate

Run the smallest useful sequence repeatedly while implementing, then full suite for touched areas.

1. `just test` scoped to new/changed subscription + quota + public_api tests.
2. `just quality-check` for lint/type checks.
3. Re-run full impacted backend tests before merge.

Required evidence to capture in PR notes:
- Which tests were added first
- Initial failing test output (red state)
- Final passing output after implementation (green state)
- Confirmation that tests assert observable behavior and maintain setup/assertion abstraction parity.

---

## Execution Order (Strict)

1. Task 2 (contracts, failing)
2. Task 3 (integration behaviors, failing)
3. Task 4 (subscription domain)
4. Task 5 (quota handlers)
5. Task 6 (API + signup wiring)
6. Task 7 (data migration)
7. Task 8 (admin)
8. Task 9 (verification and evidence)

No implementation starts before Tasks 2 and 3 are committed in failing form.
