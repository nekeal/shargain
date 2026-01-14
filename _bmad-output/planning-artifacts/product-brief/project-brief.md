# Project Brief: Shargain - Offer Notification System

## 1. Executive Summary

The project is a notification system that automates the hunt for new offers on a curated list of popular advertisement platforms. It addresses the challenge of manually tracking multiple sites by centralizing offer discovery and delivering timely notifications through channels like Telegram. The target users are individuals looking for specific items, deals, or updates on these supported platforms. The key value proposition is providing a centralized, automated way to stay informed about new offers. This significantly reduces manual search effort and provides a critical speed advantage, helping users be among the first to act on competitive or time-sensitive offers.

## 2. Problem Statement

In today's fast-paced online marketplace, valuable opportunities are often fleeting. Users who monitor advertisement platforms for high-demand or well-priced items are at a disadvantage, as they are forced to rely on manual, repetitive checking of multiple websites. This process is not only time-consuming and inefficient but also highly unreliable.

The direct impact of this inefficiency is significant: users frequently miss out on competitive and time-sensitive offers, leading to frustration and the loss of the very opportunities they were seeking. This is especially true for listings where speed is the primary factor in a successful transaction.

While some websites offer their own notification systems, these solutions are often inadequate. They create a fragmented experience by forcing users to manage alerts across numerous platforms, and more importantly, their notifications are often too slow. A daily summary email, for instance, is not nearly frequent enough to secure a time-sensitive bargain. Other generic tools, like RSS feeds, are similarly not robust or fast enough to provide a true competitive edge. There is a clear need for a centralized, automated solution purpose-built for this challenge.

## 3. Proposed Solution

We propose a centralized, automated notification service that acts as a personal monitor for online offers. Users will provide URLs from a curated list of supported advertisement platforms, and our system will frequently poll these pages to detect new listings. Upon detection, an immediate notification will be sent to the user via their preferred channel, starting with Telegram.

Our key differentiators are:
*   **Centralization**: Users can manage all their tracked offers from a single, simple interface, eliminating the need to juggle multiple apps and browser tabs.
*   **Timeliness**: By optimizing our polling frequency, we provide a significant speed advantage over the slow, daily-digest emails offered by many platforms.
*   **Specialization**: Unlike generic tools, our parsers are purpose-built for the structure of advertisement listings, ensuring higher reliability and accuracy.

This solution will succeed by directly targeting the core user needs of efficiency, speed, and reliability in a way that fragmented, slow, or generic existing solutions do not. Our high-level vision is to become the essential tool for anyone seeking a competitive edge in online marketplaces, continuously expanding our support for new platforms and notification methods based on user demand.

## 4. Target Users

#### Primary User Segment: "The Power Hunter"
*   **Profile**: Highly motivated individuals competing for time-sensitive items. This includes tech-savvy hobbyists, collectors, and resellers, as well as people making high-stakes personal acquisitions, such as **apartment hunting in a competitive rental market**. They are driven by the need to act faster than others to secure their desired listing.
*   **Current Behaviors**: They manually check a list of 5-15 different websites, forums, and marketplaces multiple times a day. They live with a constant fear of missing out (FOMO) and the mental overhead of tracking everything.
*   **Needs & Pains**: Their primary need is to be faster than the competition. Their main pain point is the immense, repetitive manual effort required and the frustration of discovering a great offer just moments too late.
*   **Goals**: To successfully acquire specific, high-demand, or underpriced items/listings for their collection, hobby, business, or personal life.

#### Secondary User Segment: "The Casual Searcher"
*   **Profile**: Individuals with a specific, often one-time, need. For example, a parent looking for a used bicycle, or someone waiting for an out-of-stock item to become available.
*   **Current Behaviors**: They might check a website once a day or rely on slow, built-in stock alerts. They are easily discouraged by the effort required and may give up.
*   **Needs & Pains**: They need a simple "set it and forget it" tool. Their pain is that they don't have the time or desire to engage in constant, manual monitoring.
*   **Goals**: To find a specific item with minimal effort.

