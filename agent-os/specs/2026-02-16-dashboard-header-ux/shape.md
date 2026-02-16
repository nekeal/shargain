# Shape — Dashboard Header & Loading UX

## Scope

**In scope:**
- Remove dead `AppHeader` component and all imports
- Wire existing `UserMenu` into `Navbar01` (avatar + dropdown)
- Personalized dashboard greeting with i18n
- Loading skeleton, error card, empty state for dashboard

**Out of scope:**
- New components (reuse existing `UserMenu`, `Avatar`, etc.)
- Profile/settings pages (dropdown links are placeholders)
- Backend changes

## Key Decisions

1. **Reuse `UserMenu` as-is** — The existing component already has avatar, initials, dropdown with name/email/logout. No modifications needed.

2. **Type mapping in `__root.tsx`** — The auth `User` type (`{id: number, email, username}`) differs from `UserMenu`'s expected shape (`{id: string, name, email, provider}`). Mapping happens at the call site, not via a shared type.

3. **`handleLogout` stays in `Navbar01`** — `UserMenu` uses its own `logout` from `@/lib/auth`. The existing `handleLogout` in `Navbar01` (which calls `shargainPublicApiAuthLogoutView` + `logout()` from context) is removed — `UserMenu` handles sign-out independently.

4. **Skeleton uses same gradient background** — Ensures visual continuity during loading. No layout shift when data arrives.

5. **Translation interpolation** — `"Welcome back, {{name}}"` uses i18next interpolation syntax already established in the codebase.

## Edge Cases

- **No username:** Fall back to email or generic "Welcome back"
- **Mobile:** `UserMenu` replaces the logout button in both mobile and desktop views
