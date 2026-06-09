## Context

The current notification pipeline builds source-specific location details in `OfferBatchCreateService._notify()`. It imports `LocationParserFactory`, chooses a parser from `offer.domain`, extracts map URL/location/exactness, calculates waypoint distances, and then passes a `NotificationMessageContext` to `NewOfferNotificationService`.

That makes the batch service responsible for source-specific parsing knowledge and makes each new source a change to generic orchestration code. The existing frontend and API already expose `show_location_map_in_notifications` and `waypoints`; those settings must continue to work unchanged. Filtering is intentionally out of scope and remains title-only for this change.

The first implementation targets OLX and Otodom behavior. Otomoto should remain supported by a fallback plugin that emits no source-specific notification lines until its metadata format is known.

## Goals / Non-Goals

**Goals:**

- Move OLX and Otodom source-specific notification behavior into cohesive backend plugins.
- Keep plugin matching separate from plugin behavior, avoiding a `domain_patterns` field on the plugin interface.
- Remove direct use of `LocationParserFactory` from batch notification orchestration.
- Preserve current notification behavior for OLX and Otodom, including map links, location names, exact-location icon behavior, and waypoint distances where coordinates exist.
- Preserve current frontend/API behavior and persisted `ScrapingUrl` fields.
- Keep the design modular enough that a future Otomoto plugin can be added without modifying generic notification orchestration.

**Non-Goals:**

- No frontend changes.
- No plugin-based filtering or plugin field definitions for the filter UI.
- No dynamic plugin discovery through Django `AppConfig.ready()`.
- No database-backed plugin registry.
- No geocoding implementation for Otodom in this change.
- No `plugin_config` JSONField migration in this change.
- No external source plugin ecosystem; plugins are first-party backend code.

## Decisions

### 1. Registry Owns URL Matching, Plugins Own Source Behavior

Use a static registry of `PluginRegistration` objects. Each registration pairs a plugin instance with a matcher object/function. The plugin interface itself does not expose `domain_patterns`.

Recommended shape:

```python
@dataclass(frozen=True)
class PluginRegistration:
    plugin: SourcePlugin
    matcher: SourceUrlMatcher

class SourceUrlMatcher(Protocol):
    def matches(self, url: str) -> bool: ...

class SourcePlugin(Protocol):
    id: str
    display_name: str

    def build_notification_details(
        self,
        offer: SourceOfferInput,
        settings: LegacyUrlNotificationSettings,
    ) -> SourceNotificationDetails: ...
```

Rationale: URL matching and plugin behavior change for different reasons. Keeping matching in the registry avoids unclear pattern semantics on the plugin interface and makes matching logic explicit and testable. A plugin remains cohesive: it understands one source's metadata and notification presentation.

Alternative considered: `SourcePlugin.get_domain_patterns()`. Rejected because it exposes matching mechanics as plugin API, leaves pattern semantics ambiguous, and encourages substring matching mistakes like matching `olx` inside an unrelated domain.

### 2. Single `build_notification_details()` Method — No `extract()` / `enrich()` Split

The plugin interface has one method that receives the raw offer metadata plus current notification settings and returns final notification lines. No intermediate fact extraction step.

Recommended shape:

```python
@dataclass(frozen=True)
class SourceOfferInput:
    url: str
    metadata: Mapping[str, Any]

@dataclass(frozen=True)
class LegacyUrlNotificationSettings:
    show_location_details: bool
    waypoints: list[WaypointData]

@dataclass(frozen=True)
class NotificationLine:
    text: str

@dataclass(frozen=True)
class SourceNotificationDetails:
    lines: list[NotificationLine]
```

Rationale: a single method avoids premature abstraction. Since filtering is descoped, there is no consumer of extracted facts separate from notification rendering. Adding `extract()` + `enrich()` + `notification_lines()` now would force every plugin to implement three methods when the only use case is build-notification.

Alternative considered: `extract(metadata) -> SourceFacts` followed by `notification_lines(facts, settings) -> list[NotificationLine]`. Rejected because `SourceFacts` would need to be a generic intermediate type that all plugins share. That would either be too vague (raw dict) or too location-centric (`SourceLocationFacts`). Either case recreates the rigidity of the current location parser hierarchy.

Future extension: if plugin fields are later exposed for filtering, add a separate `extract(metadata) -> Mapping[str, FieldValue]` method then. Do not add it now.

### 3. Plugin Computes Distances Internally Using `haversine()`

The plugin receives the full `LegacyUrlNotificationSettings` including `waypoints`. If the plugin has coordinate data (OLX), it imports `haversine()` from `shargain.offers.services.geo_utils`, computes distances, and includes distance lines in its output. If the plugin has no coordinate data (Otodom), it ignores `waypoints` and returns address/map-search lines only.

Rationale: this keeps `SourceNotificationDetails` simple — one field, `lines`. There is no `distance_origin` or `Coordinates` on the output. The generic context builder has no distance computation logic. Each plugin is fully cohesive: it knows its own metadata shape, its own notification lines, and whether it handles waypoints.

Alternative considered: plugin returns `distance_origin: Coordinates | None` and the generic builder computes distances. Rejected because it introduces source-specific location types into the generic contract and splits distance computation across plugin and builder.

### 4. Plugin Owns Full Line Formatting Including Icons

Each plugin formats its own lines including emoji or text prefixes. The notification service renders lines as-is below the shared header. A `NotificationLine` is simply a text string — the plugin embeds any icon directly in the text.

