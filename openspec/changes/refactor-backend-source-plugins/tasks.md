## 1. Source Plugin Contracts and Registry

- [ ] 1.1a Test that URL matcher matches OLX hosts.
- [ ] 1.1b Implement OLX URL matcher.
- [ ] 1.1c Test that URL matcher matches Otodom hosts.
- [ ] 1.1d Implement Otodom URL matcher.
- [ ] 1.1e Test that URL matcher rejects unsupported hosts.
- [ ] 1.1f Test substring safety (e.g. "olx" inside longer domain does not match).
- [ ] 1.2 Define plugin contract types (`SourcePlugin` protocol, `NotificationLine`, `SourceNotificationDetails`, `LegacyUrlNotificationSettings`), URL matcher protocol, `PluginRegistration` dataclass, and static registry skeleton.
- [ ] 1.3a Test that registry selects plugin by URL, preferring a configured scraping URL when present.
- [ ] 1.3b Implement registry selection preferring scraping URL.
- [ ] 1.3c Test that registry falls back to offer URL when no scraping URL is available.
- [ ] 1.3d Implement fallback selection and fallback plugin behavior for unmatched URLs.
- [ ] 1.4 Test that when the module is imported, the static registry contains registered OLX and Otodom plugins (no DB lookup required).

## 2. OLX Source Plugin

- [ ] 2.1a Test OLX `build_notification_details()` with coordinate metadata: produces a map link line with correct icon.
- [ ] 2.1b Implement coordinate → map link in OLX plugin (no waypoints yet).
- [ ] 2.1c Test OLX with waypoints configured: produces distance lines via `haversine()`.
- [ ] 2.1d Implement distance computation from waypoints in OLX plugin.
- [ ] 2.2a Test OLX with approximate coordinates (`show_detailed=false`): produces appropriate icon for approximate location.
- [ ] 2.2b Implement approximate-coordinates icon choice.
- [ ] 2.2c Test OLX with city/district metadata (no coordinates): produces location name line with correct icon.
- [ ] 2.2d Implement city/district location name line.
- [ ] 2.3 Test OLX with malformed or empty metadata: returns empty lines gracefully.
- [ ] 2.4 Test OLX with `show_location_details=False`: returns empty lines.
- [ ] 2.5 Tie off: wire error-handling into OLX plugin implementation to pass 2.3 and 2.4.

## 3. Otodom and Fallback Source Plugins

- [ ] 3.1a Test Otodom `build_notification_details()` with city-and-street metadata: produces address-based location line with correct icon.
- [ ] 3.1b Implement city+street address line in Otodom plugin.
- [ ] 3.1c Test Otodom produces a Google Maps search URL line when address is available.
- [ ] 3.1d Implement Google Maps search URL line.
- [ ] 3.2a Test Otodom with city-only metadata: produces correct location line.
- [ ] 3.2b Implement city-only handling.
- [ ] 3.2c Test Otodom with malformed metadata: returns empty lines gracefully.
- [ ] 3.2d Implement malformed metadata handling.
- [ ] 3.3 Test Otodom with waypoints configured but no coordinates: verifies no distance lines are produced.
- [ ] 3.4 Test fallback plugin returns no notification lines regardless of input.
- [ ] 3.5 Implement fallback source plugin.

## 4. Source Notification Context Builder

- [ ] 4.1a Test builder with `show_location_details=False`: plugin is called with flag set, no extra lines in context.
- [ ] 4.1b Implement builder dispatch that passes `show_location_details` to plugin.
- [ ] 4.2a Test builder with OLX plugin and enabled details: plugin-produced lines appear as `extra_lines`.
- [ ] 4.2b Implement builder that collects plugin lines into `extra_lines`.
- [ ] 4.2c Test builder with OLX and waypoints: waypoints passed in settings, distance lines in output.
- [ ] 4.2d Implement waypoints pass-through in builder.
- [ ] 4.3 Test builder with Otodom plugin and waypoints: address/map-search lines but no distance lines.
- [ ] 4.4 Tie off: implement `SourceNotificationContextBuilder` selection logic.

## 5. Notification Rendering Integration

- [ ] 5.0 Test that `NotificationMessageContext` accepts `extra_lines` field and rejects removed field names (`map_url`, `location_name`, `is_exact_location`, `distances`).
- [ ] 5.1 Test that shared notification header rendering is unchanged when source-specific extra lines are present.
- [ ] 5.2 Test that notification with no extra lines still renders title, published time, price, and URL.
- [ ] 5.3 Update `NotificationMessageContext` to replace old source-specific fields with `extra_lines: list[NotificationLine]`.
- [ ] 5.4 Update `NewOfferNotificationService` to render plugin-produced `extra_lines` below the shared header while preserving existing message batching behavior.

## 6. Batch Create Integration

- [ ] 6.1 Add or update batch create tests proving title filters still run before notification context construction.
- [ ] 6.2 Add or update batch create tests proving `_notify()` delegates source-specific context construction and does not call `LocationParserFactory`.
- [ ] 6.3 Refactor `OfferBatchCreateService._notify()` to use `SourceNotificationContextBuilder` instead of direct location parser imports and source-specific parsing.
- [ ] 6.4a Add API schema snapshot test that public schemas and frontend-facing response fields are unchanged.
- [ ] 6.4b Verify by running snapshot test and confirming no unexpected response shape changes.

## 7. Cleanup and Verification

- [ ] 7.1a Test that no code imports `LocationParserFactory` from old location.
- [ ] 7.1b Remove `LocationParserFactory` and old parser classes if no callers remain.
- [ ] 7.2 Move or rewrite existing location parser tests so source behavior is covered through plugin tests.
- [ ] 7.3 Run targeted backend tests for source plugins, notification rendering, filter service, and batch create.
- [ ] 7.4 Run full backend test suite with `make test`.
- [ ] 7.5 Run backend quality checks with `make quality-check`.