## 5. Goals & Success Metrics

#### Business Objectives
*   **Validate Core Value Proposition**: Achieve 100 daily active users within 3 months of launch to confirm product-market fit with our "Power Hunter" segment.
*   **Drive User Retention**: Attain a month-over-month retention rate of at least 40% for the first 6 months, indicating that users find ongoing value.
*   **Inform Future Development**: Gather qualitative feedback from at least 20 active users within the first 4 months to build a data-driven product roadmap.

#### User Success Metrics
*   **Time Saved**: Users report a significant reduction in the time they spend manually checking websites (measured via user surveys).
*   **Successful Acquisitions**: A meaningful percentage of users report that the service directly led to them successfully acquiring a competitive item they would have otherwise missed.
*   **High Satisfaction**: Achieve a Net Promoter Score (NPS) of 50+ from active users, indicating high satisfaction with the timeliness and relevance of notifications.

#### Key Performance Indicators (KPIs)
*   **User Engagement**: Daily Active Users (DAU) and Monthly Active Users (MAU).
*   **Service Adoption**: Average number of active tracked URLs per user.
*   **Notification Action Rate**: The **Click-Through Rate (CTR)** on notifications. This directly measures how often users visit the offers we send them. A high CTR is a strong signal that our notifications are relevant, timely, and valuable.
*   **System Health**: Scraper success rate and average notification delay.

## 6. MVP Scope

#### Core Features (Must-Haves for MVP)
*   **Web-Based User Interface (Primary)**: A web dashboard where users can register, log in, manage their tracked URLs, and view a history of their recent notifications.
*   **User Account System**: Standard email and password registration and login through the web interface.
*   **URL Submission & Management**: A user-friendly interface on the web dashboard for adding, viewing, and removing URLs from our curated list of supported platforms.
*   **Scraping Engine**: The core service that polls user-submitted URLs. For the MVP, this will specifically support our initial platforms: **OLX, Vinted, Otomoto, and Otodom**.
*   **Notification Engine**: The service responsible for sending notifications.
*   **Telegram Notifications (Secondary Channel)**: A Telegram bot will serve as a primary channel for *receiving* notifications. All account and URL management will be handled through the web app to keep the bot's role focused for the MVP.

#### Out of Scope for MVP
*   Managing account settings or tracked URLs via the Telegram bot.
*   Support for any website not on our initial, curated list.
*   Advanced notification controls (e.g., price-range filtering, keyword muting).
*   Support for notification channels other than Telegram.
*   Advanced user analytics or historical data dashboards.
*   Any form of payment or subscription.

#### MVP Success Criteria
The MVP's success is tied to providing a tangible speed advantage and will be measured by the user adoption and retention goals we set earlier.

## 7. Post-MVP Vision

#### Phase 2 Features (The Next Priorities)
*   **Expanded Platform Support**: Gradually add support for more advertisement platforms based on user requests and popularity.
*   **Advanced Notification Controls**: Introduce features like keyword filtering, price range filtering, and the ability to mute specific searches.
*   **Additional Notification Channels**: Add support for other delivery methods like Email and native Web Push notifications.
*   **Enhanced Bot Interactivity**: Allow users to perform simple management tasks directly from the Telegram bot.

#### Long-term Vision (1-2 Years)
*   To evolve from a notification tool into a comprehensive "deal-hunting" platform. This could include features like historical price tracking for items, analytics on offer frequency, and insights into market trends. The vision is to become the "Google Analytics for online deals."

#### Expansion Opportunities (Speculative Ideas)
*   **AI-Powered Recommendations**: Proactively suggest items or searches to users based on their activity and success patterns.
*   **Cross-Platform Arbitrage**: Automatically identify significant price differences for the same item across different supported platforms.
*   **Premium Tiers**: Introduce a subscription model for power users that could offer higher polling frequency, a larger number of tracked URLs, or access to advanced analytics.

## 8. Technical Considerations

#### Platform Requirements
*   **Target Platforms**: The web application must support modern desktop and mobile browsers. Notifications will be delivered via Telegram.
*   **Performance Requirements**: The scraping engine must be efficient, and the notification system must have minimal latency.

