# 6. Epic: MVP Public Launch

**Epic Goal**: To transform the existing closed-beta application into a stable, secure, and polished product ready for a public launch, delivering all features defined in the MVP scope.

### Story Sequence
1.  **Story 1.1: API Contract Finalization**: As a Senior Developer, I want to review and finalize the public API contract (OpenAPI spec), so that the frontend and backend teams have a stable, agreed-upon definition to work against.
    *   **AC1: MVP Endpoint Coverage**: The specification includes all necessary endpoints, request payloads, and response objects for the MVP's core user flows: user authentication (register/login), URL management (CRUD), and Telegram account connection.
    *   **AC2: Specification Validity**: The `openapi.json` file successfully validates against the OpenAPI 3.0 standard using a linting tool.
2.  **Story 1.2: Monetization Hook Implementation**: As a Product Owner, I want to add a `tier` field to the user model in the backend, so that we can easily introduce premium features and monetization in the future.
    *   **AC1: API Exposure**: The new `tier` field is included in the User object within the API responses (e.g., on the `/users/me` endpoint).
3.  **Story 1.3: Public User Authentication UI**: As a new user, I want to create an account and log in through a polished web interface, so that I can securely access the application.
    *   **AC1: Successful Registration**: A new user can navigate to a `/register` page and create an account by providing a valid email and password. Upon success, they are redirected to the main dashboard.
    *   **AC2: Successful Login**: A registered user can navigate to a `/login` page and sign in using their correct email and password. Upon success, they are redirected to the main dashboard.
    *   **AC3: Invalid Login**: If a user attempts to log in with an incorrect email or password, a clear error message is displayed on the login page.
    *   **AC4: Duplicate Registration**: If a user attempts to register with an email that already exists in the system, a clear error message is displayed on the registration page.
    *   **AC5: Google Login**: A user can log in or register by authenticating with their Google account.
4.  **Story 1.4: Core URL Management UI**: As an authenticated user, I want to use the web dashboard to add, view, and delete the URLs I want to track, so that I can manage my notification targets.
    *   **AC1: View URLs**: An authenticated user can see a list of all their tracked URLs on the main dashboard. Each item in the list should display the full URL and its current status (e.g., `Active`, `Disabled`).
    *   **AC2: Add URL**: The user can add a new URL to be tracked by submitting it through a form on the dashboard. The URL must be from a supported domain.
    *   **AC3: Delete URL**: The user can permanently remove a URL from their tracked list.
    *   **AC4: Disable/Enable URL**: The user can temporarily disable a tracked URL to pause notifications without deleting it. They can re-enable it at any time from the dashboard.
    *   **AC5: Invalid URL**: If a user submits a URL from an unsupported domain or in an invalid format, a clear error message is displayed.
    *   **AC6: UI/UX**: The dashboard interface for managing URLs is responsive and consistent with the project's `shadcn/ui` design system.
5.  **Story 1.5: Telegram Account Connection UI**: As an authenticated user, I want to connect my Telegram account through the web dashboard, so that the system knows where to send my notifications.
    *   **AC1: Connection Status**: On the user settings page, there is a clear visual indicator showing whether a Telegram account is currently connected or not.
    *   **AC2: Connection Instructions**: If not connected, the page displays clear instructions for the user, including a unique activation token or command (e.g., `/start 123xyz`) to create the notification config.
    *   **AC3: Successful Connection**: After the user interacts with the Telegram bot to create the config, the settings page UI updates to show the "Connected" status.
    *   **AC4: Disconnect**: If an account is connected, the user has a button to "Disconnect," which will remove the notification configuration for their personal chat.
6.  **Story 1.6: Legal Links UI**: As a new or existing user, I want to easily find and access the Terms of Service and Privacy Policy, so that I can understand my rights and the rules of the service.
    *   **AC1: Footer Links**: Links to the "Terms of Service" and "Privacy Policy" are present in the footer of the main application layout, making them accessible from all pages.
    *   **AC2: Legal Pages**: The routes for `/terms-of-service` and `/privacy-policy` are created and display the corresponding legal text.
7.  **Story 1.7: End-to-End Notification Validation**: As a user with a tracked URL, I want to receive a timely notification on Telegram when a new offer is detected, so that I can be confident the core functionality of the service is working.
    *   **AC1: Successful Notification**: When a new item is posted on a tracked URL, a notification is successfully delivered to the user's configured notification channel.
    *   **AC2: Timeliness**: The notification is received within the 10-minute latency window defined in the Non-Functional Requirements.
    *   **AC3: Notification Content**: The notification message contains, at a minimum, the title of the new offer, its price, and a direct link to it.
    *   **AC4: No Duplicates**: The system does not send more than one notification for the same offer.
8.  **Story 1.8: Password Reset**: As a user who has forgotten their password, I want to be able to reset it via email, so that I can regain access to my account.
    *   **AC1**: A "Forgot Password?" link is present on the login page.
    *   **AC2**: Clicking the link takes the user to a page where they can enter their registered email address.
    *   **AC3**: Upon submitting their email, the user receives an email with a unique, time-sensitive link to a password reset page.
    *   **AC4**: On the reset page, the user can securely enter and confirm a new password.
9.  **Story 1.9: Backend Tier Enforcement**: As the System, I need to track the number of notifications sent per user per calendar month, so that I can enforce the free tier limit.
    *   **AC1**: A user's notification count resets to 0 at the beginning of each billing period.
    *   **AC2**: The system stops sending notifications to a user when their count for the month reaches 100.
    *   **AC3**: The scraping microservice should not be able to fetch urls from scraping targets that are deactivated due to the exceeded limit.
    *   **AC4**: The user's notification count is periodically recalculated based on the number of offers in the databse
10. **Story 1.10: Frontend Usage/Tier Display**: As an authenticated user, I want to see my current monthly notification usage on the dashboard, so that I understand my limits.
    *   **AC1**: The dashboard displays the user's current notification count for the month (e.g., "Monthly Usage: 75/100 notifications").
    *   **AC2**: When the user reaches the limit, the dashboard clearly indicates that notifications are paused until the next billing period.
    *   **AC3**: On the dashboard the user sees the button to upgrade to a higher tier when he's close (90%) to the limit of notifications
    *   **AC4**: On the dashboard the user sees the button to upgrade to a higher tier when he reaches limit of links added for scraping. 
