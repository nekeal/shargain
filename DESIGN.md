---
name: Shargain
description: Precision offer monitoring for Polish classifieds
colors:
  primary: "#7C3AED"
  primary-deep: "#5B21B6"
  primary-foreground: "#FFFFFF"
  secondary: "#F5F3FF"
  secondary-foreground: "#4C1D95"
  destructive: "#DC2626"
  destructive-foreground: "#FFFFFF"
  muted: "#F5F3FF"
  muted-foreground: "#6B7280"
  accent: "#F5F3FF"
  accent-foreground: "#4C1D95"
  background: "#FFFFFF"
  foreground: "#111827"
  card: "#FFFFFF"
  card-foreground: "#111827"
  popover: "#FFFFFF"
  popover-foreground: "#111827"
  border: "#E5E7EB"
  input: "#E5E7EB"
  ring: "#7C3AED"
  chart-1: "#7C3AED"
  chart-2: "#06B6D4"
  chart-3: "#84CC16"
  chart-4: "#F59E0B"
  chart-5: "#EC4899"
  sidebar: "#FAFAFA"
  sidebar-foreground: "#111827"
  sidebar-primary: "#7C3AED"
  sidebar-primary-foreground: "#FFFFFF"
  sidebar-accent: "#F5F3FF"
  sidebar-accent-foreground: "#4C1D95"
  sidebar-border: "#E5E7EB"
  sidebar-ring: "#7C3AED"
typography:
  display:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "clamp(2rem, 5vw, 3.5rem)"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "clamp(1.5rem, 3vw, 2.25rem)"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  title:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0"
  body:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "0"
  label:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "0.01em"
  mono:
    fontFamily: "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0"
rounded:
  sm: "4px"
  md: "6px"
  lg: "8px"
  xl: "12px"
  full: "9999px"
spacing:
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.primary-foreground}"
    rounded: "{rounded.md}"
    padding: "12px 24px"
    typography: "{typography.label}"
  button-primary-hover:
    backgroundColor: "{colors.primary-deep}"
    textColor: "{colors.primary-foreground}"
    rounded: "{rounded.md}"
    padding: "12px 24px"
    typography: "{typography.label}"
  button-outline:
    backgroundColor: "transparent"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: "12px 24px"
    typography: "{typography.label}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.foreground}"
    rounded: "{rounded.md}"
    padding: "12px 24px"
    typography: "{typography.label}"
  button-destructive:
    backgroundColor: "{colors.destructive}"
    textColor: "{colors.destructive-foreground}"
    rounded: "{rounded.md}"
    padding: "12px 24px"
    typography: "{typography.label}"
  card-default:
    backgroundColor: "{colors.card}"
    textColor: "{colors.card-foreground}"
    rounded: "{rounded.xl}"
    padding: "24px"
  input-default:
    backgroundColor: "transparent"
    textColor: "{colors.foreground}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
    typography: "{typography.body}"
  badge-default:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.primary-foreground}"
    rounded: "{rounded.md}"
    padding: "4px 8px"
    typography: "{typography.label}"
  select-trigger:
    backgroundColor: "transparent"
    textColor: "{colors.foreground}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
    typography: "{typography.body}"
  dialog-content:
    backgroundColor: "{colors.background}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.lg}"
    padding: "24px"
  dropdown-content:
    backgroundColor: "{colors.popover}"
    textColor: "{colors.popover-foreground}"
    rounded: "{rounded.md}"
    padding: "4px"
  switch-thumb:
    backgroundColor: "{colors.background}"
    rounded: "{rounded.full}"
  switch-track-checked:
    backgroundColor: "{colors.primary}"
    rounded: "{rounded.full}"
  switch-track-unchecked:
    backgroundColor: "{colors.input}"
    rounded: "{rounded.full}"
  tabs-trigger:
    backgroundColor: "transparent"
    textColor: "{colors.foreground}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
    typography: "{typography.label}"
  tabs-trigger-active:
    backgroundColor: "{colors.background}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
    typography: "{typography.label}"
---

# Design System: Shargain

## 1. Overview

**Creative North Star: "The Calibrated Monitor"**

Shargain is a precision instrument for monitoring Polish classifieds. Like a calibrated sensor, it does one thing exceptionally well: you configure exactly what to watch (URLs, filters, notification channel), and it delivers exactly what matches — nothing more, nothing less. No engagement loops, no algorithmic feed, no "discovery" features. The system polls, filters, and notifies. That is the whole product.

