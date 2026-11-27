import { beforeEach, describe, expect, it, vi } from "vitest"
import { fireEvent, render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { EditUrlParamsDialog } from "./EditUrlParamsDialog"
import type { ScrapingUrlResponse } from "@/lib/api/types.gen"

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}))

const mockMutate = vi.fn()
vi.mock("./useMonitors", () => ({
  useUpdateUrlMutation: () => ({
    mutate: mockMutate,
    isPending: false,
  }),
}))

describe("EditUrlParamsDialog", () => {
  let queryClient: QueryClient

  const sampleUrl: ScrapingUrlResponse = {
    id: 42,
    url: "https://www.olx.pl/d/nieruchomosci/mieszkania/?search%5Bfilter_float_price%3Ato%5D=500000&page=1",
    name: "OLX Flats",
    isActive: true,
    lastCheckedAt: null,
    filters: null,
    showLocationMapInNotifications: false,
    sendMapInNotifications: true,
    waypoints: null,
    notificationFields: null,
  }

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
    mockMutate.mockClear()
  })

  const renderDialog = (url: ScrapingUrlResponse | null = sampleUrl, isOpen = true) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <EditUrlParamsDialog
          targetId={1}
          url={url}
          isOpen={isOpen}
          onClose={vi.fn()}
        />
      </QueryClientProvider>,
    )
  }

  it("displays locked base URL and parsed query parameters in compact rows", () => {
    renderDialog()

    expect(screen.getByText("https://www.olx.pl/d/nieruchomosci/mieszkania/")).toBeInTheDocument()
    const keyInputs = screen.getAllByLabelText("dashboard.monitoredWebsites.editParamsDialog.keyPlaceholder")
    const valueInputs = screen.getAllByLabelText("dashboard.monitoredWebsites.editParamsDialog.valuePlaceholder")

    expect(keyInputs).toHaveLength(2)
    expect(keyInputs[0]).toHaveValue("search[filter_float_price:to]")
    expect(valueInputs[0]).toHaveValue("500000")
    expect(keyInputs[1]).toHaveValue("page")
    expect(valueInputs[1]).toHaveValue("1")
  })

  it("disables save button when no changes have been made", () => {
    renderDialog()

    const saveButton = screen.getByRole("button", { name: "dashboard.monitoredWebsites.editParamsDialog.save" })
    expect(saveButton).toBeDisabled()
  })

  it("updates external open-search link and submits new URL preserving base URL", () => {
    renderDialog()

    const valueInputs = screen.getAllByLabelText("dashboard.monitoredWebsites.editParamsDialog.valuePlaceholder")
    fireEvent.change(valueInputs[0], { target: { value: "650000" } })

    const expectedUrl =
      "https://www.olx.pl/d/nieruchomosci/mieszkania/?search%5Bfilter_float_price%3Ato%5D=650000&page=1"

    const openLink = screen.getByRole("link", { name: "dashboard.monitoredWebsites.editParamsDialog.openSearch" })
    expect(openLink).toHaveAttribute("href", expectedUrl)
    expect(openLink).toHaveAttribute("target", "_blank")

    const saveButton = screen.getByRole("button", { name: "dashboard.monitoredWebsites.editParamsDialog.save" })
    expect(saveButton).toBeEnabled()
    fireEvent.click(saveButton)

    expect(mockMutate).toHaveBeenCalledTimes(1)
    expect(mockMutate).toHaveBeenCalledWith(
      { url: expectedUrl },
      expect.any(Object),
    )
  })

  it("allows empty parameter values as valid when key is non-empty", () => {
    renderDialog()

    const valueInputs = screen.getAllByLabelText("dashboard.monitoredWebsites.editParamsDialog.valuePlaceholder")
    fireEvent.change(valueInputs[1], { target: { value: "" } })

    expect(screen.queryByRole("alert")).not.toBeInTheDocument()
    const saveButton = screen.getByRole("button", { name: "dashboard.monitoredWebsites.editParamsDialog.save" })
    expect(saveButton).toBeEnabled()
    fireEvent.click(saveButton)

    expect(mockMutate).toHaveBeenCalledWith(
      {
        url: "https://www.olx.pl/d/nieruchomosci/mieszkania/?search%5Bfilter_float_price%3Ato%5D=500000&page=",
      },
      expect.any(Object),
    )
  })

  it("allows adding and removing query parameters", () => {
    renderDialog()

    fireEvent.click(screen.getByRole("button", { name: "dashboard.monitoredWebsites.editParamsDialog.addParam" }))
    const keyInputs = screen.getAllByLabelText("dashboard.monitoredWebsites.editParamsDialog.keyPlaceholder")
    const valueInputs = screen.getAllByLabelText("dashboard.monitoredWebsites.editParamsDialog.valuePlaceholder")
    expect(keyInputs).toHaveLength(3)

    fireEvent.change(keyInputs[2], { target: { value: "rooms" } })
    fireEvent.change(valueInputs[2], { target: { value: "3" } })

    const removeButtons = screen.getAllByRole("button", {
      name: "dashboard.monitoredWebsites.editParamsDialog.removeParam",
    })
    fireEvent.click(removeButtons[1])

    const saveButton = screen.getByRole("button", { name: "dashboard.monitoredWebsites.editParamsDialog.save" })
    fireEvent.click(saveButton)

    expect(mockMutate).toHaveBeenCalledWith(
      {
        url: "https://www.olx.pl/d/nieruchomosci/mieszkania/?search%5Bfilter_float_price%3Ato%5D=500000&rooms=3",
      },
      expect.any(Object),
    )
  })

  it("shows validation error and disables save when a key is empty", () => {
    renderDialog()

    fireEvent.click(screen.getByRole("button", { name: "dashboard.monitoredWebsites.editParamsDialog.addParam" }))

    expect(screen.getByRole("alert")).toHaveTextContent(
      "dashboard.monitoredWebsites.editParamsDialog.emptyKeyError",
    )
    const saveButton = screen.getByRole("button", { name: "dashboard.monitoredWebsites.editParamsDialog.save" })
    expect(saveButton).toBeDisabled()
  })

  it("keeps save disabled when URLSearchParams normalizes encoding without user edits", () => {
    renderDialog({
      ...sampleUrl,
      url: "https://www.olx.pl/d/nieruchomosci/mieszkania/?q=nowe%20mieszkanie",
    })

    const saveButton = screen.getByRole("button", { name: "dashboard.monitoredWebsites.editParamsDialog.save" })
    expect(saveButton).toBeDisabled()
  })

  it("shows validation error when resulting URL exceeds 1024 characters", () => {
    renderDialog()

    const valueInputs = screen.getAllByLabelText("dashboard.monitoredWebsites.editParamsDialog.valuePlaceholder")
    fireEvent.change(valueInputs[0], { target: { value: "x".repeat(1020) } })

    expect(screen.getByRole("alert")).toHaveTextContent(
      "dashboard.monitoredWebsites.editParamsDialog.urlTooLongError",
    )
    const saveButton = screen.getByRole("button", { name: "dashboard.monitoredWebsites.editParamsDialog.save" })
    expect(saveButton).toBeDisabled()
  })
})
