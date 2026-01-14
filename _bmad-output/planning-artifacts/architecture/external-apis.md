# External APIs

## Telegram Bot API

-   **Purpose:** To send notifications about newly found offers to users who have configured a Telegram channel.
-   **Documentation:** `https://core.telegram.org/bots/api`
-   **Base URL(s):** `https://api.telegram.org/bot<token>/`
-   **Authentication:** A secret Bot Token, which is included in the request URL. This token must be stored securely as an environment variable and should never be exposed client-side.
-   **Rate Limits:** The API has rate limits that must be respected. While high, bulk notifications should be sent with care, potentially with small delays between messages to avoid being flagged.

**Key Endpoints Used:**
-   `POST /sendMessage` - This is the primary endpoint used to send a text message to a specific chat ID. The message content will include the offer's title, price, and a direct link.

**Integration Notes:**
-   The `Async Job Service (Celery)` is solely responsible for making outbound calls to this API.
-   The application must gracefully handle potential errors, such as an invalid `chat_id` (if a user revokes permission) or network failures.
-   The `register_token` in the `NotificationConfig` model is used to associate a user's Telegram `chat_id` with their Shargain account during a one-time setup flow.

## Target Websites (e.g., OLX, Vinted)

-   **Purpose:** To serve as the source of data (offers) for the **Scraping Microservice**.
-   **Documentation:** N/A. There is no official, public API. The "contract" is the website's HTML structure, which is volatile and subject to change without any notice.
-   **Base URL(s):** The specific URLs of the search/listing pages provided by users in the `ScrapingUrl` entries.
-   **Authentication:** Not typically required for accessing public listings. However, the scraper may need to manage cookies or a basic session to mimic a regular user and avoid detection.
-   **Rate Limits:** While there are no published rate limits, overly aggressive or rapid-fire requests will likely result in temporary IP bans, CAPTCHA challenges, or other anti-bot measures.

**Integration Notes:**
-   **High Instability:** This is the most fragile part of the system. The scraping logic must be designed for resilience and adaptability, as changes to the target websites' HTML layout are expected and will break the scraper.
-   **"Good Citizen" Scraping:** The **Scraping Microservice** must be configured to be respectful. This includes using realistic user-agents, introducing randomized delays between requests, and potentially rotating IP addresses to avoid being blocked.
-   **Maintenance Overhead:** A significant portion of ongoing maintenance for this project will likely be updating the scraper to adapt to changes on these target websites.
