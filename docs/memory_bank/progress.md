# Progress: Application for following websites for new offers

## What Works
- Memory bank structure established
- Clean architecture principles defined
- API for reading scraping targets by scraper service
- API for receiving scraping results by scraper service
- Telegram user interface with:
  - Clean handler registration system
  - Pure application service layer
  - HTML formatting, clickable links, emojis
  - Internationalization (i18n) for all user-facing messages

## What's Left to Build
- A way to deactivate scraping targets from within the Telegram interface
- Implement UI for end users to add URLs and set preferences
- Integrate new sources of offers 
- Currently when new offer appears in multiple scraping targets, only the first appearance triggers notification. This can be a problem if scraping targets for different users overlap.

## Known Issues and Limitations

## Evolution of Project Decisions
