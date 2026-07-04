# Product

## Register

product

## Users

**Primary: "The Power Hunter"**
Highly motivated individuals competing for time-sensitive items (apartment hunting, limited-edition collectibles, rare car parts). They need to be faster than the competition and are frustrated by manual, repetitive checking of multiple websites. They configure multiple URLs with precise filters, expect near-real-time alerts, and treat the tool as a competitive advantage.

**Secondary: "The Casual Searcher"**
Individuals with a specific, one-time need (used bicycle, specific furniture piece, one-off purchase). They need a simple "set it and forget it" tool and are easily discouraged by manual monitoring. They configure one or two URLs, want zero maintenance, and expect notifications to just work without tuning.

Both personas share: Polish-speaking users monitoring OLX, Vinted, Otomoto, Otodom. The product serves as a **register of scraped products per user config** — each user defines their own monitoring targets and notification rules.

## Product Purpose

Shargain monitors Polish classified websites (OLX, Vinted, Otomoto, Otodom) for new offers matching user-defined criteria and delivers instant Telegram notifications. It eliminates the need to manually refresh listing pages, giving users a reliable, configurable alert system that respects their time and attention.

**What success looks like:**
- Users trust the system to catch relevant offers without false positives or missed items
- Notification latency stays under 10 minutes for 95% of alerts
- Free tier (100 notifications/month) serves casual users; power users have a clear upgrade path
- The dashboard feels like a precise instrument, not a generic SaaS dashboard

## Brand Personality

**Intentional** — Every element serves a purpose. No decorative flourishes, no engagement-hacking patterns. The interface earns its place by helping users configure monitors and interpret notifications efficiently.

**Efficient** — Optimized for the "set it and forget it" workflow. Configuration is dense but scannable; status is glanceable; actions are one-click. Power users can manage dozens of URLs without friction.

**Respectful** — The product works *for* the user, not *on* them. No dark patterns, no unnecessary notifications, no data harvesting. The free tier limit (100/month) is visible and honest. When limits are reached, the system pauses gracefully and communicates clearly.

## Anti-references

- **Generic SaaS dashboards** — Rounded-card grids, purple gradients, hollow "AI-powered" badges, empty-state illustrations with meaningless friendly blobs. Shargain is a utility, not a lifestyle brand.
- **Classifieds site UI (OLX, etc.)** — Dense tables, aggressive upsells, visual noise, mystery-meat navigation, cluttered filter sidebars. Shargain extracts signal from that noise; it shouldn't replicate it.
- **Notification spam** — Intrusive, irrelevant, hard-to-control alerts that train users to ignore or disable them. Shargain's notifications are user-configured, high-signal, and respect the monthly quota.

## Design Principles

1. **Signal over chrome** — The dashboard is a tool for configuring monitors and reading status. Visual hierarchy serves information density, not marketing. If a UI element doesn't help the user understand "what am I monitoring?" or "what just happened?", remove it.

2. **Configuration is the product** — The core user action is defining what to watch and how to be notified. Make URL entry, filter construction, and channel setup precise and fast. Favor inline editing over modals; show live validation; prevent invalid states rather than erroring after submit.

3. **Quotas are visible, not punitive** — The 100-notification monthly limit is a core constraint. Display usage prominently (e.g., "67/100 this month"), warn at 90%, pause cleanly at 100%, and show the reset date. Never surprise the user with a silent failure.

4. **Telegram is the delivery layer, not the product** — The web dashboard is where users *configure* and *review*; Telegram is where they *act*. Don't duplicate dashboard features in the bot. Keep the bot flow minimal: connect, test, done.

5. **Dark mode is a first-class citizen** — Power users monitor at all hours. Both themes. The violet/indigo accent system works in both themes without "dark mode as afterthought" compromises (no washed-out muted grays, no contrast failures).

## Accessibility & Inclusion

- **WCAG 2.1 AA** compliance target
- Reduced motion: all animations respect `prefers-reduced-motion`
- Color blindness: never rely on color alone for status (use icons, labels, patterns)
- Keyboard navigation: all interactive elements reachable and operable via keyboard
- Screen readers: semantic HTML, proper ARIA labels for dynamic content (loading states, toast notifications, filter builder)