Rationale: OLX uses `📍` for exact coordinates and `🗺️` for approximate. Otodom uses a map pin or no icon. A future car listing plugin may use `🚗` for mileage and `⛽` for fuel type. A separate `icon` field would need to be joined to `text` for rendering anyway, so keeping them fused simplifies the contract.

Alternative considered: structured `text` + `icon` fields. Rejected because no consumer needs them separate in this iteration. If a future notification channel (e.g., rich push notification) needs structured icon data, add the field then.

### 5. Move Plugin Orchestration Out of `OfferBatchCreateService`

Add a small backend service responsible for turning offers plus a `ScrapingUrl` into notification contexts. The batch service should group offers, apply existing filters, fetch the `ScrapingUrl`, then delegate plugin-specific notification context construction.

Recommended shape:

```python
class SourceNotificationContextBuilder:
    def build_contexts(
        self,
        offers: list[Offer],
        scraping_url: ScrapingUrl | None,
    ) -> list[NotificationMessageContext]: ...
```

The builder selects a plugin using the scraping URL when available, falling back to the offer URL. When `show_location_details` is false, it calls the plugin with `show_location_details=False` — the plugin returns empty `lines`, and the builder produces a context with no extra lines. When `show_location_details` is true, the plugin returns full lines including distances if applicable.

Rationale: `OfferBatchCreateService` should orchestrate batch persistence, grouping, filtering, and notification sending. It should not know about OLX/Otodom metadata shapes or plugin selection internals.

Alternative considered: put plugin selection directly in `NewOfferNotificationService`. Rejected because notification rendering should not depend on `ScrapingUrl` configuration or source metadata extraction. It should render already-prepared contexts.

### 6. Keep Shared Notification Header Centralized

`NewOfferNotificationService` continues to render title, published time, price, and URL. Plugins only provide additional notification lines below the shared header.

`NotificationMessageContext` evolves from source-specific fields (`map_url`, `location_name`, `is_exact_location`, `distances`) toward generic `extra_lines: list[NotificationLine]`. The builder collects plugin-produced lines.

Rationale: the notification header is not source-specific and should remain consistent across all plugins. Extra lines give plugins source-specific control without owning the whole message format.

Alternative considered: plugins render full offer messages. Rejected because that would duplicate shared header logic, split Telegram message-length concerns, and make multi-offer batching harder to keep consistent.

### 7. Preserve Existing Settings as Legacy Interface

`LegacyUrlNotificationSettings` directly maps to current `ScrapingUrl` fields: `show_location_map_in_notifications` (renamed to `show_location_details`) and `waypoints`. No `plugin_config` is added in this change.

The name is explicit: this is today's persisted config, not the future plugin configuration model. When different plugins need different options, add a generic `plugin_config: dict | None` field then.

Rationale: this keeps the change backend-only and avoids frontend/API migrations. It also allows the plugin refactor to be verified against existing tests and behavior.

## Risks / Trade-offs

- Plugin selection by scraping URL may differ from offer URL if the scraper sends a mismatched `list_url` → Prefer `ScrapingUrl.url` for configuration, fall back to `offer.url`, and log when no scraping URL is found.
- Moving to `extra_lines` may subtly change notification formatting order → Add tests that assert OLX and Otodom message output remains equivalent to current behavior.
- Static registry requires code changes for new first-party plugins → Acceptable for the current curated-source scope and safer than auto-discovery.
- No geocoding abstraction yet means Otodom still cannot compute waypoint distances → Explicitly out of scope; the design leaves room for a later shared batch geocoding service.
- Calling `show_location_details=False` still invokes the plugin → The design intentionally passes the flag in rather than skipping the plugin, to keep behavior generic across all plugins.
- OLX plugin needs `haversine()` imported from a shared utility → Acceptable; haversine is already a pure function in `geo_utils.py`, and the plugin imports it the same way any other service would.

## Migration Plan

1. Add plugin contracts (`SourcePlugin`, `NotificationLine`, `SourceNotificationDetails`, `SourceOfferInput`, `LegacyUrlNotificationSettings`), static registry, and URL matchers.
2. Implement OLX, Otodom, and fallback plugins with behavior equivalent to current parsers.
3. Add `SourceNotificationContextBuilder` and update `_notify()` to use it instead of `LocationParserFactory`.
4. Update `NotificationMessageContext` and notification rendering to support `extra_lines` while preserving the shared header.
5. Rewrite or move location parser tests to plugin tests.
6. Run backend tests and verify notification output parity.
7. Remove `LocationParserFactory` if no callers remain.

Rollback strategy: keep the changes contained behind the new builder. If plugin behavior fails during implementation, `_notify()` can temporarily be switched back to `LocationParserFactory` before removing legacy code.

## Resolved Design Questions

- Plugin decides icons embedded in line text — `NotificationLine` is a plain string, not a `text+icon` struct.
- `SourceNotificationDetails` has one field: `lines`. No `distance_origin`, no `Coordinates`, no `SourceLocationFacts`.
- Plugin receives waypoints and computes distances internally using `haversine()`.
- Plugin receives `show_location_details=False` and returns empty `lines` when location details are disabled.
- Legacy settings mapped from current `ScrapingUrl` fields, named `LegacyUrlNotificationSettings` to indicate it is not the future plugin config model.
- Notification service renders `extra_lines` from `NotificationMessageContext` below the shared header.
- `NotificationMessageContext` drops `map_url`, `location_name`, `is_exact_location`, `distances`, and `get_distances()`. Replaced by `extra_lines: list[NotificationLine]`.
