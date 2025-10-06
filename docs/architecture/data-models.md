# Data Models

## User (Final, Aligned with API)

**Purpose:** Represents an individual account on the platform. A user defines scraping targets to monitor for offers and configures how they receive notifications about new findings.

**Key Attributes:**
- `id`: `integer` - The unique, primary identifier for the user.
- `username`: `string` - The user's public-facing name.
- `email`: `string` - The user's private email address, used for login.
- `tier`: `string` - The user's subscription tier or access level.

### TypeScript Interface
```typescript
interface User {
  id: number;
  username: string;
  email: string;
  tier: string;
}
```

### Relationships
-   **One-to-Many:** A `User` has many `ScrappingTarget`s (via the `scraping_targets` related name).
-   **One-to-Many:** A `User` has many `NotificationConfig`s (via the `notification_configs` related name).

## ScrappingTarget

**Purpose:** A user-defined group that contains one or more specific URLs to be monitored for new offers. It serves as the central configuration for a scraping job, linking search pages to a notification channel.

**Key Attributes:**
- `id`: `integer` - The unique, primary identifier for the scraping target.
- `name`: `string` - A user-friendly name for the target group (e.g., "Looking for 15-inch laptops").
- `enable_notifications`: `boolean` - A master switch to enable or disable notifications for all offers found under this target.
- `is_active`: `boolean` - A master switch to enable or disable the scraping process for this target.

### TypeScript Interface
```typescript
interface ScrappingTarget {
  id: number;
  name: string;
  enable_notifications: boolean;
  is_active: boolean;
  notification_config: number | null; // ID of the NotificationConfig
  owner: string; // UUID of the User
  scraping_urls: ScrapingUrl[]; // Array of associated URLs to be scraped
}

// We will define this next, but including it here for context
interface ScrapingUrl {
  id: number;
  name: string;
  url: string;
  is_active: boolean;
}
```

### Relationships
-   **Many-to-One:** Belongs to a `User` (the `owner`).
-   **Many-to-One:** Can be linked to one `NotificationConfig`.
-   **One-to-Many:** Has many `ScrapingUrl`s, which contain the actual URLs to scrape.
-   **One-to-Many:** Has many `Offer`s found during scraping.

## ScrapingUrl

**Purpose:** Represents a single, specific URL that the system will actively monitor for offers. It is the "leaf" in the scraping configuration tree, belonging to a parent `ScrappingTarget`.

**Key Attributes:**
- `id`: `integer` - The unique, primary identifier for the scraping URL.
- `name`: `string` - A user-friendly, human-readable name for this specific URL (e.g., "OLX Laptops < $500").
- `url`: `string` - The full URL of the listings page to be scraped.
- `is_active`: `boolean` - A switch to enable or disable scraping for this specific URL.

### TypeScript Interface
```typescript
interface ScrapingUrl {
  id: number;
  name: string;
  url: string;
  is_active: boolean;
  scraping_target: number; // ID of the parent ScrappingTarget
}
```

### Relationships
-   **Many-to-One:** Belongs to a `ScrappingTarget`. The `on_delete=models.CASCADE` rule means if the parent `ScrappingTarget` is deleted, all of its associated `ScrapingUrl`s will also be deleted.
-   **One-to-Many:** Has many `ScrapingCheckin`s, which log the history of scraping attempts for this URL.

## Offer

**Purpose:** Represents a single item/listing discovered by the scraper on a target website. It contains all the relevant details of the listing, such as title, price, and image.

**Key Attributes:**
- `id`: `integer` - The unique, primary identifier for the offer in our system.
- `url`: `string` - The direct URL to the offer page on the source website.
- `title`: `string` - The title of the listing (e.g., "Slightly used MacBook Pro").
- `price`: `number` (optional) - The price of the item.
- `main_image_url`: `string` (optional) - The URL of the offer's primary image.
- `list_url`: `string` - The URL of the search/listing page where this offer was found.
- `published_at`: `DateTime` (optional) - The timestamp when the offer was originally published on the source website.
- `closed_at`: `DateTime` (optional) - The timestamp when our system detected that the offer was no longer available.
- `created_at`: `DateTime` - The timestamp when our system first discovered this offer.

### TypeScript Interface
```typescript
interface Offer {
  id: number;
  url: string;
  title: string;
  price?: number;
  main_image_url?: string;
  list_url: string;
  published_at?: string; // ISO 8601 DateTime
  closed_at?: string; // ISO 8601 DateTime
  created_at: string; // ISO 8601 DateTime
  target: number; // ID of the parent ScrappingTarget
}
```

### Relationships
-   **Many-to-One:** Belongs to a `ScrappingTarget`. The `on_delete=models.PROTECT` rule is a critical detail: it prevents a `ScrappingTarget` from being deleted if it has associated offers, thus preserving historical data.

## NotificationConfig

**Purpose:** Represents a configured destination channel for sending notifications about new offers. A user can create multiple configurations (e.g., one for Telegram, one for Discord) and assign them to their `ScrappingTarget`s.

**Key Attributes:**
- `id`: `integer` - The unique, primary identifier for the notification configuration.
- `name`: `string` - A user-friendly name for this configuration (e.g., "My Personal Telegram").
- `channel`: `string` - The type of notification channel. This will be an enum of available choices (e.g., "discord", "telegram").
- `register_token`: `string` - A unique token provided to the user to link their chat client (like Telegram) to this configuration.

### TypeScript Interface
```typescript
enum NotificationChannel {
  DISCORD = 'discord',
  TELEGRAM = 'telegram',
}

interface NotificationConfig {
  id: number;
  name: string;
  channel: NotificationChannel;
  register_token: string;
  owner: string; // UUID of the User
}
```

### Relationships
-   **Many-to-One:** Belongs to a `User` (the `owner`). If the user is deleted, this configuration is also deleted (`on_delete=models.CASCADE`).
-   **One-to-Many:** Can be used by many `ScrappingTarget`s.
