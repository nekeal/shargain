import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, renderHook, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { OffersPage } from "./OffersPage";
import { useOfferKeyboardTriage } from "./useOfferKeyboardTriage";
import type { PublicOfferSchema, TargetSummaryResponse } from "@/lib/api/types.gen";
import * as api from "@/lib/api/sdk.gen";
import plTranslations from "@/locales/pl/translation.json";

vi.mock("@/lib/api/sdk.gen", () => ({
  getTargetOffers: vi.fn(),
  likeOffer: vi.fn(),
  unlikeOffer: vi.fn(),
  markOfferSeen: vi.fn(),
  markOfferUnseen: vi.fn(),
  listTargets: vi.fn(),
  getMyTarget: vi.fn(),
}));

function getNestedTranslation(obj: any, path: string): string | undefined {
  return path.split(".").reduce((acc, part) => acc && acc[part], obj);
}

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string, options?: Record<string, unknown>) => {
      let val = getNestedTranslation(plTranslations, key) ?? key;
      if (typeof val === "string" && options) {
        Object.entries(options).forEach(([k, v]) => {
          val = (val).replace(`{{${k}}}`, String(v));
        });
      }
      return val;
    },
  }),
}));

const mockTargets: Array<TargetSummaryResponse> = [
  { id: 1, name: "Mieszkania Warszawa", isActive: true, enableNotifications: true, urlCount: 3 },
  { id: 2, name: "Działki Mazury", isActive: false, enableNotifications: false, urlCount: 1 },
];

const mockOffer1: PublicOfferSchema = {
  id: 1,
  title: "Mieszkanie 2-pokojowe Mokotów",
  url: "https://www.otodom.pl/pl/oferta/test-1",
  listUrl: "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie",
  price: 650000,
  mainImageUrl: "https://example.com/img1.jpg",
  images: ["https://example.com/img1.jpg"],
  createdAt: "2026-11-10T10:00:00.000Z",
  publishedAt: "2026-11-10T09:30:00.000Z",
  closedAt: null,
  isSeen: false,
  seenAt: null,
  isLiked: false,
  likedAt: null,
  scrapingUrlName: "Otodom Mokotów",
  description: "Piękne mieszkanie w świetnej lokalizacji.",
  location: {
    name: "Warszawa, Mokotów",
    mapUrl: "https://maps.google.com/?q=Warszawa",
    latitude: 52.2,
    longitude: 21.0,
    isExact: true,
  },
  attributes: [
    { name: "area", label: "Powierzchnia", type: "number", unit: "m²", value: 50, display: "50 m²" },
  ],
};

const mockOffer2: PublicOfferSchema = {
  id: 2,
  title: "Kawalerka Śródmieście",
  url: "https://www.otodom.pl/pl/oferta/test-2",
  listUrl: "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie",
  price: 450000,
  mainImageUrl: null,
  images: [],
  createdAt: "2026-11-10T11:00:00.000Z",
  publishedAt: "2026-11-10T10:30:00.000Z",
  closedAt: null,
  isSeen: true,
  seenAt: "2026-11-10T11:15:00.000Z",
  isLiked: true,
  likedAt: "2026-11-10T11:15:00.000Z",
  scrapingUrlName: "Otodom Śródmieście",
  description: "Kawalerka po remoncie.",
  location: {
    name: "Warszawa, Śródmieście",
    mapUrl: null,
    latitude: null,
    longitude: null,
    isExact: false,
  },
  attributes: [],
};

