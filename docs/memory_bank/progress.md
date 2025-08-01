# Progress: Application for following websites for new offers

## What Works
- **Memory Bank:** A comprehensive memory bank structure is established and maintained.
- **Clean Architecture:** The Telegram bot is refactored to use a clean architecture with a pure application service layer, adapters, and dependency inversion.
- **Telegram User Interface:**
  - A robust command handler registration system.
  - A user-friendly interface for listing tracked links, featuring:
    - HTML formatting for readability and clickable links.
    - Emojis for better visual engagement.
    - Clear instructions for deleting links.
  - Internationalization (i18n) for all user-facing messages.
- **API:**
    - API for reading scraping targets by scraper service.
    - API for receiving scraping results by scraper service.


## What's Left to Build
- A way to deactivate or pause scraping for a specific URL from the Telegram interface.
- A user interface for adding new URLs to track.
- Integration of new sources for offers.
- A mechanism to handle notifications for offers that appear in multiple, overlapping scraping targets for different users.
- Subscription management system.
- User activity tracking features.
- User onboarding process.
- Admin dashboard.
- Secure the scraper API.
- Create a new User API for managing scraping URLs.

## Known Issues and Limitations
- Currently, if a new offer appears in multiple scraping targets, only the first one triggers a notification. This could be an issue for overlapping user interests.
- The scraper API is currently public and needs to be secured.

## Evolution of Project Decisions
- The initial Telegram bot implementation was tightly coupled to the `pyTelegramBotAPI` library. This was refactored to a clean architecture to improve maintainability, testability, and flexibility for adding new features or even other notification channels in the future.
- The list display format was improved from plain text to formatted HTML to enhance the user experience.

## MVP Implementation Progress

### API Implementation
- [ ] **Scraper API:** Secure with API key authentication.
- [ ] **User API:** Implement Facade, Views, and URLs.

### Subscription Management
- [ ] **Models:** Create `Subscription` model.
- [ ] **Views:** Create views for subscription management.
- [ ] **Logic:** Implement subscription limit enforcement and payment integration.

### User Activity Tracking
- [ ] **Models:** Create `OfferClick` and `FavoriteOffer` models.
- [ ] **Views:** Create views for tracking offer clicks and favorites.
- [ ] **Logic:** Implement notification engagement tracking.

### User Onboarding
- [ ] **Welcome Email:** Implement welcome email for new users.
- [ ] **Tutorial:** Create a simple user tutorial.

### Administration
- [ ] **Dashboard:** Create an admin dashboard.
- [ ] **User Management:** Implement user management features.
