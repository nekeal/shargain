# Codebase Concerns

**Analysis Date:** 2026-01-24

## Tech Debt

**DEBUG mode hardcoded in base settings:**
- Issue: `DEBUG = True` is set as default in `shargain/settings/base.py:18`, creating security risk if production environment isn't explicitly overridden
- Files: `shargain/settings/base.py:18`, `shargain/settings/production.py:6`
- Impact: Exposes sensitive information, full exception traces, and debug toolbar in production if override fails. High security risk.
- Fix approach: Remove `DEBUG = True` from base.py and make it environment-dependent via env var. Verify all deployment pipelines set `DJANGO_DEBUG=False` explicitly.

**Bare Exception Handling:**
- Issue: Exception handler in `shargain/notifications/views/api.py:24` uses bare `except Exception` without logging specifics
- Files: `shargain/notifications/views/api.py:24-27`
- Impact: Telegram webhook errors silently fail, missing critical debugging information. Production issues become invisible.
- Fix approach: Replace with specific exception handling. Log exception details. Return appropriate HTTP status codes.

**Print statements in production code:**
- Issue: Multiple `print()` calls left in non-test code used in Celery tasks and API endpoints
- Files: `shargain/offers/tasks.py:50,53,56`, `shargain/public_api/auth.py:77`, `shargain/scrapper/management/commands/scrap.py`, `shargain/celery.py`
- Impact: Output goes to stdout instead of logging system. Invisible in production logging. Violates 12-factor app principles.
- Fix approach: Replace all `print()` with proper `logger.*()` calls. Use ruff linter rule T201 (already enabled in pyproject.toml but not enforced in CI).

**Incomplete password validation:**
- Issue: `_validate_password()` in `shargain/public_api/auth.py:29-31` is a no-op that doesn't call Django's validators
- Files: `shargain/public_api/auth.py:29-31`
- Impact: Users can register with weak passwords (single character, only numbers, etc.). Security vulnerability.
- Fix approach: Implement proper validation using Django's `validate_password()` from `django.contrib.auth.password_validation`. Catch `ValidationError` and raise `ValueError` for Pydantic.

**Inefficient database queries in get_target functions:**
- Issue: Query duplication and complex prefetch logic repeated in two similar functions (`get_target` and `get_target_by_user`)
- Files: `shargain/offers/application/queries/get_target.py:11-64`
- Impact: Code duplication increases maintenance burden. Complex query logic is error-prone and hard to test. TODO comment at line 44 indicates known issue.
- Fix approach: Extract shared query logic into a queryset method on `ScrappingTarget` or `ScrapingUrl`. Use single source of truth for prefetch patterns.

**CORS configured to allow all origins:**
- Issue: `CORS_ALLOW_ALL_ORIGINS = True` in `shargain/settings/base.py:155`
- Files: `shargain/settings/base.py:155`
- Impact: Any website can make requests to API. Bypasses CORS security controls entirely. Serious security vulnerability.
- Fix approach: Explicitly define `CORS_ALLOWED_ORIGINS` list. In development use `localhost:*`, in production use exact frontend domain(s). Remove `CORS_ALLOW_ALL_ORIGINS` setting.

**Unprotected queryset access in NotificationConfigViewSet:**
- Issue: `NotificationConfigViewSet` at `shargain/notifications/views/api.py:15-18` uses `.all()` without user filtering
- Files: `shargain/notifications/views/api.py:15-18`
- Impact: Users can see all notification configs across all users. Data breach vulnerability.
- Fix approach: Override `get_queryset()` to filter by authenticated user. Example: `return NotificationConfig.objects.filter(user=self.request.user)`

## Known Bugs

**Potential NoneType error in OlxOffer parsing:**
- Symptoms: `AttributeError` when parsing OLX offers with missing or malformed JSON structure
- Files: `shargain/parsers/olx.py:31-37`, `shargain/parsers/olx.py:47-63`
- Trigger: Scraping OLX page where JSON structure doesn't match expected format (e.g., closed listing, regional variant)
- Workaround: Try/except around `OlxOffer.from_content()` calls in tasks. Currently no error handling.
- Root cause: Parser assumes data structure exists without validation. No error handling for malformed HTML.

