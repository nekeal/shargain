# Brainstorming (Revised): A Hybrid Approach to Onboarding and Notification Tokens

## 1. Re-evaluating The Core Problem

Initial analysis focused on creating a single, generic token system. However, further reflection reveals two distinct, and fundamentally different, business processes:

1.  **Channel Registration**: An existing user wants to link a new notification method (Telegram, email, etc.) to their account. This is a generic requirement for any channel.
2.  **Interactive Onboarding**: An admin wants to onboard a new, UI-less user *specifically through an interactive channel like Telegram*. This channel acts as the user's primary interface. This is a powerful, but likely channel-specific, feature.

Furthermore, the introduction of **channel confirmation** (e.g., verifying an email address) adds another layer of complexity. A token might initiate a registration, but the channel isn't truly active until confirmed.

The core challenge is not just about differentiating two flows, but about **designing a system that provides a generic foundation for all notification channels while allowing for specialized, high-value onboarding experiences on capable channels like Telegram.**

---

## 2. Proposed Hybrid Architecture: Separate Concerns

Instead of a single "Smart Token", we should introduce two distinct concepts and models to handle the different use cases. This keeps the generic parts clean and isolates the specialized logic.

1.  **`NotificationRegistrationToken`**: A generic token whose **sole purpose** is to securely link a new notification channel to an *existing user account*. This will be the backbone for adding any new channel.
2.  **`OnboardingInvite`**: A specialized token/invite whose purpose is to execute the full "magic link" flow: create a `ScrapingTarget` for an admin and link it to a new user's `NotificationChannel`. Initially, this can be designed specifically for Telegram.

### Module Placement

-   `NotificationRegistrationToken` and its logic belong in the **`notifications` module**. It's the generic, central piece.
-   `OnboardingInvite` and its logic could live in the **`telegram` module** for now. This acknowledges that the flow is currently a unique feature of the Telegram integration. If another channel (e.g., Slack) later supports a similar interactive flow, this concept could be extracted into a more generic `invites` module.

---

## 3. Detailed Flow Walkthroughs

### Flow A: Standard Channel Registration (Generic Flow)

This flow covers a new user configuring their first channel, or an existing user adding another one. Your point about creating the channel in a `PENDING` state first is excellent, as it dramatically improves the user experience.

**Data Model: `notifications.models.NotificationRegistrationToken`**

```python
class NotificationRegistrationToken(models.Model):
    # ... (token, user, expires_at, is_used)
    # No token_type needed, its purpose is singular.
    pass

class NotificationChannel(models.Model):
    class Status(models.TextChoices):
        PENDING_CONFIRMATION = 'PENDING', 'Pending Confirmation'
        ACTIVE = 'ACTIVE', 'Active'

    # ... (user, channel_type, details)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_CONFIRMATION)
```

**Walkthrough (Adding an Email Channel):**

1.  **Initiation**: User clicks "Add Email Notification" in the UI. Frontend calls `POST /api/notifications/channels` with the user's email address.
2.  **Backend (`notifications` module)**:
    - Immediately creates a `NotificationChannel` record for the user's email with its `status` set to `PENDING_CONFIRMATION`.
    - Creates a `NotificationRegistrationToken` and associates it with the user and/or the pending channel.
    - Sends the confirmation email containing a link like `https://app.com/confirm-email?token={token}`.
3.  **User Action (In UI)**: The API call from step 1 returns a success. The UI can now immediately display the new email channel, perhaps with a `(Pending confirmation)` label. The user can **assign this pending channel to a `ScrapingTarget`**. The UI should clearly indicate that notifications for this channel are paused until it's confirmed.
4.  **User Action (Confirmation)**: User clicks the link in their email.
5.  **Backend Handler**: The `/confirm-email` endpoint receives the token.
    - It validates the token.
    - It finds the corresponding `NotificationChannel` that is in the `PENDING_CONFIRMATION` state.
    - It updates the channel's `status` to `ACTIVE`.
    - The user is redirected to a success page, and notifications for any assigned scraping targets can now be sent.

**Walkthrough (Adding a Telegram Channel):**

