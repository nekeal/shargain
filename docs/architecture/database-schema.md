# Database Schema

This section provides the definitive database schema as SQL DDL (Data Definition Language) statements for PostgreSQL. This reflects the Django models and their relationships.

```sql
-- Note: This schema is a representation of the Django models.
-- Django automatically creates tables like 'accounts_user' based on the app and model name.

-- Represents the core user model, likely extending Django's built-in AbstractUser.
CREATE TABLE "accounts_user" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "password" varchar(128) NOT NULL,
    "last_login" timestamptz NULL,
    "is_superuser" boolean NOT NULL,
    "username" varchar(150) NOT NULL UNIQUE,
    "first_name" varchar(150) NOT NULL,
    "last_name" varchar(150) NOT NULL,
    "email" varchar(254) NOT NULL,
    "is_staff" boolean NOT NULL,
    "is_active" boolean NOT NULL,
    "date_joined" timestamptz NOT NULL,
    "tier" varchar(50) NOT NULL DEFAULT 'free'
);

-- Configuration for a notification channel (e.g., Telegram, Discord).
CREATE TABLE "notifications_notificationconfig" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "channel" varchar(50) NOT NULL, -- e.g., 'telegram', 'discord'
    "register_token" varchar(255) NOT NULL UNIQUE,
    "owner_id" bigint NOT NULL REFERENCES "accounts_user" ("id") ON DELETE CASCADE
);

-- A group of URLs to be scraped, linked to a user and a notification channel.
CREATE TABLE "offers_scrappingtarget" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "name" varchar(200) NOT NULL,
    "enable_notifications" boolean NOT NULL,
    "is_active" boolean NOT NULL,
    "notification_config_id" bigint NULL REFERENCES "notifications_notificationconfig" ("id") ON DELETE SET NULL,
    "owner_id" bigint NOT NULL REFERENCES "accounts_user" ("id") ON DELETE CASCADE
);

-- A single URL to be scraped, belonging to a ScrappingTarget.
CREATE TABLE "offers_scrapingurl" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "name" varchar(200) NOT NULL,
    "url" text NOT NULL,
    "is_active" boolean NOT NULL,
    "scraping_target_id" bigint NOT NULL REFERENCES "offers_scrappingtarget" ("id") ON DELETE CASCADE
);

-- An item/listing discovered by the scraper.
CREATE TABLE "offers_offer" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "url" text NOT NULL,
    "title" varchar(500) NOT NULL,
    "price" decimal(10, 2) NULL,
    "main_image_url" text NULL,
    "list_url" text NOT NULL,
    "published_at" timestamptz NULL,
    "closed_at" timestamptz NULL,
    "created_at" timestamptz NOT NULL,
    "target_id" bigint NOT NULL,
    -- The ON DELETE PROTECT rule is enforced at the application level by Django.
    -- Adding a non-deferrable foreign key constraint achieves a similar result at the DB level.
    CONSTRAINT "offers_offer_target_id_fk_offers_scrappingtarget"
        FOREIGN KEY ("target_id") REFERENCES "offers_scrappingtarget" ("id") ON DELETE RESTRICT
);

-- Add indexes for frequently queried columns
CREATE INDEX "notifications_notificationconfig_owner_id_idx" ON "notifications_notificationconfig" ("owner_id");
CREATE INDEX "offers_scrappingtarget_owner_id_idx" ON "offers_scrappingtarget" ("owner_id");
CREATE INDEX "offers_scrapingurl_scraping_target_id_idx" ON "offers_scrapingurl" ("scraping_target_id");
CREATE INDEX "offers_offer_target_id_idx" ON "offers_offer" ("target_id");
CREATE INDEX "offers_offer_created_at_idx" ON "offers_offer" ("created_at");

```
