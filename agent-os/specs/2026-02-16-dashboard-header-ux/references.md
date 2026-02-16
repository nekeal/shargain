# References — Dashboard Header & Loading UX

## Components

- **AppHeader (dead):** `frontend/src/components/app-header.tsx` — renders `<></>`
- **UserMenu:** `frontend/src/components/auth/user-menu.tsx` — avatar + dropdown with name/email/logout
- **Navbar01:** `frontend/src/components/ui/shadcn-io/navbar-01/index.tsx` — sticky navbar with nav links + auth buttons

## Routes

- **Root:** `frontend/src/routes/__root.tsx` — renders Navbar01 for protected routes
- **Dashboard:** `frontend/src/routes/dashboard.tsx` — main dashboard page
- **Notifications:** `frontend/src/routes/notifications.tsx` — notifications page

## Auth

- **Context:** `frontend/src/context/auth.tsx` — `useAuth()` providing `user: User | null`, `isAuthenticated`, `logout()`
- **User type:** `frontend/src/types/user.ts` — `{ id: number; email: string; username: string }`
- **Logout lib:** `frontend/src/lib/auth.ts` — `logout()` function used by UserMenu

## i18n

- **English:** `frontend/src/locales/en/translation.json`
- **Polish:** `frontend/src/locales/pl/translation.json`
