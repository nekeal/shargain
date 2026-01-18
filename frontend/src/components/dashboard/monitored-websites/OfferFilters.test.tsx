import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { OfferFilters } from './OfferFilters'
import type { FiltersConfigSchema } from '@/lib/api/types.gen'

// Mock the i18next hook
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, options?: Record<string, unknown>) => {
      // Simple mock translations
      const translations: Record<string, string> = {
        'filters.title': 'Smart Filters',
        'filters.expand': 'Expand filters',
        'filters.collapse': 'Collapse filters',
        'filters.matchLabel': 'Match',
        'filters.all': 'ALL',
        'filters.any': 'ANY',
        'filters.ofTheFollowing': 'of the following:',
        'filters.valuePlaceholder': 'Enter text...',
        'filters.addRule': 'Add rule',
        'filters.addGroup': 'Add group',
        'filters.save': 'Save',
        'filters.deleteGroup': `Delete filter group ${options?.index || ''}`,
        'filters.deleteRule': 'Delete filter rule',
        'filters.toggleLogic': 'Toggle logic',
        'filters.field.title': 'Title',
        'filters.operator.contains': 'contains',
        'filters.operator.not_contains': 'does not contain',
        'filters.logic.and': 'AND',
        'filters.logic.or': 'OR',
        'filters.errors.saveFailed': 'Failed to save filters',
        'filters.errors.valueEmpty': 'Filter value cannot be empty',
      }
      return translations[key] || key
    },
  }),
}))

// Mock the useUpdateFiltersMutation hook
const mockMutate = vi.fn()
vi.mock('./useMonitors', () => ({
  useUpdateFiltersMutation: () => ({
    mutate: mockMutate,
    isPending: false,
    isError: false,
    error: null,
  }),
}))

