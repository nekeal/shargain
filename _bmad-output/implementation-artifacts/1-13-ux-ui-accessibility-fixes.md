# Story 1.13: UX/UI Accessibility & Usability Fixes

Status: ready-for-dev

## Story

As a **user with disabilities or using mobile devices**,
I want **the application to be fully accessible and usable across all devices**,
so that **I can effectively manage my offer monitoring without barriers**.

## Background & Context

This story addresses critical findings from a comprehensive UX/UI audit conducted on 2026-01-17. The audit identified accessibility violations (WCAG 2.1), mobile usability issues, and user experience friction points that must be resolved before public launch.

**Audit Source:** Professional UX/UI audit analyzing all frontend components, routes, and user flows.

## Acceptance Criteria

### AC1: Icon-Only Buttons Have Accessible Labels
- All icon-only buttons throughout the application have appropriate `aria-label` attributes
- Screen reader users can understand the purpose of every interactive element
- **Files:** `monitored-websites/index.tsx`, `OfferFilters.tsx`

### AC2: Destructive Actions Require Confirmation
- Delete actions for URLs display a confirmation dialog before executing
- Delete actions for filter rules have appropriate safeguards
- Confirmation dialogs are accessible (focus trapped, escape to close)

### AC3: Touch Targets Meet WCAG Minimum (44x44px)
- All interactive elements have minimum 44x44px touch targets on mobile
- Filter delete buttons increased from ~20x20px to minimum 44x44px
- URL action buttons have adequate touch area

### AC4: Console Logs Removed from Production Code
- No `console.log` statements in production builds that expose user data
- Debug statements removed or wrapped in development-only checks
- **Files:** `dashboard.tsx:13`, `hey-api-config.ts`

### AC5: Error Handling is Type-Safe and User-Friendly
- Error messages use proper TypeScript types (no `as any`)
- Fallback messages for unexpected error structures
- Error display components are consistent across the application
- **Files:** `monitored-websites/index.tsx:193`

### AC6: Mobile Filter UI is Usable
- Filter rules don't overflow or cramp on mobile screens
- Error messages visible on all breakpoints (not hidden on desktop)
- Responsive breakpoints use `md:` consistently (not mixed `sm:`/`md:`)

### AC7: Dead Code Removed
- Unused `Header.tsx` component removed
- Empty `AppHeader.tsx` component removed or properly implemented
- No orphaned components in the codebase

### AC8: Loading States Show Visual Feedback
- Dashboard loading state displays spinner (not plain text)
- Consistent loading indicators across all pages
- Skeleton screens considered for better perceived performance

## Tasks / Subtasks

