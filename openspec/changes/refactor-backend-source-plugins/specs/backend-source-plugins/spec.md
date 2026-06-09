## ADDED Requirements

### Requirement: Backend selects a source plugin by URL
The system SHALL select a first-party backend source plugin for notification preparation using explicit URL matching against the configured scraping URL when available, and against the offer URL as a fallback.

#### Scenario: Scraping URL matches OLX
- **WHEN** a new offer belongs to a `ScrapingUrl` whose URL host is an OLX host
- **THEN** the system uses the OLX source plugin to prepare source-specific notification details

#### Scenario: Scraping URL matches Otodom
- **WHEN** a new offer belongs to a `ScrapingUrl` whose URL host is an Otodom host
- **THEN** the system uses the Otodom source plugin to prepare source-specific notification details

#### Scenario: Scraping URL is missing for an offer
- **WHEN** a new offer has no matching `ScrapingUrl` configuration for its `list_url`
- **THEN** the system attempts source plugin selection using the offer URL

#### Scenario: No source plugin matches
- **WHEN** no source plugin matches the scraping URL or offer URL
- **THEN** the system uses fallback behavior that emits no source-specific notification details and does not block notification delivery

### Requirement: Source plugins produce final notification lines
Source plugins SHALL produce final notification lines including location details and waypoint distances when applicable. The plugin output SHALL be a simple list of text strings.

#### Scenario: OLX offer with coordinates produces location lines and distance lines
- **WHEN** an OLX offer metadata payload contains map latitude and longitude values and its `ScrapingUrl` has waypoints configured
- **THEN** the OLX plugin produces lines including a map link with appropriate emoji prefix and distance lines from the offer coordinates to each configured waypoint

#### Scenario: OLX offer with approximate coordinates uses different icon
- **WHEN** an OLX offer metadata payload has map coordinates but `show_detailed` is false
- **THEN** the OLX plugin produces lines using a less precise location emoji prefix

#### Scenario: OLX offer contains city and district location metadata
- **WHEN** an OLX offer metadata payload contains city and district values
- **THEN** the OLX plugin produces a location name line composed from available location values

#### Scenario: Otodom offer contains city and street metadata
- **WHEN** an Otodom offer metadata payload contains city and street address values
- **THEN** the Otodom plugin produces an address-based location name line and an address-based Google Maps search URL line

#### Scenario: Otodom offer has no coordinates with waypoints
- **WHEN** an Otodom offer has no coordinate data but its `ScrapingUrl` has waypoints configured
- **THEN** the Otodom plugin produces address/map-search lines and no distance lines

#### Scenario: Source metadata is malformed
- **WHEN** a source plugin receives missing or malformed metadata
- **THEN** the plugin returns no unavailable source-specific notification lines and notification delivery continues

#### Scenario: Location notifications are disabled
- **WHEN** a `ScrapingUrl` has `show_location_map_in_notifications` disabled
- **THEN** the selected plugin receives `show_location_details=False` and returns empty notification lines

### Requirement: Notification pipeline uses plugin-prepared source details
The system SHALL prepare source-specific notification details through the source plugin system before rendering notification messages.

#### Scenario: Location notifications are enabled
- **WHEN** a `ScrapingUrl` has `show_location_map_in_notifications` enabled
- **THEN** notification lines from the selected plugin are included below the shared notification header

#### Scenario: Location notifications are disabled
- **WHEN** a `ScrapingUrl` has `show_location_map_in_notifications` disabled
- **THEN** no plugin-provided location map, location name, or waypoint distance lines are included in notifications

### Requirement: Shared notification header remains source-independent
The system SHALL continue to render the shared offer header independently of source plugins.

#### Scenario: Notification message is rendered
- **WHEN** a notification message is created for a new offer
- **THEN** the message includes the offer title, published time, price, and URL using the shared notification renderer

#### Scenario: Source plugin emits no details
- **WHEN** the selected source plugin emits no source-specific notification details
- **THEN** the notification still includes the shared offer header

#### Scenario: Plugin notification lines are rendered below header
- **WHEN** a plugin returns notification lines
- **THEN** each line is rendered below the shared header as-is

### Requirement: Existing filters and frontend contracts remain unchanged
The system SHALL preserve existing notification filter behavior and public frontend-facing API contracts during this backend plugin refactor.

#### Scenario: Existing title filter is configured
- **WHEN** a `ScrapingUrl` has a title-based notification filter configured
- **THEN** the system applies the existing filter behavior before sending notifications

#### Scenario: Plugin-specific fields exist internally
- **WHEN** a source plugin extracts source-specific details
- **THEN** those details are not exposed as frontend filter fields in this change

#### Scenario: Frontend reads scraping URL settings
- **WHEN** the frontend fetches scraping URLs through the existing public API
- **THEN** the response shape for filters, `showLocationMapInNotifications`, and `waypoints` remains unchanged

### Requirement: Source plugin registry is static and first-party
The system SHALL use a static first-party backend registry for source plugins in this change.

#### Scenario: Application starts
- **WHEN** Django imports the source plugin registry
- **THEN** all registered first-party plugins are available without database lookup or dynamic discovery

#### Scenario: New first-party source is added later
- **WHEN** a developer adds support for a new source
- **THEN** the developer registers the new plugin and URL matcher in backend code without changing generic notification orchestration