**Unhandled None response in offer checking:**
- Symptoms: Task `check_for_closed_offers` crashes if `response` is None
- Files: `shargain/offers/tasks.py:52-58`
- Trigger: When `is_offer_closed()` returns `(url, None, False)` due to `ConnectionResetError`
- Workaround: None
- Root cause: Line 38-39 returns None for response on connection error, but line 54 tries to access `response.content` unconditionally

**Silent task failures in check_for_closed_offers:**
- Symptoms: Offers never marked as closed despite being removed from site
- Files: `shargain/offers/tasks.py:48-58`
- Trigger: Any network error or parsing failure
- Workaround: None
- Root cause: No exception handling. No logging of failures. Missing retry logic for transient network errors.

**Unsanitized attribute access in filter rules:**
- Symptoms: `AttributeError` if filter rule references non-existent Offer field
- Files: `shargain/offers/services/filter_service.py:113`
- Trigger: User creates filter with `field: "nonexistent_field"` in UI
- Workaround: None
- Root cause: Line 113 uses `getattr(offer, rule["field"], "")` but doesn't validate field name against safe list

## Security Considerations

**Request timeout insufficient for unreliable networks:**
- Risk: 10-second timeout is too aggressive for slow websites or high-latency connections. Offers may be marked as closed incorrectly.
- Files: `shargain/offers/tasks.py:36,75`, `shargain/parsers/olx.py:42`
- Current mitigation: Fixed 10-second timeout
- Recommendations: Make timeout configurable. Add exponential backoff retry logic. Log timeout failures separately. Consider increasing to 30-60 seconds for web scraping.

**No authentication on Telegram webhook endpoint:**
- Risk: Anyone can POST to `/api/telegram/webhook/` and trigger bot logic. Potential for abuse.
- Files: `shargain/notifications/views/api.py:21-28`
- Current mitigation: None visible
- Recommendations: Validate Telegram update signature using bot token. Check `X-Telegram-Bot-API-Secret-Header`. Rate limit endpoint. Only accept POST from Telegram IP addresses if possible.

**User password stored with multiple hashers:**
- Risk: Old bcrypt/pbkdf2 hashes supported indefinitely. If one algorithm is broken, compromised accounts can't be re-hashed automatically.
- Files: `shargain/settings/base.py:97-103`
- Current mitigation: Argon2 is preferred (line 100 order)
- Recommendations: Remove obsolete hashers (BCryptSHA256, BCrypt, PBKDF2SHA1). Keep only Argon2. Add middleware to auto-upgrade weak hashes on login.

**No rate limiting on authentication endpoints:**
- Risk: Brute force attacks on login endpoint feasible
- Files: `shargain/public_api/auth.py:61-91`
- Current mitigation: None
- Recommendations: Add rate limiting (e.g., 5 attempts per minute per IP). Use `django-ratelimit` or similar. Add exponential backoff.

**CSRF token generation without validation:**
- Risk: Signup endpoint doesn't validate email format during token generation
- Files: `shargain/public_api/auth.py:72-84`
- Current mitigation: None
- Recommendations: Add email validation. Send confirmation email before activation. Prevent signup during suspicious circumstances.

**FileField stored HTML without sanitization:**
- Risk: Source HTML files could contain malicious JavaScript if served directly
- Files: `shargain/offers/models.py:121`, `shargain/offers/tasks.py:54,78`
- Current mitigation: Stored as file not served directly (likely)
- Recommendations: Never serve raw HTML files. If HTML must be displayed, sanitize with `bleach` library. Store in non-web-accessible location.

## Performance Bottlenecks

