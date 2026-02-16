# Standards — Dashboard Header & Loading UX

## Frontend Colocated Hooks

No new hooks needed. Existing hooks reused:
- `useAuth()` — global auth context (user, isAuthenticated, logout)
- `useGetMyTarget()` — colocated in `frontend/src/components/dashboard/monitored-websites/useMonitors.ts`

## Component Composition

- `UserMenu` is an existing standalone component at `frontend/src/components/auth/user-menu.tsx`
- `Navbar01` accepts props for customization — `user` prop added for UserMenu integration
- Dashboard states (loading/error/empty) stay inline in the route component — no separate component extraction needed (KISS)

## i18n

- Translation keys follow existing `dashboard.*` namespace
- Interpolation uses `{{variable}}` syntax (i18next standard)
- Both `en` and `pl` translation files updated simultaneously
