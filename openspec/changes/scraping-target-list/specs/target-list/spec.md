## ADDED Requirements

### Requirement: List user's scraping targets
The system SHALL expose an endpoint that returns all scraping targets belonging to the authenticated user, without deep URL data.

#### Scenario: User has multiple targets
- **WHEN** the authenticated user has 3 scraping targets
- **THEN** the list endpoint SHALL return an array of 3 items, each with id, name, is_active, enable_notifications, and url_count

#### Scenario: User has a single target
- **WHEN** the authenticated user has exactly 1 scraping target
- **THEN** the list endpoint SHALL return an array of 1 item

#### Scenario: User has no targets
- **WHEN** the authenticated user has 0 scraping targets
- **THEN** the list endpoint SHALL return an empty array

### Requirement: Dashboard shows target list when >1 target
The frontend dashboard SHALL detect how many targets the user has and show a target selector only when there are multiple targets.

#### Scenario: Single target — no selector shown
- **WHEN** the user has exactly 1 scraping target
- **THEN** the dashboard SHALL load that target directly, without showing any target list UI

#### Scenario: Multiple targets — selector shown
- **WHEN** the user has 3 scraping targets
- **THEN** the dashboard SHALL display a target list/selector instead of immediately showing a single target's details

### Requirement: Select target and view its details
The user SHALL be able to select a target from the list and see that target's full details (URLs, filters, settings) in the existing dashboard layout.

#### Scenario: Select a target
- **WHEN** the user clicks on a target in the list
- **THEN** the dashboard SHALL load and display that target's full data (URLs, filters, settings) using the existing MonitoredWebsites, MonitorSettings, and DashboardSidebar components

#### Scenario: Switch between targets
- **WHEN** the user is viewing target A and selects target B
- **THEN** the dashboard SHALL unload target A and load target B's full data

### Requirement: Persist last selected target in localStorage
The system SHALL persist the last selected target ID in localStorage so the user's choice survives page reloads.

#### Scenario: Selection persists across reload
- **WHEN** the user selects target B from the list
- **THEN** the selected target ID SHALL be saved to localStorage
- **THEN** on page reload, the dashboard SHALL load target B directly instead of the default target

#### Scenario: Stored target no longer exists
- **WHEN** the user reloads and the stored target ID was deleted in admin
- **THEN** the dashboard SHALL fall back to the default target (my-target) and clear the stale localStorage entry