This flow is special because obtaining the `chat_id` can be difficult for users. The process should support both manual entry for power users and an automatic, deep-link-based retrieval for standard users.

1.  **Initiation (Web UI)**: The user goes to add a Telegram channel. The UI offers two paths:
    *   **Path A (Manual Entry)**: An input field for the `chat_id`.
    *   **Path B (Automatic Retrieval)**: A button like "Connect with Telegram".

2.  **Executing Path A (Power User)**:
    *   The user enters their `chat_id` and saves.
    *   The frontend calls `POST /api/notifications/channels` with `{ channel_type: 'TELEGRAM', details: { chat_id: '...' } }`.
    *   The backend creates the `NotificationChannel` and can immediately set its `status` to `ACTIVE` (potentially after sending a test message to validate the ID).

3.  **Executing Path B (Standard User)**:
    *   The user clicks "Connect with Telegram".
    *   The frontend first calls `POST /api/notifications/channels` with just `{ channel_type: 'TELEGRAM' }`.
    *   The backend creates a `NotificationChannel` with a `PENDING_CONFIRMATION` status and **no `chat_id`**. It also creates and associates a `NotificationRegistrationToken`.
    *   The API returns the `token`. The UI can now show the pending channel.
    *   The frontend uses the token to create and show the deep link: `t.me/YourBot?start=confirm_{token}`.

4.  **Confirmation (Path B)**:
    *   The user clicks the deep link, which opens their Telegram app and sends the `/start` command.
    *   The bot handler on the backend receives the command, the `token`, and the user's `chat_id` from the Telegram API.
    *   It calls a service, e.g., `notifications.services.confirm_telegram_channel(token, chat_id)`.
    *   This service finds the pending `NotificationChannel` via the token, updates its `details` field with the `chat_id`, and sets its `status` to `ACTIVE`.
    *   A confirmation message is sent to the user in Telegram, and the web UI can be updated to reflect the active status.

### Flow B: Admin-Generated Telegram Onboarding (Specialized Flow)

This flow is treated as a special feature of the Telegram module.

**Data Model: `telegram.models.OnboardingInvite`**

```python
class OnboardingInvite(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # ... expires_at, is_used, etc.
```

**Walkthrough:**

1.  **Invite Generation**: Admin clicks "Generate Telegram Invite". Frontend calls a specific endpoint: `POST /api/telegram/invites`.
2.  **Backend (`telegram` module)**: Creates an `OnboardingInvite` linked to the admin.
3.  **User Action**: The invitee clicks the deep link: `t.me/YourBot?start=invite_{token}`.
4.  **Bot Handler (`telegram` module)**:
    - Receives `/start invite_{token}`.
    - It looks up the token in the `OnboardingInvite` table.
    - Finding a match, it executes the specialized logic:
        1. Creates a new `ScrapingTarget` for the `invite.admin_user`.
        2. Creates a new `NotificationChannel` for the invitee's Telegram chat, marking it as `ACTIVE` immediately.
        3. Links the two.
        4. Marks the invite as used and sends a welcome message.

---

## 4. Advantages of the Hybrid Approach

-   **Clarity and Simplicity**: The generic `NotificationRegistrationToken` has one job and does it well for all channels. The complex, multi-step logic of the admin flow is isolated.
-   **True Extensibility**: Adding a new, simple notification channel (e.g., Discord Webhook) is trivial. You just need to implement the final confirmation step. You don't need to worry about how it fits into the complex admin onboarding flow.
-   **Isolation of Complexity**: The Telegram-as-a-UI feature is powerful but unique. This architecture treats it as a feature of the `telegram` module, preventing its specific requirements from complicating the design of the core `notifications` system.
-   **Handles Confirmation**: The model naturally supports multi-step confirmation flows (like email) by introducing a `status` on the `NotificationChannel`.

## 5. Conclusion

By separating the concerns of **channel registration** from **interactive onboarding**, we can build a system that is both robustly generic and powerfully specific. The core notification system remains simple and scalable, while specialized modules like `telegram` can build high-value, complex features on top of it without compromise. This hybrid model provides the best of both worlds.
