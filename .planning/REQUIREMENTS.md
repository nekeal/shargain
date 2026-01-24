# Requirements: Multi-Channel Notifications

**Defined:** 2026-01-24
**Core Value:** Users can receive offer notifications on all their preferred channels from a single scraping target.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Backend/Model Layer

- [ ] **BACK-01**: M2M relationship between ScrappingTarget and NotificationConfig (replace single FK)
- [ ] **BACK-02**: Migration preserves existing single-config relationships (no data loss)
- [ ] **BACK-03**: Webhook channel type added to NotificationChannelChoices
- [ ] **BACK-04**: WebhookNotificationSender implements BaseNotificationSender

### Service Layer

- [ ] **SERV-01**: NewOfferNotificationService iterates over all target channels and sends to each
- [ ] **SERV-02**: send_test_notification command supports sending to all configured channels
- [ ] **SERV-03**: OfferBatchCreateService._notify() updated for M2M relationship

### API Layer

- [ ] **API-01**: Endpoint to add notification config to target
- [ ] **API-02**: Endpoint to remove notification config from target
- [ ] **API-03**: Endpoint to list notification configs for a target
- [ ] **API-04**: Target detail endpoint includes associated notification configs

### Frontend

- [ ] **FRNT-01**: UI to create and add notification configs directly per scraping target
- [ ] **FRNT-02**: Display list of associated notification configs on target detail
- [ ] **FRNT-03**: Ability to remove notification config from target

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Reliability

- **REL-01**: Retry logic with exponential backoff for webhook failures
- **REL-02**: Notification delivery status tracking
- **REL-03**: Dead letter queue for failed notifications

### Customization

- **CUST-01**: Per-channel message formatting
- **CUST-02**: Per-channel filtering rules

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Discord integration fix | Broken, not priority for this milestone |
| Per-channel filtering | All channels get same notifications — simplifies UX |
| Notification templates | Same format across all channels for now |
| Rate limiting | Defer unless issues arise |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| BACK-01 | TBD | Pending |
| BACK-02 | TBD | Pending |
| BACK-03 | TBD | Pending |
| BACK-04 | TBD | Pending |
| SERV-01 | TBD | Pending |
| SERV-02 | TBD | Pending |
| SERV-03 | TBD | Pending |
| API-01 | TBD | Pending |
| API-02 | TBD | Pending |
| API-03 | TBD | Pending |
| API-04 | TBD | Pending |
| FRNT-01 | TBD | Pending |
| FRNT-02 | TBD | Pending |
| FRNT-03 | TBD | Pending |

**Coverage:**
- v1 requirements: 14 total
- Mapped to phases: 0
- Unmapped: 14 ⚠️

---
*Requirements defined: 2026-01-24*
*Last updated: 2026-01-24 after initial definition*
