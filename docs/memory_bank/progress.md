# Progress

## What Works
- Memory bank structure established
- Clean architecture principles defined
- API for reading scraping targets by scraper service
- API for receiving scraping results by scraper service
- Basic Telegram user interface

## What's Left
- Upgrade project to use latest Python version (3.13)
- Implement UI for end users to add URLs and set preferences
- Integrate new sources of offers 
- Currently when new offer appears in multiple scraping targets, only the first appearance triggers notification. This can be a problem if scraping targets for different users overlap.
