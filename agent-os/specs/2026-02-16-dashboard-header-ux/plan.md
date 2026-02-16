# Dashboard Header & Loading UX — Implementation Plan

## Context

The dashboard header has three problems:
1. `AppHeader` renders an empty fragment — dead code imported in `dashboard.tsx` and `notifications.tsx`
2. `Navbar01` shows a plain "Log Out" text button with no user identity — a polished `UserMenu` component (avatar + dropdown) exists but is unused
3. The page title ("Offer Monitor Dashboard") is a raw h1+p with no user context or hierarchy
4. Loading/error states are unstyled plain text divs

---

## Task 1: Save Spec Documentation

Create `agent-os/specs/2026-02-16-dashboard-header-ux/` with plan.md, shape.md, standards.md, references.md.

---

## Task 2: Remove Dead `AppHeader`

**Files:**
- `frontend/src/routes/dashboard.tsx` — remove import + `<AppHeader />`
- `frontend/src/routes/notifications.tsx` — remove import + `<AppHeader />`
- `frontend/src/components/app-header.tsx` — delete file

---

## Task 3: Wire `UserMenu` into `Navbar01`

**Files:**
- `frontend/src/components/ui/shadcn-io/navbar-01/index.tsx`
  - Add optional `user` prop (`{ id: string; name: string; email: string; provider: string | null } | null`)
  - Replace authenticated logout button with `<UserMenu user={user} />`
  - Import from `@/components/auth/user-menu`
- `frontend/src/routes/__root.tsx`
  - Get `user` from `useAuth()`, map `User` type (`{id: number, email, username}`) → UserMenu shape (`{id: string, name, email, provider: null}`)
  - Pass as prop to `<Navbar01 user={...} />`

---

## Task 4: Improve Dashboard Title Section

**File:** `frontend/src/routes/dashboard.tsx`
- Replace h1/p with personalized greeting using `useAuth().user.username`
- Hierarchy: greeting `text-2xl font-semibold text-gray-900`, subtitle `text-sm text-gray-500`
- Add translation keys: `dashboard.greeting` = `"Welcome back, {{name}}"`

**Files:** `frontend/src/locales/en/translation.json`, `frontend/src/locales/pl/translation.json`

---

## Task 5: Add Loading Skeleton & Improve Error/Empty States

**File:** `frontend/src/routes/dashboard.tsx`
- Loading: full-page skeleton matching dashboard layout — pulsing title bar + 2-col grid with card placeholders using Tailwind `animate-pulse` + `bg-gray-200 rounded-lg`
- Wrap skeleton in the same gradient background (`from-violet-50 via-purple-50 to-indigo-100`)
- Error state: centered card with `AlertCircle` icon + message
- No-data state: centered card with illustration text + CTA feel
- Human collaboration: design decision on skeleton card layout

---

## Verification

1. `cd frontend && npm run dev` → navigate to `/dashboard`
2. Navbar: avatar with initials visible, dropdown shows name/email/logout
3. Title: personalized greeting with username
4. Throttle network in DevTools → see skeleton loader on dashboard
5. No `AppHeader` remnants anywhere
6. `npx tsc --noEmit` — no type errors