- [ ] **Task 1: Fix Icon-Only Button Accessibility** (AC: #1)
  - [ ] 1.1 Add `aria-label` to Eye/EyeOff toggle buttons in monitored-websites/index.tsx
  - [ ] 1.2 Add `aria-label` to Trash delete buttons in monitored-websites/index.tsx
  - [ ] 1.3 Add `aria-label` to X delete buttons in OfferFilters.tsx
  - [ ] 1.4 Audit all other icon-only buttons and add labels

- [ ] **Task 2: Implement Delete Confirmation Dialogs** (AC: #2)
  - [ ] 2.1 Create reusable ConfirmationDialog component using shadcn Dialog
  - [ ] 2.2 Wrap URL delete action with confirmation dialog
  - [ ] 2.3 Ensure dialog traps focus and handles keyboard navigation

- [ ] **Task 3: Increase Touch Targets** (AC: #3)
  - [ ] 3.1 Update OfferFilters.tsx delete buttons from `p-0.5` to `p-2` minimum
  - [ ] 3.2 Update URL action buttons to use `size="default"` on mobile
  - [ ] 3.3 Verify all interactive elements meet 44x44px minimum

- [ ] **Task 4: Remove Debug Console Logs** (AC: #4)
  - [ ] 4.1 Remove `console.log` from dashboard.tsx line 13
  - [ ] 4.2 Remove `console.log` from hey-api-config.ts
  - [ ] 4.3 Search for any other production console.log statements

- [ ] **Task 5: Fix Error Handling Type Safety** (AC: #5)
  - [ ] 5.1 Define proper error type interface for API errors
  - [ ] 5.2 Replace `as any` with type-safe error parsing in monitored-websites
  - [ ] 5.3 Add fallback error message for unexpected error structures
  - [ ] 5.4 Create reusable ErrorMessage component for consistency

- [ ] **Task 6: Improve Mobile Filter Layout** (AC: #6)
  - [ ] 6.1 Fix error message visibility (remove `sm:hidden` that hides on desktop)
  - [ ] 6.2 Standardize responsive breakpoints to use `md:` consistently
  - [ ] 6.3 Stack filter selectors vertically on mobile for better usability
  - [ ] 6.4 Test filter UI on various mobile screen sizes

- [ ] **Task 7: Remove Dead Code** (AC: #7)
  - [ ] 7.1 Delete unused Header.tsx component
  - [ ] 7.2 Remove or implement AppHeader.tsx (currently returns empty fragment)
  - [ ] 7.3 Verify no import errors after removal

- [ ] **Task 8: Improve Loading States** (AC: #8)
  - [ ] 8.1 Replace plain text "Loading..." with spinner in dashboard.tsx
  - [ ] 8.2 Create consistent LoadingSpinner component
  - [ ] 8.3 Apply loading spinner to all loading states

## Dev Notes

### Critical Architecture Patterns

**Component Library:** shadcn/ui - All UI primitives must come from `src/components/ui/`
**Styling:** TailwindCSS with violet/purple gradient theme
**State Management:** TanStack Query for server state, React Context for UI state
**Routing:** TanStack Router with file-based routing

### Source Files to Modify

```
frontend/src/
├── components/
│   ├── app-header.tsx              # REMOVE or implement
│   ├── Header.tsx                  # REMOVE (dead code)
│   ├── dashboard/
│   │   └── monitored-websites/
│   │       ├── index.tsx           # AC1, AC2, AC5 - Add aria-labels, confirmation, error handling
│   │       └── OfferFilters.tsx    # AC1, AC3, AC6 - Touch targets, mobile layout
│   └── ui/
│       └── (new) confirmation-dialog.tsx  # AC2 - New component
├── routes/
│   └── dashboard.tsx               # AC4, AC8 - Remove console.log, improve loading
└── hey-api-config.ts               # AC4 - Remove console.log
```

### WCAG 2.1 Compliance Requirements

- **1.1.1 Non-text Content:** All icon buttons need text alternatives (aria-label)
- **2.5.5 Target Size:** Minimum 44x44 CSS pixels for touch targets
- **4.1.2 Name, Role, Value:** All UI components must have accessible names

### Testing Checklist

1. **Screen Reader Testing:**
   - Navigate entire app with VoiceOver/NVDA
   - Verify all buttons announce their purpose
   - Confirm dialogs announce properly

2. **Mobile Testing:**
   - Test on 320px width viewport (iPhone SE)
   - Test on 375px width viewport (iPhone 12)
   - Verify touch targets with finger (not mouse)

3. **Keyboard Testing:**
   - Tab through all interactive elements
   - Verify focus visible on all elements
   - Test Escape closes dialogs

### Existing Patterns to Follow

**Button with aria-label example:**
```tsx
<Button
  size="sm"
  variant="outline"
  aria-label={url.isActive ? "Pause monitoring" : "Resume monitoring"}
  onClick={() => toggleUrlActiveMutation.mutate(...)}
>
  {url.isActive ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
</Button>
```

**Confirmation Dialog pattern (create new):**
```tsx
<Dialog open={isDeleteConfirmOpen} onOpenChange={setIsDeleteConfirmOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Delete URL?</DialogTitle>
      <DialogDescription>
        This will permanently remove "{url.name}" from your monitored list.
      </DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <Button variant="outline" onClick={() => setIsDeleteConfirmOpen(false)}>
        Cancel
      </Button>
      <Button variant="destructive" onClick={handleDelete}>
        Delete
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

**Touch target sizing:**
```tsx
// BAD: Too small (~20x20px)
<button className="p-0.5">
  <X className="w-3.5 h-3.5" />
</button>

// GOOD: Meets minimum (44x44px)
<button className="p-2 min-w-[44px] min-h-[44px] flex items-center justify-center">
  <X className="w-4 h-4" />
</button>
```

### Error Type Definition

Create in `frontend/src/types/api-errors.ts`:
```typescript
export interface ApiValidationError {
  detail: Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}

export function getApiErrorMessage(error: unknown): string {
  if (error && typeof error === 'object' && 'detail' in error) {
    const apiError = error as ApiValidationError;
    return apiError.detail?.[0]?.msg ?? 'An unexpected error occurred';
  }
  return 'An unexpected error occurred';
}
```

### Project Structure Notes

- Alignment with unified project structure (paths, modules, naming): **Fully aligned**
- All new components go in appropriate directories per architecture.md
- No new dependencies required - uses existing shadcn/ui components

### References

- [Source: frontend/src/components/dashboard/monitored-websites/index.tsx#L251-265] Icon buttons without aria-labels
- [Source: frontend/src/components/dashboard/monitored-websites/OfferFilters.tsx#L264-275] Small touch targets
- [Source: frontend/src/routes/dashboard.tsx#L13] Console.log exposure
- [Source: _bmad-output/planning-artifacts/architecture/frontend-architecture.md] Component strategy
- [Source: UX/UI Audit Report 2026-01-17] Comprehensive audit findings

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