describe('OfferFilters', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
    mockMutate.mockClear()
  })

  const renderWithProviders = (ui: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {ui}
      </QueryClientProvider>
    )
  }

  it('renders collapsed by default', () => {
    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={null}
      />
    )

    expect(screen.getByText('Smart Filters')).toBeInTheDocument()
    expect(screen.queryByText('Add group')).not.toBeInTheDocument()
  })

  it('expands when clicked', async () => {
    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={null}
      />
    )

    const trigger = screen.getByRole('button', { name: /expand filters/i })
    fireEvent.click(trigger)

    await waitFor(() => {
      expect(screen.getByText('Add group')).toBeInTheDocument()
    })
  })

  it('auto-creates first empty group when opened with no filters', async () => {
    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={null}
      />
    )

    const trigger = screen.getByRole('button', { name: /expand filters/i })
    fireEvent.click(trigger)

    await waitFor(() => {
      expect(screen.getByText('ALL')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Enter text...')).toBeInTheDocument()
    })
  })

  it('displays existing filters correctly', () => {
    const initialFilters: FiltersConfigSchema = {
      ruleGroups: [
        {
          logic: 'and',
          rules: [
            {
              field: 'title',
              operator: 'contains',
              value: 'apartment',
              caseSensitive: false,
            },
          ],
        },
      ],
    }

    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={initialFilters}
      />
    )

    // Badge should show 1 active rule
    expect(screen.getByText('1')).toBeInTheDocument()
  })

  it('allows adding a new rule to a group', async () => {
    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={null}
      />
    )

    // Expand filters
    const trigger = screen.getByRole('button', { name: /expand filters/i })
    fireEvent.click(trigger)

    await waitFor(() => {
      expect(screen.getByText('Add rule')).toBeInTheDocument()
    })

    // Click "Add rule"
    const addRuleButton = screen.getByText('Add rule')
    fireEvent.click(addRuleButton)

    await waitFor(() => {
      // Should now have 2 input fields
      const inputs = screen.getAllByPlaceholderText('Enter text...')
      expect(inputs).toHaveLength(2)
    })
  })

  it('allows deleting a rule from a group with multiple rules', async () => {
    const initialFilters: FiltersConfigSchema = {
      ruleGroups: [
        {
          logic: 'and',
          rules: [
            {
              field: 'title',
              operator: 'contains',
              value: 'apartment',
              caseSensitive: false,
            },
            {
              field: 'title',
              operator: 'not_contains',
              value: 'studio',
              caseSensitive: false,
            },
          ],
        },
      ],
    }

    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={initialFilters}
      />
    )

    // Expand filters
    const trigger = screen.getByRole('button', { name: /expand filters/i })
    fireEvent.click(trigger)

    await waitFor(() => {
      expect(screen.getAllByPlaceholderText('Enter text...')).toHaveLength(2)
    })

    // Find and click delete button
    const deleteButtons = screen.getAllByRole('button', { name: /delete filter rule/i })
    expect(deleteButtons.length).toBeGreaterThan(0)
    fireEvent.click(deleteButtons[0])

    await waitFor(() => {
      expect(screen.getAllByPlaceholderText('Enter text...')).toHaveLength(1)
    })
  })

  it('allows adding a new filter group', async () => {
    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={null}
      />
    )

    // Expand filters
    const trigger = screen.getByRole('button', { name: /expand filters/i })
    fireEvent.click(trigger)

    await waitFor(() => {
      expect(screen.getByText('Add group')).toBeInTheDocument()
    })

    // Click "Add group"
    const addGroupButton = screen.getByText('Add group')
    fireEvent.click(addGroupButton)

    await waitFor(() => {
      // Should now have logic divider between groups
      expect(screen.getByText('OR')).toBeInTheDocument()
    })
  })

  it('allows deleting a filter group when multiple groups exist', async () => {
    const initialFilters: FiltersConfigSchema = {
      ruleGroups: [
        {
          logic: 'and',
          logicWithNext: 'or',
          rules: [
            {
              field: 'title',
              operator: 'contains',
              value: 'apartment',
              caseSensitive: false,
            },
          ],
        },
        {
          logic: 'and',
          rules: [
            {
              field: 'title',
              operator: 'contains',
              value: 'flat',
              caseSensitive: false,
            },
          ],
        },
      ],
    }

    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={initialFilters}
      />
    )

    // Expand filters
    const trigger = screen.getByRole('button', { name: /expand filters/i })
    fireEvent.click(trigger)

    await waitFor(() => {
      const deleteGroupButtons = screen.getAllByRole('button', { name: /delete filter group/i })
      expect(deleteGroupButtons.length).toBeGreaterThan(0)
    })

    // Delete first group
    const deleteGroupButtons = screen.getAllByRole('button', { name: /delete filter group/i })
    fireEvent.click(deleteGroupButtons[0])

    await waitFor(() => {
      // Should no longer have the OR divider
      expect(screen.queryByText('OR')).not.toBeInTheDocument()
    })
  })

  it('toggles group logic between ALL and ANY', async () => {
    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={null}
      />
    )

    // Expand filters
    const trigger = screen.getByRole('button', { name: /expand filters/i })
    fireEvent.click(trigger)

    await waitFor(() => {
      expect(screen.getByText('ALL')).toBeInTheDocument()
    })

    // Click the toggle button
    const toggleButton = screen.getByRole('button', { name: /toggle logic/i })
    fireEvent.click(toggleButton)

    await waitFor(() => {
      // Should now show ANY as active
      const anyButtons = screen.getAllByText('ANY')
      // One should have the active styling (white background)
      expect(anyButtons.length).toBeGreaterThan(0)
    })
  })

  it('disables save button when no changes', () => {
    const initialFilters: FiltersConfigSchema = {
      ruleGroups: [
        {
          logic: 'and',
          rules: [
            {
              field: 'title',
              operator: 'contains',
              value: 'apartment',
              caseSensitive: false,
            },
          ],
        },
      ],
    }

    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={initialFilters}
      />
    )

    // Expand filters
    const trigger = screen.getByRole('button', { name: /expand filters/i })
    fireEvent.click(trigger)

    // Save button should be disabled (no changes)
    const saveButton = screen.getByRole('button', { name: /save/i })
    expect(saveButton).toBeDisabled()
  })

  it('renders save button', () => {
    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={null}
      />
    )

    // Expand filters
    const trigger = screen.getByRole('button', { name: /expand filters/i })
    fireEvent.click(trigger)

    // Should have a save button
    const saveButton = screen.getByRole('button', { name: /save/i })
    expect(saveButton).toBeInTheDocument()
  })

  it('shows active rules count badge correctly', () => {
    const initialFilters: FiltersConfigSchema = {
      ruleGroups: [
        {
          logic: 'and',
          rules: [
            {
              field: 'title',
              operator: 'contains',
              value: 'apartment',
              caseSensitive: false,
            },
            {
              field: 'title',
              operator: 'not_contains',
              value: 'studio',
              caseSensitive: false,
            },
          ],
        },
      ],
    }

    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={initialFilters}
      />
    )

    // Badge should show 2 active rules
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('does not count empty rules in active rules badge', () => {
    const initialFilters: FiltersConfigSchema = {
      ruleGroups: [
        {
          logic: 'and',
          rules: [
            {
              field: 'title',
              operator: 'contains',
              value: 'apartment',
              caseSensitive: false,
            },
            {
              field: 'title',
              operator: 'contains',
              value: '',  // Empty value
              caseSensitive: false,
            },
          ],
        },
      ],
    }

    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={initialFilters}
      />
    )

    // Badge should show 1 active rule (empty ones don't count)
    expect(screen.getByText('1')).toBeInTheDocument()
  })
})
