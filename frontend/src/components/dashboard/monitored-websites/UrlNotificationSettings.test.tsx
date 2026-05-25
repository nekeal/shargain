import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { UrlNotificationSettings } from './UrlNotificationSettings'
import type { WaypointSchema } from '@/lib/api/types.gen'

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}))

const mockMutate = vi.fn()
vi.mock('./useMonitors', () => ({
  useUpdateUrlMutation: () => ({
    mutate: mockMutate,
    isPending: false,
    isError: false,
    error: null,
    isSuccess: false,
  }),
}))

describe('UrlNotificationSettings', () => {
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

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  const renderWithProviders = (ui: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {ui}
      </QueryClientProvider>
    )
  }

  it('renders waypoint rows when showLocationMap is on and waypoints are provided', () => {
    const waypoints: Array<WaypointSchema> = [
      { name: 'Metro Centrum', lat: 52.23, lon: 21.0 },
    ]

    renderWithProviders(
      <UrlNotificationSettings
        targetId={1}
        urlId={1}
        initialShowLocationMap={true}
        initialWaypoints={waypoints}
      />,
    )

    const trigger = screen.getByRole('button', {
      name: /filters.notificationSettingsExpand/,
    })
    fireEvent.click(trigger)

    expect(screen.getByDisplayValue('Metro Centrum')).toBeInTheDocument()
  })

  it('adds a new empty waypoint row when clicking Add Waypoint', async () => {
    renderWithProviders(
      <UrlNotificationSettings
        targetId={1}
        urlId={1}
        initialShowLocationMap={true}
        initialWaypoints={[]}
      />,
    )

    const trigger = screen.getByRole('button', {
      name: /filters.notificationSettingsExpand/,
    })
    fireEvent.click(trigger)

    const addButton = screen.getByText('filters.addWaypoint')
    fireEvent.click(addButton)

    await waitFor(() => {
      const nameInput = screen.getByPlaceholderText('filters.waypointNamePlaceholder')
      expect(nameInput).toBeInTheDocument()
    })
  })

  it('opens modal when clipboard is unavailable and fills waypoint from URL', async () => {
    vi.stubGlobal('navigator', {
      clipboard: {
        readText: vi.fn().mockRejectedValue(new Error('No clipboard access')),
      },
    })

    const waypoints: Array<WaypointSchema> = [
      { name: '', lat: 0, lon: 0 },
    ]

    renderWithProviders(
      <UrlNotificationSettings
        targetId={1}
        urlId={1}
        initialShowLocationMap={true}
        initialWaypoints={waypoints}
      />,
    )

    const trigger = screen.getByRole('button', {
      name: /filters.notificationSettingsExpand/,
    })
    fireEvent.click(trigger)

    const pasteButton = screen.getByRole('button', {
      name: /filters.pasteFromClipboard/,
    })
    fireEvent.click(pasteButton)

    await waitFor(() => {
      expect(screen.getByText('filters.addFromGoogleMaps')).toBeInTheDocument()
    })

    const modalInput = screen.getByPlaceholderText('filters.googleMapsUrlPlaceholder')
    fireEvent.change(modalInput, {
      target: { value: 'https://www.google.com/maps/place/Warsaw/@52.237049,21.017532' },
    })

    const parseButton = screen.getByText('filters.parse')
    fireEvent.click(parseButton)

    await waitFor(() => {
      const latInput = screen.getByDisplayValue('52.237049')
      expect(latInput).toBeInTheDocument()
    })
  })

  it('calls mutation with waypoints when saving', async () => {
    renderWithProviders(
      <UrlNotificationSettings
        targetId={1}
        urlId={1}
        initialShowLocationMap={true}
        initialWaypoints={[]}
      />,
    )

    const trigger = screen.getByRole('button', {
      name: /filters.notificationSettingsExpand/,
    })
    fireEvent.click(trigger)

    const addButton = screen.getByText('filters.addWaypoint')
    fireEvent.click(addButton)

    const nameInput = screen.getByPlaceholderText('filters.waypointNamePlaceholder')
    fireEvent.change(nameInput, { target: { value: 'Test Waypoint' } })

    const saveButton = screen.getByRole('button', { name: /filters.save/ })
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith({
        showLocationMapInNotifications: true,
        waypoints: [{ name: 'Test Waypoint', lat: 0, lon: 0 }],
      })
    })
  })
})