The visual system reflects this clarity. Violet/indigo is the primary accent — purposeful, not decorative — used only on primary actions and key status indicators. Surfaces are clean white (light) or deep charcoal (dark) with subtle borders. Shadows appear only as a response to interaction (hover, focus, elevation), never at rest. Typography uses the system font stack at readable sizes with generous line height. Every component has a sharp, professional affordance: clear boundaries, predictable states, no ambiguity.

This system explicitly rejects:
- **Generic SaaS dashboards** — rounded-card grids, purple gradients everywhere, hollow "AI-powered" badges, meaningless friendly illustrations
- **Classifieds site UI (OLX, etc.)** — dense tables, aggressive upsells, visual noise, mystery-meat navigation, cluttered filter sidebars
- **Notification spam** — intrusive, irrelevant, hard-to-control alerts that train users to ignore them

**Key Characteristics:**
- Signal over chrome: visual hierarchy serves information density, not marketing
- Configuration is the product: URL entry, filter construction, channel setup are precise and fast
- Quotas are visible, not punitive: usage shown prominently, warned at 90%, paused cleanly at 100%
- Telegram is the delivery layer, not the product: web dashboard configures; bot delivers
- Dark mode is a first-class citizen: both themes are complete, no contrast compromises

## 2. Colors

A purposeful violet/indigo accent on a neutral canvas. The primary (oklch(0.606 0.25 292.717) ≈ #7C3AED) carries brand identity and marks primary actions. It appears on ≤10% of any screen — its rarity is the point. Neutrals are true grays (chroma ≈ 0) in both themes; no warm/cool tint by default.

### Primary
- **Purposeful Violet** (#7C3AED / oklch(0.606 0.25 292.717)): Primary actions (CTAs, save buttons), active navigation, key status indicators (active badges, connected channel). In dark mode: slightly lighter (oklch(0.541 0.281 293.009)) for contrast.
- **Deep Violet** (#5B21B6 / oklch(0.5 0.25 292)): Hover/active state for primary buttons. Never used as a background wash.

### Secondary
- **Violet Tint** (#F5F3FF / oklch(0.97 0.03 292)): Subtle backgrounds for selected states, hover on outline buttons, badge backgrounds for secondary info. Dark mode: #4C1D95 (oklch(0.3 0.15 292)) for same role.

### Destructive
- **Signal Red** (#DC2626 / oklch(0.577 0.245 27.325)): Destructive actions (delete, disconnect), error states, quota exceeded warnings. Dark mode: lighter (#EF4444 / oklch(0.704 0.191 22.216)).

### Neutral
- **White** (#FFFFFF / oklch(1 0 0)): Page background, card background, popover background (light)
- **Charcoal** (#111827 / oklch(0.141 0.005 285.823)): Primary text, headings (light)
- **Medium Gray** (#6B7280 / oklch(0.552 0.016 285.938)): Muted text, placeholders, secondary labels (light)
- **Border Gray** (#E5E7EB / oklch(0.92 0.004 286.32)): Borders, inputs, dividers (light)
- **Deep Charcoal** (#0A0A0A / oklch(0.141 0.005 285.823)): Page background (dark)
- **White** (#FAFAFA / oklch(0.985 0 0)): Primary text (dark)
- **Muted Gray** (#9CA3AF / oklch(0.705 0.015 286.067)): Muted text (dark)
- **Border Dark** (rgba(255,255,255,0.1) / oklch(1 0 0 / 10%)): Borders, inputs (dark)

**The Restrained Accent Rule.** The primary violet appears on ≤10% of any given screen. It marks the primary action, the active nav item, the connected status — and stops there. No gradient washes, no violet card borders, no decorative accents.

## 3. Typography

**Display Font:** System UI stack (system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif)  
**Body Font:** System UI stack (same)  
**Label/Mono Font:** System UI stack for labels; ui-monospace stack for code/URLs

**Character:** One font family, multiple weights. The system stack renders crisply on all platforms, respects user preferences, and carries no brand baggage — fitting for a tool that gets out of the way.

### Hierarchy
- **Display** (700, clamp(2rem, 5vw, 3.5rem), 1.1, -0.02em): Landing page hero only. Never in dashboard.
- **Headline** (600, clamp(1.5rem, 3vw, 2.25rem), 1.2, -0.01em): Page titles (Dashboard, Settings), major section headers.
- **Title** (600, 1.125rem, 1.4, 0): Card titles, sidebar section headers, modal titles.
- **Body** (400, 1rem, 1.6, 0): All prose, descriptions, help text, notification content. Max line length 65–75ch.
- **Label** (500, 0.875rem, 1.4, 0.01em): Form labels, button text, badge text, navigation labels.
- **Mono** (400, 0.875rem, 1.5, 0): URLs, tokens, code snippets, technical identifiers.

**The One Weight Rule.** Only 400, 500, 600, 700 are used. No 300 (too light for UI), no 800/900 (too heavy, reduces readability). Weight conveys hierarchy, not size alone.

## 4. Elevation

Flat by default. Surfaces (cards, pages, inputs) have no shadow at rest — only a 1px border in `border` color. Shadows appear only as a response to state:
- **Hover/Focus**: `shadow-md` on dropdowns, `shadow-lg` on modals, subtle lift on cards
- **Elevated overlays**: Dropdown menus, dialogs, popovers use `shadow-md` to `shadow-lg` to separate from page
- **No ambient shadows**: No `shadow-sm` on resting cards, no "depth" for its own sake

### Shadow Vocabulary
- **Interaction Lift** (`0 4px 12px rgba(0,0,0,0.08)`): Card hover, button press feedback
- **Overlay Separation** (`0 10px 24px rgba(0,0,0,0.12)`): Dropdown menus, popovers, select content
- **Modal Elevation** (`0 20px 40px rgba(0,0,0,0.15)`): Dialogs, sheet overlays

**The Flat-By-Default Rule.** Surfaces are flat at rest. Shadows appear only as a response to state (hover, focus, elevation). No card shadows, no page-depth layering, no "floating" elements without interaction purpose.

## 5. Components

### Buttons
- **Shape:** `rounded-md` (6px), `h-10` (40px) default, `px-4` horizontal padding
- **Primary:** `bg-primary text-primary-foreground`, gradient `from-violet-600 to-indigo-700` → hover `from-violet-700 to-indigo-800`, `shadow-md` → `shadow-lg`. The gradient is the *only* gradient in the system.
- **Outline:** `border-2 border-violet-300 text-violet-700` → hover `bg-violet-50` (dark: `border-violet-700 text-violet-400` → `bg-violet-900/50`). Border weight (2px) distinguishes from input borders.
- **Secondary:** `bg-secondary text-secondary-foreground` → hover `bg-secondary/80`. For non-primary actions.
- **Ghost:** Transparent → hover `bg-accent text-accent-foreground`. For tertiary/navigation actions.
- **Destructive:** `bg-destructive text-destructive-foreground` → hover `bg-destructive/90`. Delete, disconnect, revoke.
- **Focus:** `focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2` on all variants.
- **Disabled:** `opacity-50 pointer-events-none` on all variants.

### Cards
- **Corner Style:** `rounded-xl` (12px) — slightly more rounded than buttons for visual nesting
- **Background:** `bg-card` (white/charcoal) with `border` (1px) stroke, no shadow at rest
- **Internal Padding:** `py-6` vertical, `px-6` horizontal via `CardContent`
- **Header:** `CardTitle` (Title typography) + optional `CardDescription` (Body, muted-foreground)
- **Hover:** `shadow-sm` → `shadow-md` transition (subtle lift on interactive cards)

### Inputs / Fields
- **Style:** `border-input` (1px), `bg-transparent`, `rounded-md`, `h-9` (36px), `px-3`
- **Focus:** `focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]` — 3px ring, no border color shift
- **Error:** `aria-invalid:border-destructive aria-invalid:ring-destructive/20`
- **Placeholder:** `text-muted-foreground`
- **Disabled:** `opacity-50 pointer-events-none cursor-not-allowed`
- **File Input:** Styled to match, `file:border-0 file:bg-transparent file:text-sm file:font-medium`

### Badges
- **Style:** `rounded-md`, `px-2 py-0.5`, `text-xs font-medium`, `inline-flex items-center gap-1`
- **Default:** `bg-primary text-primary-foreground` — status active, connected, enabled
- **Secondary:** `bg-secondary text-secondary-foreground` — status inactive, paused, info
- **Destructive:** `bg-destructive text-white` — quota exceeded, error, disabled
- **Outline:** `border-transparent bg-transparent text-foreground` → hover `bg-accent` — filter tags, categories

### Select / Dropdown Trigger
- **Style:** Matches Input (`border-input`, `rounded-md`, `h-9`, `px-3`) + trailing chevron icon
- **Focus:** Same as Input (3px ring)
- **Content:** `rounded-md border shadow-md`, `p-1` internal padding, `max-h-(--radix-select-content-available-height)`
- **Item:** `rounded-sm px-2 py-1.5 text-sm` → focus `bg-accent text-accent-foreground`, checkmark indicator

### Dialog / Modal
- **Content:** `bg-background rounded-lg border p-6 shadow-lg`, `max-w-lg`, centered with `translate-x-[-50%] translate-y-[-50%]`
- **Animation:** `zoom-in-95` + `fade-in` enter, `zoom-out-95` + `fade-out` exit (200ms)
- **Overlay:** `bg-black/50` fixed inset
- **Close Button:** Top-right, `rounded-xs opacity-70` → hover `opacity-100`, `focus:ring-2`

### Dropdown Menu
- **Content:** `rounded-md border p-1 shadow-md`, `min-w-[8rem]`
- **Item:** `rounded-sm px-2 py-1.5 text-sm` → focus `bg-accent text-accent-foreground`
- **Destructive Item:** `text-destructive` → focus `bg-destructive/10 text-destructive`
- **Separator:** `bg-border -mx-1 my-1 h-px`
- **Submenu:** `shadow-lg` (deeper than parent)

### Switch
- **Track:** `h-[1.15rem] w-8 rounded-full border border-transparent shadow-xs`
  - Unchecked: `bg-input` (light) / `bg-input/80` (dark)
  - Checked: `bg-primary`
- **Thumb:** `size-4 rounded-full bg-background` (light) / `bg-foreground` (dark unchecked) / `bg-primary-foreground` (dark checked)
- **Motion:** `translate-x` transition, `data-[state=checked]:translate-x-[calc(100%-2px)]`
- **Focus:** `focus-visible:ring-3 focus-visible:ring-ring/50`

### Tabs
- **List:** `bg-muted rounded-lg p-[3px] inline-flex`
- **Trigger:** `rounded-md border border-transparent px-2 py-1 text-sm font-medium`
  - Inactive: `text-muted-foreground` (dark: `text-muted-foreground`)
  - Active: `bg-background text-foreground shadow-sm` (dark: `bg-input/30 text-foreground border-input`)
- **Focus:** `focus-visible:ring-3 focus-visible:ring-ring/50`

### Navigation (shared focus ring)

## 6. Do's and Don'ts

### Do:
- **Do** use the primary violet only on the primary action, active nav, and key status — ≤10% of screen area
- **Do** keep surfaces flat at rest; add shadows only on hover, focus, or overlay elevation
- **Do** show quota usage prominently: "67/100 this month", warn at 90% ("90/100 — upgrade soon"), pause cleanly at 100% with reset date
- **Do** use the system font stack at 1rem/1.6 line height for body; cap line length at 65–75ch
- **Do** make configuration inline and immediate: URL validation on blur, filter builder with live preview, channel connection with real-time status
- **Do** respect `prefers-reduced-motion`: all transitions become instant or crossfade
- **Do** use `text-wrap: balance` on headlines; `text-wrap: pretty` on body prose
- **Do** ensure 4.5:1 contrast on all text (including placeholders and muted text) in both themes
- **Do** use semantic HTML and ARIA for dynamic content: loading states, toast notifications, filter builder announcements

### Don't:
- **Don't** use gradient washes, violet card borders, or decorative violet accents — the primary color is for action and status only
- **Don't** replicate classifieds UI density: no dense tables, no mystery-meat icons, no cluttered filter sidebars
- **Don't** hide quota state or surprise users with silent notification failures — quotas are visible, honest, and communicated
- **Don't** use `border-left`/`border-right` >1px as colored stripes on cards or list items — use full borders, background tints, or leading icons instead
- **Don't** use `background-clip: text` gradient text — emphasis via weight or size only
- **Don't** use glassmorphism/backdrop-blur decoratively — only the navbar uses `backdrop-blur` for sticky positioning
- **Don't** use identical card grids with icon+heading+text repeated endlessly — card content varies by purpose
- **Don't** put tiny uppercase tracked eyebrows ("DASHBOARD", "SETTINGS") above every section — one deliberate kicker if needed
- **Don't** number section markers (01/02/03) unless the sequence carries real information
- **Don't** let headings overflow containers — test at every breakpoint; reduce clamp max or rewrite copy
- **Don't** rely on color alone for status — always pair with icon, label, or pattern (colorblind-safe)
- **Don't** gate content visibility on class-triggered transitions — default state must be visible