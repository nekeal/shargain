import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { TargetSelectorInline } from './target-selector-inline'
import type { TargetSummaryResponse } from '@/lib/api/types.gen'

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'dashboard.targetSelector.selectPlaceholder': 'Select a target',
        'dashboard.monitoredWebsites.active': 'Active',
        'dashboard.monitoredWebsites.paused': 'Paused',
      }
      return translations[key] || key
    },
  }),
}))

const mockTargets: Array<TargetSummaryResponse> = [
  { id: 1, name: 'Target A', isActive: true, enableNotifications: true, urlCount: 5 },
  { id: 2, name: 'Target B', isActive: false, enableNotifications: false, urlCount: 3 },
]

describe('TargetSelectorInline', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
    Element.prototype.scrollIntoView = vi.fn()
  })

  const renderWithProviders = (ui: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {ui}
      </QueryClientProvider>
    )
  }

  it('shows placeholder when no target selected', () => {
    renderWithProviders(
      <TargetSelectorInline
        targets={mockTargets}
        selectedTargetId={null}
        onSelect={vi.fn()}
      />
    )

    expect(screen.getByText('Select a target')).toBeInTheDocument()
  })

  it('renders all target names in the select dropdown', async () => {
    renderWithProviders(
      <TargetSelectorInline
        targets={mockTargets}
        selectedTargetId={null}
        onSelect={vi.fn()}
      />
    )

    const trigger = screen.getByRole('combobox')
    fireEvent.click(trigger)

    await waitFor(() => {
      expect(screen.getByText('Target A')).toBeInTheDocument()
      expect(screen.getByText('Target B')).toBeInTheDocument()
    })
  })

  it('calls onSelect with correct target id when a target is chosen', async () => {
    const onSelect = vi.fn()
    renderWithProviders(
      <TargetSelectorInline
        targets={mockTargets}
        selectedTargetId={null}
        onSelect={onSelect}
      />
    )

    const trigger = screen.getByRole('combobox')
    fireEvent.click(trigger)

    await waitFor(() => {
      expect(screen.getByText('Target A')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Target A'))

    expect(onSelect).toHaveBeenCalledWith(1)
  })

  it('shows active badge for active targets and paused badge for paused targets', async () => {
    renderWithProviders(
      <TargetSelectorInline
        targets={mockTargets}
        selectedTargetId={null}
        onSelect={vi.fn()}
      />
    )

    const trigger = screen.getByRole('combobox')
    fireEvent.click(trigger)

    await waitFor(() => {
      expect(screen.getByText('Active')).toBeInTheDocument()
      expect(screen.getByText('Paused')).toBeInTheDocument()
    })
  })
})
