# Active Context: Application for following websites for new offers

## Current Work Focus
- Designing the notification architecture for new offers
- Ensuring clean separation between business logic and adapters (e.g., Telegram)
- Improving the Telegram user interface for better user experience

## Recent Changes
- Initiated memory bank documentation
- Outlined clean architecture approach
- Upgraded project to use latest Python version (3.13)
- Refactored Telegram handlers to use pure application service layer and adapter pattern
- Improved Telegram UI: HTML formatting, clickable links, emojis, prominent delete command
- Added internationalization (i18n) for all user-facing messages
- Improved the /delete command to be interactive
- Streamlined the 'add link' flow in Telegram bot, removing an extra step and adding a 'Skip' button and 'x' command for skipping name input.

## Next Steps
- Implement UI for end users to add URLs and set preferences
- Allow deactivating scraping targets from within the Telegram interface
- Integrate new sources of offers 

## Active Decisions and Considerations
- use django built-in internationalization for translations of telegram messages
- **Accepted Trade-off in Offer Creation:** The system identifies unique offers by combining the offer's `url` and the `ScrappingTarget` that found it. This can lead to duplicate database entries and notifications if multiple targets find the same offer. This is an accepted trade-off, as the typical user is expected to have few, non-overlapping targets, making the issue minor in practice.

## Important Patterns and Preferences

## Learnings and Project Insights
