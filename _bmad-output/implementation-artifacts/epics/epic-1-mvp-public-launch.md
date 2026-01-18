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
11. **Story 1.11: Webhook Notification Channel**: As a developer or power user, I want to configure a webhook URL as a notification channel, so that I can integrate new offer alerts into my own automation systems (e.g., Slack, Discord bots, custom dashboards).
    *   **AC1: Webhook Channel Option**: When creating or editing a notification configuration, the user can select "Webhook" as the channel type.
    *   **AC2: Webhook URL Configuration**: When webhook channel is selected, the user can enter a valid HTTPS URL where notifications will be sent.
    *   **AC3: Webhook URL Validation**: The system validates that the webhook URL is a valid HTTPS URL before saving.
    *   **AC4: Webhook Notification Delivery**: When a new offer is detected, the system sends a POST request to the configured webhook URL with the offer data in JSON format.
    *   **AC5: Webhook Payload Schema Documentation**: The webhook payload schema is documented in an accessible location (API docs or dedicated page) so users know how to parse incoming notifications.
    *   **AC6: Webhook Error Handling**: If a webhook delivery fails (timeout, 4xx/5xx response), the system logs the error but does not retry (MVP behavior).
    *   **AC7: Backend Integration**: The webhook sender integrates with the existing notification system architecture (BaseNotificationSender pattern).
12. **Story 1.12: Google Social Login**: As a new or returning user, I want to log in or register using my Google account, so that I can access the application quickly without creating a separate password.
    *   **AC1: Google Login Button**: The login page displays a "Continue with Google" button that redirects to Google OAuth.
    *   **AC2: Google Signup Button**: The signup page displays a "Sign up with Google" button that redirects to Google OAuth.
    *   **AC3: New User Registration**: When a user authenticates with Google for the first time, a new account is automatically created using their Google email.
    *   **AC4: Existing User Login**: When a user authenticates with Google and an account with that email already exists, they are logged into that existing account.
    *   **AC5: Session Creation**: Upon successful Google authentication, a Django session is created.
    *   **AC6: Error Handling**: If Google authentication fails or is cancelled, user is redirected back with appropriate error state.
    *   **AC7: Dashboard Redirect**: After successful authentication, the user is redirected to frontend `/dashboard`.
    *   **AC8: Conditional Button Display**: Google login/signup buttons are only displayed if backend has Google OAuth configured (client ID/secret present).
13. **Story 1.13: UX/UI Accessibility & Usability Fixes**: As a user with disabilities or using mobile devices, I want the application to be fully accessible and usable across all devices, so that I can effectively manage my offer monitoring without barriers.
    *   **AC1: Icon-Only Buttons Have Accessible Labels**: All icon-only buttons have appropriate `aria-label` attributes for screen reader users.
    *   **AC2: Destructive Actions Require Confirmation**: Delete actions display a confirmation dialog before executing.
    *   **AC3: Touch Targets Meet WCAG Minimum**: All interactive elements have minimum 44x44px touch targets on mobile.
    *   **AC4: Console Logs Removed**: No `console.log` statements in production builds that expose user data.
    *   **AC5: Error Handling is Type-Safe**: Error messages use proper TypeScript types with fallback messages.
    *   **AC6: Mobile Filter UI is Usable**: Filter rules don't overflow or cramp on mobile screens.
    *   **AC7: Dead Code Removed**: Unused components (Header.tsx, AppHeader.tsx) removed from codebase.
    *   **AC8: Loading States Show Visual Feedback**: Dashboard loading state displays spinner with consistent indicators.