#### Technology Preferences
*   **Frontend**: The web application will be built with **React**. It will use **TanStack Router** for routing, **TanStack Query** for server state management, and **openapi-ts** for generating the API client.
*   **Backend**: The main web application backend will be built with the **Django** framework.
*   **Database**: The project will use **PostgreSQL** as its database.
*   **Scraping**: A separate Python service will handle scraping, using libraries like **`requests`** or **`httpx`**.
*   **Deployment**: The entire application will be containerized using **Docker** and orchestrated for local development and deployment with **Docker Compose**.

#### Architecture Considerations
*   **Service Architecture**: The system will be composed of at least two main services: the primary **Django web application** and a separate **Scraping Service**. The Scraping Service will operate independently and push its results (newly found offers) to an API endpoint on the main Django backend.
*   **API Specification**: The Django backend will expose an OpenAPI-compliant REST API. The React frontend will consume this API via the client generated by `openapi-ts`.
*   **Security**: User authentication and security will be handled by Django's robust, built-in features.

## 9. Constraints & Assumptions

#### Constraints
*   **Budget**: To be determined. The self-hosted, containerized nature of the application will require ongoing infrastructure cost management.
*   **Timeline**: To be determined. The decision to build a full web application for the MVP is a key factor that will influence the project timeline.
*   **Technical Scope**: The service is strictly limited to scraping the pre-defined list of supported platforms. It cannot scrape arbitrary websites.
*   **External Dependencies**: The system is dependent on the structure and terms of service of the target websites. Changes or anti-scraping measures on their end are a significant constraint.

#### Key Assumptions
*   **User Demand**: We assume there is a sufficient number of "Power Hunter" users who will find, adopt, and actively use our service.
*   **Technical Feasibility**: We assume that the target websites are technically scrapable on a consistent basis and that we can build a system resilient enough to handle common anti-bot measures.
*   **Value of Speed**: We assume the speed advantage our service provides is a compelling reason for users to choose our product.
*   **Legal & Ethical**: We assume that scraping publicly available data from the target platforms for the purpose of user notification is permissible. (Note: This should be verified).

## 10. Risks & Open Questions

#### Key Risks
*   **Technical Risk (High)**: Our primary risk is that target websites implement advanced anti-bot measures that make our scraping service unreliable.
*   **Execution Risk (Medium)**: The decision to build a full web application for the MVP increases development time, risking loss of momentum.
*   **Market Risk (Medium)**: Our target users might be a niche group or may already be satisfied with their own custom solutions.
*   **Legal Risk (Unknown)**: Scraping target websites may violate their Terms of Service.

#### Areas Needing Further Research
*   A thorough legal review of the Terms of Service for **OLX, Vinted, Otomoto, and Otodom**.
*   Technical investigation ("spikes") into the anti-scraping technologies used by **OLX, Vinted, Otomoto, and Otodom**.
*   User research to validate the MVP feature set with our "Power Hunter" persona.

## 11. Appendices

#### A. Research Summary
*   *(This section is a placeholder for the findings from the "Areas Needing Further Research" listed above.)*

#### B. Stakeholder Input
*   This Project Brief was created collaboratively with the primary project stakeholder. Key decisions have been incorporated directly into the document.

#### C. References
*   Initial project context was drawn from: `docs/memory_bank/projectbrief.md` and `.serena/memories/project_overview.md`.

## 12. Next Steps

#### Immediate Actions
1.  **Finalize and Distribute Project Brief**: Save this document as `docs/project-brief.md`.
2.  **Conduct Platform Research**: Perform the legal and technical research on the four target platforms.
3.  **Validate with Users**: Conduct interviews with "Power Hunter" users.
4.  **Create High-Level Roadmap**: Create a project roadmap and timeline based on research findings.

#### PM Handoff
This Project Brief provides the full context for the project. The Product Manager (PM) agent, John, should now take this brief to begin the creation of a detailed Product Requirements Document (PRD).
