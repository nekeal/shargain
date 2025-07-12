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

## Next Steps
- Fix the way how new offer is detected. Currently if the new Offer object is created, notification is sent to the user. However, if the same offers appear under the different scraping target (especially belonging to a different user), the notification is not sent. 
- Implement UI for end users to add URLs and set preferences
- Allow deactivating scraping targets from within the Telegram interface
- Integrate new sources of offers 

## Active Decisions and Considerations
- use django built-in internationalization for translations of telegram messages

## Important Patterns and Preferences

## Learnings and Project Ins
