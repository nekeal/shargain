# Roadmap: Multi-Channel Notifications

## Overview

This roadmap transforms Shargain from single-channel to multi-channel notifications per scraping target. Starting with database model changes to support M2M relationships, we build upward through service layer updates, new channel types (webhook), API endpoints, and finally the frontend UI. Each phase delivers a complete, testable layer that the next phase builds upon.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Model Foundation** - M2M relationship replacing single FK
- [ ] **Phase 2: Webhook Channel** - Add webhook as a notification channel type
- [ ] **Phase 3: Service Layer** - Update notification services for multi-channel dispatch
- [ ] **Phase 4: API Layer** - Endpoints for managing channel associations
- [ ] **Phase 5: Frontend** - UI for multi-channel configuration per target

## Phase Details

### Phase 1: Model Foundation
**Goal**: Database supports multiple notification configs per scraping target
**Depends on**: Nothing (first phase)
**Requirements**: BACK-01, BACK-02
**Success Criteria** (what must be TRUE):
  1. ScrappingTarget can be associated with multiple NotificationConfig records
  2. Existing single-config relationships are preserved after migration (no data loss)
  3. Django admin shows M2M relationship for target notification configs
**Plans**: TBD

Plans:
- [ ] 01-01: M2M model change and migration

### Phase 2: Webhook Channel
**Goal**: Webhook is available as a notification channel type alongside Telegram
**Depends on**: Phase 1
**Requirements**: BACK-03, BACK-04
**Success Criteria** (what must be TRUE):
  1. User can create a NotificationConfig with channel type "webhook"
  2. WebhookNotificationSender successfully POSTs to a URL when triggered
  3. Webhook channel appears in channel type choices in Django admin
**Plans**: TBD

Plans:
- [ ] 02-01: Webhook channel type and sender implementation

### Phase 3: Service Layer
**Goal**: Notification dispatch sends to all configured channels for a target
**Depends on**: Phase 1, Phase 2
**Requirements**: SERV-01, SERV-02, SERV-03
**Success Criteria** (what must be TRUE):
  1. When offers are found, all configured channels for the target receive notifications
  2. send_test_notification command sends to all channels on a target
  3. OfferBatchCreateService correctly triggers multi-channel notifications
**Plans**: TBD

Plans:
- [ ] 03-01: Update notification services for multi-channel dispatch

### Phase 4: API Layer
**Goal**: API endpoints allow managing notification config associations per target
**Depends on**: Phase 3
**Requirements**: API-01, API-02, API-03, API-04
**Success Criteria** (what must be TRUE):
  1. Client can add a notification config to a target via API
  2. Client can remove a notification config from a target via API
  3. Client can list all notification configs for a target via API
  4. Target detail endpoint returns associated notification configs
**Plans**: TBD

Plans:
- [ ] 04-01: Channel association endpoints

### Phase 5: Frontend
**Goal**: Users can configure multiple notification channels per target through the UI
**Depends on**: Phase 4
**Requirements**: FRNT-01, FRNT-02, FRNT-03
**Success Criteria** (what must be TRUE):
  1. User can create and add notification configs directly from target detail page
  2. User can see all associated notification configs on target detail page
  3. User can remove a notification config from a target via UI
**Plans**: TBD

Plans:
- [ ] 05-01: Multi-channel UI components

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Model Foundation | 0/1 | Not started | - |
| 2. Webhook Channel | 0/1 | Not started | - |
| 3. Service Layer | 0/1 | Not started | - |
| 4. API Layer | 0/1 | Not started | - |
| 5. Frontend | 0/1 | Not started | - |

---
*Roadmap created: 2026-01-24*