**N+1 query in Offer queryset operations:**
- Problem: `scrapingurl_set.all()` called without prefetch causes extra queries per offer
- Files: `shargain/offers/application/dto.py` (if iterating offers)
- Cause: Accessing related objects without prefetch/select_related
- Improvement path: Use `Prefetch("scrapingurl_set")` in all list operations. Document pattern in CONVENTIONS.md.

**Inefficient filter evaluation for large offer lists:**
- Problem: `OfferFilterService.apply_filters()` iterates all offers in Python (line 37-40), evaluates complex rules
- Files: `shargain/offers/services/filter_service.py:23-40`
- Cause: No database-level filtering. All rule evaluation happens in application code.
- Improvement path: For simple filters (contains, not_contains), consider generating Django Q objects and applying at query time. Cache compiled rule expressions.

**Missing database indexes on frequently filtered fields:**
- Problem: Queries filter on `closed_at`, `created_at`, `url` but no explicit indexes
- Files: `shargain/offers/models.py:116-138`, `shargain/offers/tasks.py:49,69`
- Cause: Relying on automatic indexes
- Improvement path: Add `db_index=True` to `closed_at`, `created_at` fields. Add unique index on `url` if intended. Profile with Django Debug Toolbar.

**Synchronous HTTP requests block Celery workers:**
- Problem: `requests.get()` calls in Celery tasks are synchronous and tie up worker
- Files: `shargain/offers/tasks.py:36,75`, `shargain/parsers/olx.py:42`
- Cause: Using blocking requests library instead of async
- Improvement path: Use `httpx` with async/await or `requests` with connection pooling. Consider `aiohttp` for web scraping.

## Fragile Areas

**OLX Parser depends on exact HTML structure:**
- Files: `shargain/parsers/olx.py:24-38`
- Why fragile: Parser uses hardcoded selectors (`#olx-init-config`) and string manipulation (`splitlines()[4]`). Any OLX HTML change breaks parsing. No version detection.
- Safe modification: Add defensive checks for None values. Log actual HTML structure on failure. Add unit tests with real OLX HTML samples. Consider using dedicated scraping library or official API.
- Test coverage: Unit tests exist but only with mocked data. No integration tests with real OLX pages.

**Telegram bot command handling:**
- Files: `shargain/telegram/bot.py`, `shargain/telegram/application/setup_scraping_target_handler.py:102`
- Why fragile: Multiple handlers registered dynamically. State management relies on message context. No transaction guarantees.
- Safe modification: Add comprehensive logging at each handler step. Use Django transactions. Add state machine pattern for multi-step commands.
- Test coverage: Limited. Integration tests with real Telegram bot not present.

**Filter validation schema lacks comprehensive checks:**
- Files: `shargain/offers/schemas/offer_filter.py`, `shargain/offers/services/filter_service.py`
- Why fragile: Filter structure validated at endpoint but assumptions about field names not validated. Service code uses unsafe `getattr()`.
- Safe modification: Create whitelist of valid filter fields (`title`, `price`, `url`). Validate field names in schema. Add type checking for filter values.
- Test coverage: `test_filter_schemas.py` and `test_filter_service.py` exist but unclear coverage of edge cases.

## Scaling Limits

**Single-threaded Telegram bot:**
- Current capacity: Serial message processing. One command blocks others.
- Limit: ~10 messages/second before queue buildup
- Scaling path: Use webhook mode (already configured at `TELEGRAM_WEBHOOK_URL`). Async message processing with Celery. Multiple bot instances with load balancing.

**Offer HTML storage on filesystem:**
- Current capacity: Unlimited but slow to access. No deduplication.
- Limit: Disk space. I/O bottleneck on high volume.
- Scaling path: Move to S3 or CDN. Implement storage cleanup for closed offers. Compress HTML before storing.

**Database connection pool under load:**
- Current capacity: Default Django settings, likely 1-5 connections
- Limit: Connection exhaustion under concurrent requests
- Scaling path: Configure `DATABASES['default']['CONN_MAX_AGE']` and connection pooling (pgbouncer). Monitor with `django-health-check`.