describe("OffersPage", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    Element.prototype.scrollIntoView = vi.fn();

    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    vi.mocked(api.listTargets).mockResolvedValue({
      data: mockTargets,
    } as any);

    vi.mocked(api.getTargetOffers).mockResolvedValue({
      data: {
        count: 2,
        items: [mockOffer1, mockOffer2],
      },
    } as any);
  });

  const renderWithProviders = (ui: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {ui}
      </QueryClientProvider>
    );
  };

  it("renders live offers from getTargetOffers and does not display prototype elements", async () => {
    renderWithProviders(<OffersPage initialTargetId={1} />);

    await waitFor(() => {
      expect(screen.getAllByText("Mieszkanie 2-pokojowe Mokotów").length).toBeGreaterThan(0);
    });

    expect(screen.getByText("Kawalerka Śródmieście")).toBeInTheDocument();

    // Verify prototype scaffolding is NOT rendered
    expect(screen.queryByText(/Tryb prototypu/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Przełącz na Live API/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Przełącz na Sample Data/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Card Gallery/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Analyst Table/i)).not.toBeInTheDocument();
  });

  it("switches tabs to filter unseen, liked, or all offers", async () => {
    renderWithProviders(<OffersPage initialTargetId={1} />);

    await waitFor(() => {
      expect(screen.getAllByText("Mieszkanie 2-pokojowe Mokotów").length).toBeGreaterThan(0);
    });

    // Default tab is unseen
    expect(api.getTargetOffers).toHaveBeenCalledWith(
      expect.objectContaining({
        path: { target_id: 1 },
        query: expect.objectContaining({ seen: false, liked: undefined }),
      }),
    );

    // Click 'Polubione' tab
    const likedTab = screen.getByRole("tab", { name: /Polubione/i });
    fireEvent.pointerDown(likedTab, { button: 0, ctrlKey: false });
    fireEvent.keyDown(likedTab, { key: "Enter" });

    await waitFor(() => {
      expect(api.getTargetOffers).toHaveBeenCalledWith(
        expect.objectContaining({
          path: { target_id: 1 },
          query: expect.objectContaining({ liked: true }),
        }),
      );
    });

    // Click 'Wszystkie' tab
    const allTab = screen.getByRole("tab", { name: /Wszystkie/i });
    fireEvent.pointerDown(allTab, { button: 0, ctrlKey: false });
    fireEvent.keyDown(allTab, { key: "Enter" });

    await waitFor(() => {
      expect(api.getTargetOffers).toHaveBeenCalledWith(
        expect.objectContaining({
          path: { target_id: 1 },
          query: expect.objectContaining({ seen: undefined, liked: undefined }),
        }),
      );
    });
  });

  it("toggles ordering between oldest and newest", async () => {
    renderWithProviders(<OffersPage initialTargetId={1} />);

    await waitFor(() => {
      expect(screen.getAllByText("Mieszkanie 2-pokojowe Mokotów").length).toBeGreaterThan(0);
    });

    const orderingBtn = screen.getByRole("button", { name: /Kolejność:/i });
    expect(orderingBtn).toHaveTextContent("Najstarsze (kolejka)");

    fireEvent.click(orderingBtn);

    await waitFor(() => {
      expect(orderingBtn).toHaveTextContent("Najnowsze");
      expect(api.getTargetOffers).toHaveBeenCalledWith(
        expect.objectContaining({
          path: { target_id: 1 },
          query: expect.objectContaining({ ordering: "newest" }),
        }),
      );
    });
  });

  it("allows selecting target when multiple targets exist and notifies onTargetChange", async () => {
    const onTargetChange = vi.fn();
    renderWithProviders(
      <OffersPage initialTargetId={1} onTargetChange={onTargetChange} />,
    );

    await waitFor(() => {
      expect(screen.getAllByText("Mieszkanie 2-pokojowe Mokotów").length).toBeGreaterThan(0);
    });

    const selectTrigger = screen.getByRole("combobox", { name: "Wybierz cel" });
    expect(selectTrigger).toBeInTheDocument();

    fireEvent.click(selectTrigger);

    await waitFor(() => {
      expect(screen.getByText("Działki Mazury")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Działki Mazury"));

    expect(onTargetChange).toHaveBeenCalledWith(2);

    await waitFor(() => {
      expect(api.getTargetOffers).toHaveBeenCalledWith(
        expect.objectContaining({
          path: { target_id: 2 },
        }),
      );
    });
  });

  it("refetches offers when clicking refresh button", async () => {
    renderWithProviders(<OffersPage initialTargetId={1} />);

    await waitFor(() => {
      expect(screen.getAllByText("Mieszkanie 2-pokojowe Mokotów").length).toBeGreaterThan(0);
    });

    const initialCallCount = vi.mocked(api.getTargetOffers).mock.calls.length;

    const refreshBtn = screen.getByTitle("Odśwież listę z serwera");
    fireEvent.click(refreshBtn);

    await waitFor(() => {
      expect(vi.mocked(api.getTargetOffers).mock.calls.length).toBeGreaterThan(initialCallCount);
    });
  });

  it("triggers like and seen mutations when user interacts with an offer", async () => {
    vi.mocked(api.likeOffer).mockResolvedValue({
      data: { ...mockOffer1, isLiked: true },
    } as any);

    vi.mocked(api.markOfferSeen).mockResolvedValue({
      data: { ...mockOffer1, isSeen: true },
    } as any);

    renderWithProviders(<OffersPage initialTargetId={1} />);

    await waitFor(() => {
      expect(screen.getAllByText("Mieszkanie 2-pokojowe Mokotów").length).toBeGreaterThan(0);
    });

    // Toggle seen on the active offer (mockOffer1 is initially unseen)
    const markSeenBtn = screen.getByRole("button", { name: /Oznacz przeczytane/i });
    fireEvent.click(markSeenBtn);

    await waitFor(() => {
      expect(api.markOfferSeen).toHaveBeenCalledWith(
        expect.objectContaining({
          path: { target_id: 1, offer_id: 1 },
        }),
      );
    });

    // Toggle like on the active offer (mockOffer1 is initially not liked)
    const likeBtn = screen.getByRole("button", { name: "Polub (L)" });
    fireEvent.click(likeBtn);

    await waitFor(() => {
      expect(api.likeOffer).toHaveBeenCalledWith(
        expect.objectContaining({
          path: { target_id: 1, offer_id: 1 },
        }),
      );
    });
  });

  it("presses J shortcut to advance to next offer", async () => {
    vi.mocked(api.markOfferSeen).mockResolvedValue({
      data: { ...mockOffer1, isSeen: true },
    } as any);

    renderWithProviders(<OffersPage initialTargetId={1} />);

    await waitFor(() => {
      expect(screen.getAllByText("Mieszkanie 2-pokojowe Mokotów").length).toBeGreaterThan(0);
    });

    // Press 'J' key
    fireEvent.keyDown(window, { key: "j" });

    // Should advance selection to next offer without calling markOfferSeen
    await waitFor(() => {
      expect(screen.getAllByText("Kawalerka Śródmieście").length).toBeGreaterThan(0);
    });

    expect(api.markOfferSeen).not.toHaveBeenCalled();
  });

  it("auto-marks offer as seen after 1 second only when details panel is open", async () => {
    vi.mocked(api.markOfferSeen).mockResolvedValue({
      data: { ...mockOffer1, isSeen: true },
    } as any);

    renderWithProviders(<OffersPage initialTargetId={1} />);

    await waitFor(() => {
      expect(screen.getAllByText("Mieszkanie 2-pokojowe Mokotów").length).toBeGreaterThan(0);
    });

      await waitFor(
        () => {
          expect(api.markOfferSeen).toHaveBeenCalledWith(
            expect.objectContaining({
              path: { target_id: 1, offer_id: 1 },
            }),
          );
        },
        { timeout: 2000 },
      );
    });

    it("does not auto-mark offer as seen when details panel is closed", async () => {
      vi.mocked(api.markOfferSeen).mockResolvedValue({
        data: { ...mockOffer1, isSeen: true },
      } as any);

      renderWithProviders(<OffersPage initialTargetId={1} />);

      await waitFor(() => {
        expect(screen.getAllByText("Mieszkanie 2-pokojowe Mokotów").length).toBeGreaterThan(0);
      });

      // Collapse details panel by clicking "Zwiń szczegóły"
      const hideDetailsBtn = screen.getAllByTitle("Zwiń szczegóły")[0];
      fireEvent.click(hideDetailsBtn);

      // Wait 1.2s
      await new Promise((resolve) => setTimeout(resolve, 1200));

      expect(api.markOfferSeen).not.toHaveBeenCalled();
    });

  it("supports pagination by loading more offers when total count exceeds loaded items", async () => {
    vi.mocked(api.getTargetOffers).mockResolvedValue({
      data: {
        count: 55,
        items: [mockOffer1, mockOffer2],
      },
    } as any);

    renderWithProviders(<OffersPage initialTargetId={1} />);

    await waitFor(() => {
      expect(screen.getAllByText("Mieszkanie 2-pokojowe Mokotów").length).toBeGreaterThan(0);
    });

    // Results counter shows total: "2 z 55"
    expect(screen.getByText(/2 z 55/i)).toBeInTheDocument();

    // "Załaduj więcej" button should be present
    const loadMoreBtn = screen.getByRole("button", { name: /Załaduj więcej/i });
    expect(loadMoreBtn).toBeInTheDocument();

    fireEvent.click(loadMoreBtn);

    await waitFor(() => {
      expect(api.getTargetOffers).toHaveBeenCalledWith(
        expect.objectContaining({
          path: { target_id: 1 },
          query: expect.objectContaining({ limit: 100 }),
        }),
      );
    });
  });

  it("useOfferKeyboardTriage handles empty offers list without throwing", () => {
    const { result } = renderHook(() =>
      useOfferKeyboardTriage({
        offers: [],
        selectedOfferId: 0,
        setSelectedOfferId: vi.fn(),
        isDetailsOpen: true,
        onToggleLike: vi.fn(),
        onToggleSeen: vi.fn(),
      }),
    );
    expect(result.current.activeOffer).toBeUndefined();
    expect(result.current.activeIndex).toBe(0);
  });
});
