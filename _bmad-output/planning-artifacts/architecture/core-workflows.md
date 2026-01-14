# Core Workflows

This section contains diagrams and descriptions for the primary user journeys and system interactions.

## 1. User Registration & First Login

This workflow describes how a new user creates an account and logs in.

1.  **Initiation:** The user navigates to the signup page on the **Frontend** and submits their credentials (e.g., username, email, password).
2.  **Request:** The **Frontend** sends a `POST` request with the user's details to the `/api/public/auth/signup` endpoint on the **Backend API**.
3.  **Processing:** The **Backend API** validates the submitted data, ensuring the username and email are unique. It then hashes the password and creates a new `User` record in the **Database**.
4.  **Response & Login:** Upon successful creation, the **Backend API** automatically logs the new user in by creating a new session and returning a secure, `HttpOnly` session cookie to the **Frontend**.
5.  **Completion:** The **Frontend** receives the successful response and redirects the user to their dashboard, now as an authenticated user.

## 2. Linking a Notification Channel to a Target

This workflow describes the webhook-driven process for connecting a user's Telegram account to a scraping target.

1.  **Initiation:** While viewing a `ScrappingTarget` on the **Frontend**, the user clicks "Add Notification Channel".
2.  **Redirection:** The **Frontend**, having already generated a unique `register_token` for this action, redirects the user's browser to a special Telegram URL (e.g., `https://t.me/YourBotName?start=<register_token>`).
3.  **User Action:** The user's Telegram client opens, and they click the "START" button to interact with the bot.
4.  **Webhook:** **Telegram's servers** send a webhook (an HTTP POST request) to a pre-configured endpoint on our **Backend API** (e.g., `/api/webhooks/telegram`). This webhook payload contains the `register_token` and the user's unique Telegram `chat_id`.
5.  **Processing:** The **Backend API** receives the webhook. It finds the `register_token` in its system, identifies the associated user, and securely extracts the `chat_id` from the payload.
6.  **Creation & Linking:** The **Backend API** creates a new `NotificationConfig` record in the **Database**, saving the user's `chat_id`. It then programmatically links this new configuration to the `ScrappingTarget` from which the user initiated the process.
7.  **Confirmation (Optional):** The **Backend API** can send a confirmation message back to the user via the Telegram Bot API to confirm the successful link.

## 3. End-to-End Offer Notification (The "Happy Path")

```mermaid
sequenceDiagram
    participant Scraper as Scraping Microservice
    participant Target as Target Website
    participant API as Backend API (Django)
    participant DB as Database (PostgreSQL)
    participant Broker as Message Broker (RabbitMQ)
    participant Worker as Async Job Service (Celery)
    participant Telegram as Telegram Bot API

    loop Periodic Scraping Cycle
        Scraper->>+API: GET /api/internal/scraping-jobs
        API->>+DB: Fetch active ScrapingUrls
        DB-->>-API: Return list of URLs
        API-->>-Scraper: Return list of URLs
    end

    Scraper->>+Target: GET /product-listings
    Target-->>-Scraper: HTML Response

    Scraper->>Scraper: Parse HTML, find new offer

    opt Check if offer is new
        Scraper->>+API: GET /api/internal/offers?url=...
        API-->>-Scraper: 404 Not Found (Offer is new)
    end

    Scraper->>+API: POST /api/internal/offers (submit new offer data)
    API->>API: Validate data
    API->>+DB: Save new Offer record
    DB-->>-API: Confirm save
    API->>+Broker: Dispatch notification task (e.g., send_telegram.delay(offer_id))
    Note right of API: Returns 201 Created to Scraper immediately
    API-->>-Scraper: 201 Created
    Broker-->>-API: Acknowledge task received

    Note over Broker, Worker: Asynchronous Hand-off
    Worker->>+Broker: Consume notification task from queue
    Worker->>+DB: Fetch offer details and user's chat_id
    DB-->>-Worker: Return offer and config data
    Worker->>Worker: Format notification message

    Worker->>+Telegram: POST /sendMessage (to user's chat_id)
    Telegram-->>-Worker: 200 OK
```

## 4. Subscription Management (Stripe)

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as Backend API (Django)
    participant Stripe
    participant DB as Database (PostgreSQL)

    User->>+Frontend: Clicks "Upgrade to Pro Plan"
    Frontend->>+API: POST /api/public/subscriptions/create-checkout-session
    API->>+Stripe: create_checkout_session(user_id, plan='pro')
    Stripe-->>-API: Returns {session_id, url}

    API-->>-Frontend: Returns {url: "https://checkout.stripe.com/..."}
    Frontend->>User: Redirect to Stripe Checkout URL

    User->>+Stripe: Enters payment details and confirms
    Stripe->>Stripe: Processes payment securely

    Note over Stripe, API: Later, asynchronously...

    Stripe-->>+API: Webhook: POST /api/webhooks/stripe (event: 'checkout.session.completed')
    API->>API: Verify Stripe webhook signature
    API->>+DB: UPDATE users SET tier='pro' WHERE id=...
    DB-->>-API: Confirm update
    API-->>-Stripe: 200 OK
```

## 5. User Deactivates a Target
This is simply a `POST` request to the backend to disable the whole target.