**Celery worker capacity:**
- Current capacity: Default configuration, single worker
- Limit: Tasks queue up during network-heavy operations
- Scaling path: Run multiple workers. Use task routing. Implement priority queues. Add task timeouts to prevent hanging.

## Dependencies at Risk

**BeautifulSoup4 web scraping:**
- Risk: Parser is tightly coupled to OLX/Otomoto HTML. Sites update structure unexpectedly, causing parsing to fail silently.
- Impact: Offers not properly checked for closure. Users don't get notified of state changes.
- Migration plan: Consider `Scrapy` for robust, maintainable scraping. Or use official APIs (OLX has partner API). Add circuit breaker for sites that repeatedly fail parsing.

**Requests library without retries:**
- Risk: Network failures (timeouts, connection resets) cause immediate task failure
- Impact: Offers not fetched. Offers not checked for closure. Loss of data.
- Migration plan: Use `requests.Session()` with `urllib3.Retry` and `HTTPAdapter`. Or switch to `httpx` with async support. Add exponential backoff.

**Django-ninja for API (third-party validation):**
- Risk: Less battle-tested than Django REST Framework. Smaller community. May have compatibility issues with newer Django versions.
- Impact: API could break on Django upgrades. Security issues may be fixed slower.
- Migration plan: Keep eye on project activity. Ensure security updates tracked. Consider DRF as fallback if issues arise.

**Jazzmin admin theme:**
- Risk: Development dependency that could break on Django/Python version upgrades
- Impact: Admin interface unusable. Difficult to manage data without it.
- Migration plan: Ensure always tested in CI. Keep separate branch with vanilla Django admin as fallback.

## Missing Critical Features

**No transaction boundaries in offer updates:**
- Problem: `check_if_is_closed()` task updates `offer.closed_at` but doesn't verify offer still exists or is fresh
- Blocks: Accurate closure tracking. Race conditions possible.

**No audit logging:**
- Problem: No record of who changed what scraping targets/filters/configs or when
- Blocks: Debugging issues, compliance, user support

**No API versioning:**
- Problem: Single version of API. Breaking changes affect all clients.
- Blocks: Smooth upgrades. Client compatibility management.

**No webhooks for external integrations:**
- Problem: External systems can't be notified of offer changes without polling
- Blocks: Integration with other services (e.g., analytics, CRM)

**No data export:**
- Problem: Users can't export their scraping results or historical data
- Blocks: User retention. Data portability. Compliance with data regulations.

## Test Coverage Gaps

**Untested error cases in Celery tasks:**
- What's not tested: Network errors, malformed responses, database transaction failures
- Files: `shargain/offers/tasks.py`
- Risk: Production failures go unnoticed. Tasks fail silently. Data inconsistency.
- Priority: High

**No integration tests for Telegram bot:**
- What's not tested: Full message flow with bot. Multi-step command sequences. Error recovery.
- Files: `shargain/telegram/bot.py`, `shargain/telegram/application/`
- Risk: Bot breaks unexpectedly. Users experience errors. Features regress silently.
- Priority: High

**API authentication not thoroughly tested:**
- What's not tested: CSRF bypass attempts, session hijacking, concurrent login edge cases
- Files: `shargain/public_api/auth.py`
- Risk: Security vulnerabilities discovered in production only
- Priority: High

**Filter service edge cases untested:**
- What's not tested: Undefined fields in filter rules, deeply nested rule groups, malformed JSON
- Files: `shargain/offers/services/filter_service.py`
- Risk: User input can crash filtering. Notifications fail to send.
- Priority: Medium

**Database models missing constraint tests:**
- What's not tested: Uniqueness constraints, foreign key cascade behavior, null handling
- Files: `shargain/offers/models.py`, `shargain/accounts/models.py`
- Risk: Data integrity violations. Orphaned records.
- Priority: Medium

---

*Concerns audit: 2026-01-24*
