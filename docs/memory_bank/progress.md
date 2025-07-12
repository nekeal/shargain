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

## Known Issues and Limitations
- Currently, if a new offer appears in multiple scraping targets, only the first one triggers a notification. This could be an issue for overlapping user interests.

## Evolution of Project Decisions
- The initial Telegram bot implementation was tightly coupled to the `pyTelegramBotAPI` library. This was refactored to a clean architecture to improve maintainability, testability, and flexibility for adding new features or even other notification channels in the future.
- The list display format was improved from plain text to formatted HTML to enhance the user experience.
