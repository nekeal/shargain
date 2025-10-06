# Frontend Architecture

This section defines the specific architectural patterns, folder structure, and conventions for the React Single-Page Application (SPA).

## Folder Structure

The `frontend/src/` directory is organized to promote scalability, maintainability, and a clear separation of concerns.

```plaintext
src/
├── components/
│   ├── common/         # Custom, reusable components (e.g., PageHeader, DataTable)
│   ├── features/       # Components specific to a feature (e.g., target-form)
│   └── ui/             # Unstyled base components from shadcn/ui (Button, Input)
├── hooks/              # Custom React hooks for reusable logic (e.g., use-media-query)
├── lib/
│   ├── api/            # Auto-generated API client and TanStack Query hooks (DO NOT EDIT)
│   └── utils.ts        # Shared utility functions (e.g., cn for classnames)
├── routes/             # File-based routing definitions for TanStack Router
│   ├── __root.tsx      # The root layout component for the entire app
│   ├── index.tsx       # The component for the '/' route (landing page)
│   └── dashboard.tsx   # The component for the '/dashboard' route
└── types/              # Shared TypeScript types and interfaces (if not from API)
```

## Component Strategy

Our strategy is centered around composition, leveraging `shadcn/ui` as a primitive component library.

1.  **Primitives First:** All UI elements are built upon the unstyled, accessible primitives found in `src/components/ui/`. These are the foundational building blocks.
2.  **Composition:** We create custom, reusable components (e.g., a `DataTable` with sorting and filtering) by composing these primitives. These live in `src/components/common/`.
3.  **Feature-Specific Components:** Components that are only used within a single feature or route (e.g., a complex form for creating a `ScrappingTarget`) are located in `src/components/features/`.
4.  **Smart vs. Dumb Components:**
    -   **Smart Components (Containers):** These are typically the route-level components found in `src/routes/`. Their primary responsibility is to fetch data using TanStack Query hooks and manage application state. They then pass this data down to presentational components as props.
    -   **Dumb Components (Presentational):** The majority of components (in `common/` and `features/`) are "dumb." They receive data and callbacks via props, render the UI, and have little to no internal state of their own. This makes them highly reusable and easy to test.

## State Management

We strictly differentiate between server state and client state.

-   **Server State:** Exclusively managed by **TanStack Query**. This is the source of truth for any data that comes from the backend. It handles all caching, background refetching, and optimistic updates for mutations. There should be no other stores (like Redux or Zustand) for server data.
-   **Global UI State:** For minimal, app-wide UI state (e.g., theme preference, mobile navigation visibility), we will use React's built-in **Context API**. A lightweight library like Zustand will only be considered if performance with the Context API becomes a demonstrable issue.
-   **Local Component State:** State that is confined to a single component (e.g., the current value of an input field) should be managed with standard `useState` and `useReducer` hooks.

## Routing

Routing is handled by **TanStack Router** using its file-based routing engine.

-   **File-based:** The URL structure of the application is determined by the file and folder hierarchy within the `src/routes/` directory.
-   **Layouts:** The `__root.tsx` file defines the root layout that wraps all pages. Nested layouts can be created by creating new directories with their own layout files.
-   **Data Loading:** Data for a route should be pre-fetched using the `loader` function provided by TanStack Router. This integrates seamlessly with TanStack Query to ensure data is available before a page component renders, which helps prevent loading spinners from flickering on screen.

## API Interaction

This is a critical rule for maintaining type safety and consistency.

-   **Generated Client is King:** All communication with the backend REST API **MUST** go through the auto-generated TanStack Query hooks located in `src/lib/api/`. The `pnpm generate:api-client` command is the source of truth for this client.
-   **No Direct `fetch` or `axios`:** Direct, manual use of `fetch` or other HTTP clients (like `axios`) for interacting with the backend API is strictly forbidden. Using the generated hooks ensures that all API calls are type-safe and that server state is managed correctly by TanStack Query.
