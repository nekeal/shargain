# Coding Standards

## Critical Fullstack Rules

1.  **API Interaction:** All frontend communication with the backend API **MUST** go through the auto-generated TanStack Query hooks. Direct use of `fetch` or `axios` is forbidden.
2.  **Component Design:** New React components **MUST** be built by composing the generic UI primitives from the `src/components/ui/` directory to ensure visual consistency.
3.  **Asynchronous Logic:** Any backend process that is not instantaneous (e.g., sending a notification) **MUST** be delegated to the `Async Job Service (Celery)` to keep the API responsive.
4.  **API Separation:** The public API (e.g., `/api/public/...`) is exclusively for the frontend. The internal API endpoints (e.g., `/api/scrapping-targets`) are exclusively for the external scraping microservice. Do not cross these boundaries.

## Naming Conventions

| Element | Convention | Example |
| :--- | :--- | :--- |
| React Components | `PascalCase` | `TargetCard.tsx` |
| React Hooks | `useCamelCase` | `useCurrentUser.ts` |
| API Routes | `kebab-case` | `/api/public/targets/{id}/add-url` |
| Database Tables | `appname_modelname` | `offers_scrappingtarget` |
| Python Code | `snake_case` | `def get_active_targets():` |
| TypeScript Code | `camelCase` | `const newTarget = ...` |

## Accessibility (A11y)

### Compliance Target

-   **Standard:** The application **MUST** adhere to the **Web Content Accessibility Guidelines (WCAG) 2.1 Level AA** standard.

### Core Principles

1.  **Semantic HTML:** Use correct, semantic HTML5 elements (`<nav>`, `<main>`, `<button>`, etc.) at all times. This is the foundation of accessibility and ensures screen readers can interpret the page structure.
2.  **Keyboard Navigation:** All interactive elements, including links, buttons, and form fields, **MUST** be fully operable using only the keyboard. Focus order must be logical, and a visible focus indicator (outline) must always be present.
3.  **ARIA Roles:** For complex custom components (like modals or custom dropdowns), appropriate ARIA (Accessible Rich Internet Applications) roles and attributes **MUST** be used to describe their function to assistive technologies. However, native HTML elements should always be preferred over ARIA when possible.
4.  **Color Contrast:** All text must meet a minimum contrast ratio of **4.5:1** against its background to be legible for users with visual impairments.

### Testing Strategy

1.  **Automated Linting:** The `eslint-plugin-jsx-a11y` package **MUST** be integrated into our ESLint configuration to catch common accessibility issues during development.
2.  **Manual Testing:** Before a feature is considered complete, it **MUST** be manually tested for:
    -   Full keyboard navigability.
    -   Usability with a screen reader (e.g., VoiceOver on macOS, NVDA on Windows).
