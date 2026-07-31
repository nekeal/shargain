import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
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
        'filters.noFilters': 'All offers will notify',
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

// Mock the useUpdateUrlMutation hook
const mockMutate = vi.fn()
vi.mock('./useMonitors', () => ({
  useUpdateUrlMutation: () => ({
    mutate: mockMutate,
    isPending: false,
    isError: false,
    error: null,
  }),
}))

// Mock useAvailableFields
vi.mock('@/hooks/useAvailableFields', () => ({
  useAvailableFields: () => ({
    data: { fields: [{ name: 'title', label: 'Title', type: 'string', operators: [{ value: 'contains', label: 'contains' }, { value: 'not_contains', label: 'does not contain' }] }] },
    isLoading: false,
    isError: false,
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

  it('shows empty state when opened with no filters', async () => {
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
      expect(screen.getByText('All offers will notify')).toBeInTheDocument()
      expect(screen.queryByPlaceholderText('Enter text...')).not.toBeInTheDocument()
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
      expect(screen.getByText('Add group')).toBeInTheDocument()
    })

    // Create first group
    fireEvent.click(screen.getByText('Add group'))

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

    // Click "Add group" twice to create two groups
    fireEvent.click(screen.getByText('Add group'))
    fireEvent.click(screen.getByText('Add group'))

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

  it('allows deleting the last rule, clearing all filters', async () => {
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

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter text...')).toBeInTheDocument()
    })

    // Delete the only rule (both mobile and desktop delete buttons exist)
    const deleteButtons = screen.getAllByRole('button', { name: /delete filter rule/i })
    expect(deleteButtons.length).toBeGreaterThan(0)
    fireEvent.click(deleteButtons[0])

    // Empty state is shown and the rule row is gone
    await waitFor(() => {
      expect(screen.getByText('All offers will notify')).toBeInTheDocument()
      expect(screen.queryByPlaceholderText('Enter text...')).not.toBeInTheDocument()
    })
  })

  it('allows deleting the last group, clearing all filters', async () => {
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

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter text...')).toBeInTheDocument()
    })

    // Delete the only group
    fireEvent.click(screen.getByRole('button', { name: /delete filter group 1/i }))

    // Empty state is shown
    await waitFor(() => {
      expect(screen.getByText('All offers will notify')).toBeInTheDocument()
    })
  })

  it('saves cleared filters as null', async () => {
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

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter text...')).toBeInTheDocument()
    })

    // Delete the only rule, then save
    fireEvent.click(screen.getAllByRole('button', { name: /delete filter rule/i })[0])

    await waitFor(() => {
      expect(screen.getByText('All offers will notify')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: /save/i }))

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalled()
      expect(mockMutate.mock.calls[0][0]).toEqual({ filters: null })
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
      expect(screen.getByText('Add group')).toBeInTheDocument()
    })

    // Create first group
    fireEvent.click(screen.getByText('Add group'))

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

  it('enables save button when changes are made (e.g. editing value)', async () => {
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

    const saveButton = screen.getByRole('button', { name: /save/i })
    expect(saveButton).toBeDisabled()

    // Edit the input value
    const input = screen.getByPlaceholderText('Enter text...')
    fireEvent.change(input, { target: { value: 'villa' } })

    // Save button should now be enabled
    await waitFor(() => {
      expect(saveButton).toBeEnabled()
    })
  })

  it('enables save button when adding a new rule and typing a value', async () => {
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

    const saveButton = screen.getByRole('button', { name: /save/i })
    expect(saveButton).toBeDisabled()

    // Add a rule
    const addRuleButton = screen.getByText('Add rule')
    fireEvent.click(addRuleButton)

    // Adding a rule triggers validation, which normalizes (strips empty rules) and passes, so save is enabled
    // (the empty placeholder rule is filtered out before Zod validation)
    expect(saveButton).toBeEnabled()

    // Edit the new rule's input value
    const inputs = screen.getAllByPlaceholderText('Enter text...')
    expect(inputs).toHaveLength(2)
    fireEvent.change(inputs[1], { target: { value: 'house' } })

    // Save button should now be enabled
    await waitFor(() => {
      expect(saveButton).toBeEnabled()
    })
  })

  it('enables save button when opening from scratch (no existing filters) and adding a rule with a value', async () => {
    renderWithProviders(
      <OfferFilters
        targetId={1}
        urlId={1}
        initialFilters={null}
      />
    )

    // Expand filters (no filters exist yet)
    const trigger = screen.getByRole('button', { name: /expand filters/i })
    fireEvent.click(trigger)

    // Save button is disabled: nothing changed and nothing to save
    const saveButton = screen.getByRole('button', { name: /save/i })
    expect(saveButton).toBeDisabled()

    // Create a group and add a rule with a value
    fireEvent.click(screen.getByText('Add group'))

    const inputs = screen.getAllByPlaceholderText('Enter text...')
    expect(inputs).toHaveLength(1)
    fireEvent.change(inputs[0], { target: { value: 'house' } })

    // Save button is enabled
    await waitFor(() => {
      expect(saveButton).toBeEnabled()
    })
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
