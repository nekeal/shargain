# Offer Inbox — Architecture & Changes Diagrams

This document visualizes the architecture, data models, ingest pipeline, and request lifecycles defined in [2026-11-07-offer-inbox-backend-design.md](file:///home/nekeal/projects/python/shargain/docs/superpowers/specs/2026-11-07-offer-inbox-backend-design.md).

---

## 1. Data Model Evolution (ER Diagram)

Replacing the single-purpose `OfferLike` model with `UserOfferState`, and capturing filter pass/fail status directly at ingest time via `passed_filters`.

```mermaid
erDiagram
    ScrappingTarget ||--o{ Offer : "owns"
    User ||--o{ UserOfferState : "tracks state for"
    Offer ||--o{ UserOfferState : "has state per user"
    ScrappingTarget ||--o| NotificationConfig : "routes to"

    Offer {
        int id PK
        int target_id FK
        string url
        string title
        int price
        string list_url
        boolean passed_filters "Snapshot: True/False/NULL"
        datetime created_at
        datetime closed_at
        json metadata
    }

    UserOfferState {
        int id PK
        int user_id FK
        int offer_id FK
        datetime seen_at "Nullable"
        datetime liked_at "Nullable"
        datetime created_at
    }

    User {
        int id PK
        string email
    }

    NotificationConfig {
        int id PK
        int owner_id FK "Telegram identity resolution"
        string chatid "Indexed"
    }
```

---

## 2. Component & Layer Architecture

Layer dependencies flow strictly inward. The HTTP API and Telegram bot act as thin transport adapters interacting through application-layer DTOs, queries, and commands without leaking ORM internals.

```mermaid
flowchart TD
    subgraph Transports["Transport Layer"]
        WebClient["Web Frontend / TS Client"]
        TelegramUser["Telegram Bot User"]
    end

    subgraph APIAdapters["API & Bot Adapters"]
        NinjaRouter["offers.api (Django Ninja Router)"]
        PublicAPI["public_api.api (Mounts router)"]
        BotHandlers["telegram.bot (Reply & Commands)"]
    end

    subgraph AppLayer["Application Layer (shargain/offers/application)"]
        DTOs["DTOs (PublicOffer, PublicOfferPage, OfferState)"]
        StateCommands["offer_state (mark_seen, like_offers, etc.)"]
        ListQuery["queries.list_public_offers"]
        StateQuery["queries.get_offer_states"]
    end

    subgraph DomainServices["Domain & Support Services"]
        FieldResolver["field_extraction (OfferFieldResolver)"]
        LocParser["location_parsers (LocationParserFactory)"]
        SnapshotService["services.filter_snapshot (OfferFilterSnapshotService)"]
    end

    subgraph Persistence["Database & Models"]
        DB[(PostgreSQL)]
        OfferModel["Offer Model"]
        StateModel["UserOfferState Model"]
    end

    WebClient --> PublicAPI
    PublicAPI --> NinjaRouter
    NinjaRouter --> ListQuery
    NinjaRouter --> StateCommands

    TelegramUser --> BotHandlers
    BotHandlers --> StateCommands

    ListQuery --> StateQuery
    ListQuery --> FieldResolver
    ListQuery --> LocParser
    ListQuery --> OfferModel
    StateQuery --> StateModel
    StateCommands --> StateModel
    SnapshotService --> OfferModel

    OfferModel --> DB
    StateModel --> DB
```

---

## 3. Ingest Pipeline: Filter Snapshot & Notification Decoupling

`OfferBatchCreateService` snapshots filter evaluation into `Offer.passed_filters` regardless of notification settings or delivery failures.

```mermaid
sequenceDiagram
    autonumber
    participant Scraper as Scraper / Ingest Job
    participant BatchCreate as OfferBatchCreateService
    participant DB as PostgreSQL
    participant Snapshot as OfferFilterSnapshotService
    participant NotifService as NotificationService

    Scraper->>BatchCreate: run(offers_data, target)
    BatchCreate->>DB: bulk_create(new_offers)
    
    rect rgb(240, 248, 255)
        note over BatchCreate,Snapshot: Ingest Filter Snapshot
        BatchCreate->>Snapshot: apply(new_created_offers, target)
        Snapshot->>Snapshot: Group by list_url & resolve ScrapingUrl
        Snapshot->>Snapshot: Extract fields & evaluate OfferFilterService
        Snapshot->>DB: bulk_update(passed_filters = True/False)
        Snapshot-->>BatchCreate: FilterSnapshotResult(passed, scraping_url_map)
    end

    alt Notifications enabled & config present
        BatchCreate->>NotifService: run(passed_offers)
    else Notifications disabled or quota exhausted
        note over BatchCreate: Inbox still populated with passed_filters = True
    end
```

---

## 4. Inbox Read Flow (`list_public_offers`)

Assembling the public read model with 100% database-side filtering (via `Exists` subqueries), column deferrals, single-query state hydration, and resilient in-memory projection for the paginated slice only.

```mermaid
sequenceDiagram
    autonumber
    participant Frontend as Web Client
    participant Router as offers.api
    participant Query as list_public_offers
    participant DB as PostgreSQL
    participant Resolver as FieldResolver & LocationParser

    Frontend->>Router: GET /api/public/targets/{id}/offers?seen=false&ordering=oldest
    Router->>Query: list_public_offers(actor, target_id, seen=False, liked=None, ordering="oldest", limit=20, offset=0)
    
    note over Query,DB: 100% DB-Side Filtering (Zero Python in-memory filtering)
    Query->>DB: SQL: target_id, passed_filters=True, NOT EXISTS(user_offer_state where seen_at IS NOT NULL), defer("source_html")
    Query->>DB: Fetch page slice (e.g. 20 items) + total count (offer_inbox_idx)
    
    Query->>DB: get_offer_states(actor, page_offer_ids) [Single hydration query for 20 IDs]
    
    loop For each offer in 20-item page slice
        Query->>Resolver: Extract attributes & location (Fail-safe try/catch)
        alt Extraction succeeds
            Resolver-->>Query: OfferAttribute list & OfferLocation
        else Extraction raises exception
            Resolver-->>Query: Fallback (attributes=[], location=None)
        end
    end
    
    Query-->>Router: PublicOfferPage(count, items=[PublicOffer, ...])
    Router-->>Frontend: 200 OK (LimitOffset JSON)
```

---

## 5. State Transition Lifecycle (`UserOfferState`)

Illustrates state persistence, idempotency, and the `CheckConstraint` deletion rules.

```mermaid
stateDiagram-v2
    [*] --> Unseen_Unliked : Default state (No DB row)

    Unseen_Unliked --> Seen_Only : mark_seen (Create row with seen_at)
    Unseen_Unliked --> Liked_Only : like_offer (Create row with liked_at)

    Seen_Only --> Both_Seen_And_Liked : like_offer (Update liked_at)
    Liked_Only --> Both_Seen_And_Liked : mark_seen (Update seen_at)

    Both_Seen_And_Liked --> Liked_Only : mark_unseen (Clear seen_at)
    Both_Seen_And_Liked --> Seen_Only : unlike_offer (Clear liked_at)

    Seen_Only --> Unseen_Unliked : mark_unseen (Delete row to satisfy CheckConstraint)
    Liked_Only --> Unseen_Unliked : unlike_offer (Delete row to satisfy CheckConstraint)
```
