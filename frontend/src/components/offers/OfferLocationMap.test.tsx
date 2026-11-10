import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { OfferLocationMap, photonCache } from "./OfferLocationMap";
import plTranslations from "@/locales/pl/translation.json";

function getNestedTranslation(obj: Record<string, unknown>, path: string): string | undefined {
  return path.split(".").reduce<unknown>((acc, part) => {
    if (acc && typeof acc === "object" && part in acc) {
      return (acc as Record<string, unknown>)[part];
    }
    return undefined;
  }, obj) as string | undefined;
}

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string, options?: Record<string, unknown>) => {
      let val = getNestedTranslation(plTranslations as Record<string, unknown>, key) ?? key;
      if (typeof val === "string" && options) {
        Object.entries(options).forEach(([k, v]) => {
          val = val.replace(`{{${k}}}`, String(v));
        });
      }
      return val;
    },
  }),
}));

describe("OfferLocationMap", () => {
  beforeEach(() => {
    photonCache.clear();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    photonCache.clear();
  });

  it("renders no location fallback when location is null or empty", () => {
    render(<OfferLocationMap location={null} />);
    expect(screen.getByText("Brak podanej lokalizacji dla tej oferty")).toBeInTheDocument();
  });

  it("renders OpenStreetMap directly when GPS coordinates are provided (e.g. OLX)", async () => {
    render(
      <OfferLocationMap
        location={{
          name: "Warszawa, Mokotów",
          latitude: 52.2012,
          longitude: 21.0123,
          isExact: true,
        }}
      />
    );

    // Displays coordinates
    expect(
      screen.getByText("Współrzędne: 52.2012, 21.0123")
    ).toBeInTheDocument();

    // Badge shows exact GPS
    expect(screen.getByText("Dokładny punkt GPS")).toBeInTheDocument();

    // Zoom controls are visible
    expect(screen.getByLabelText("Przybliż mapę (szczegóły ulicy)")).toBeInTheDocument();
    expect(screen.getByLabelText("Oddal mapę (pokaż więcej okolicy)")).toBeInTheDocument();

    // Debounced iframe mounting
    await waitFor(() => {
      const iframe = screen.getByTitle("Lokalizacja na mapie");
      expect(iframe).toBeInTheDocument();
      expect(iframe).toHaveAttribute(
        "src",
        expect.stringContaining("openstreetmap.org/export/embed.html")
      );
      expect(iframe).toHaveAttribute(
        "src",
        expect.stringContaining("marker=52.2012%2C21.0123")
      );
      expect(iframe.getAttribute("srcdoc")).toContain("L.marker([52.2012, 21.0123])");
      expect(iframe.getAttribute("srcdoc")).not.toContain("L.circle");
    });
  });

  it("geocodes address via Photon when GPS coordinates are missing (e.g. Otodom) and displays ~300m circle", async () => {
    const mockPhotonResponse = {
      features: [
        {
          geometry: {
            coordinates: [21.005, 52.235] as [number, number], // [lon, lat]
          },
        },
      ],
    };

    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockPhotonResponse),
    } as Response);

    render(
      <OfferLocationMap
        location={{
          name: "Warszawa, ul. Marszałkowska",
          latitude: null,
          longitude: null,
          isExact: false,
        }}
      />
    );

    // Initial state before geocoding resolves
    expect(screen.getByText("Wyszukiwanie po ulicy / dzielnicy")).toBeInTheDocument();

    // Wait for geocoding to resolve and state to update
    await waitFor(() => {
      expect(
        screen.getByText("Współrzędne: 52.2350, 21.0050")
      ).toBeInTheDocument();
    });

    // Badge should indicate approximate ~300m area
    expect(screen.getByText("Obszar ~300m")).toBeInTheDocument();

    // Fetch was called with encoded query
    expect(fetchSpy).toHaveBeenCalledWith(
      "https://photon.komoot.io/api/?q=Warszawa%2C%20ul.%20Marsza%C5%82kowska&countrycode=pl&limit=1",
      expect.objectContaining({ signal: expect.any(AbortSignal) })
    );

    // Cached in photonCache
    expect(photonCache.get("Warszawa, ul. Marszałkowska")).toEqual({
      lat: 52.235,
      lon: 21.005,
    });

    // Embed URL updates to OpenStreetMap and srcdoc renders Leaflet circle of 300m
    await waitFor(() => {
      const iframe = screen.getByTitle("Lokalizacja na mapie");
      expect(iframe).toHaveAttribute(
        "src",
        expect.stringContaining("openstreetmap.org/export/embed.html")
      );
      expect(iframe).toHaveAttribute(
        "src",
        expect.stringContaining("marker=52.235%2C21.005")
      );
      expect(iframe.getAttribute("srcdoc")).toContain("radius: 300");
      expect(iframe.getAttribute("srcdoc")).toContain("L.circle([52.235, 21.005]");
    });
  });

  it("uses cached geocoded coordinates without re-fetching", () => {
    photonCache.set("Kraków, Stare Miasto", { lat: 50.0614, lon: 19.9366 });
    const fetchSpy = vi.spyOn(globalThis, "fetch");

    render(
      <OfferLocationMap
        location={{
          name: "Kraków, Stare Miasto",
          latitude: null,
          longitude: null,
          isExact: false,
        }}
      />
    );

    // Immediately shows coordinates from cache
    expect(
      screen.getByText("Współrzędne: 50.0614, 19.9366")
    ).toBeInTheDocument();

    // No network request made
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("falls back to Google Maps embed when Photon returns no results", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ features: [] }),
    } as Response);

    render(
      <OfferLocationMap
        location={{
          name: "Nieznana Ulica 999",
          latitude: null,
          longitude: null,
          isExact: false,
        }}
      />
    );

    await waitFor(() => {
      expect(photonCache.get("Nieznana Ulica 999")).toBeNull();
    });

    expect(screen.getByText("Wyszukiwanie po ulicy / dzielnicy")).toBeInTheDocument();

    await waitFor(() => {
      const iframe = screen.getByTitle("Lokalizacja na mapie");
      expect(iframe).toHaveAttribute(
        "src",
        expect.stringContaining("maps.google.com/maps?q=Nieznana%20Ulica%20999&output=embed")
      );
    });
  });

  it("falls back gracefully when Photon fetch errors", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new Error("Network timeout"));

    render(
      <OfferLocationMap
        location={{
          name: "Błąd Sieci",
          latitude: null,
          longitude: null,
          isExact: false,
        }}
      />
    );

    await waitFor(() => {
      expect(photonCache.get("Błąd Sieci")).toBeNull();
    });

    expect(screen.getByText("Wyszukiwanie po ulicy / dzielnicy")).toBeInTheDocument();

    await waitFor(() => {
      const iframe = screen.getByTitle("Lokalizacja na mapie");
      expect(iframe).toHaveAttribute(
        "src",
        expect.stringContaining("maps.google.com/maps?q=B%C5%82%C4%85d%20Sieci&output=embed")
      );
    });
  });

  it("allows switching zoom levels for OpenStreetMap", async () => {
    render(
      <OfferLocationMap
        location={{
          name: "Wrocław Rynek",
          latitude: 51.1079,
          longitude: 17.0385,
          isExact: false,
        }}
      />
    );

    await waitFor(() => {
      const iframe = screen.getByTitle("Lokalizacja na mapie");
      expect(iframe).toBeInTheDocument();
    });

    const zoomInBtn = screen.getByLabelText("Przybliż mapę (szczegóły ulicy)");
    expect(screen.getByText("Okolica")).toBeInTheDocument();

    // Zoom in from wide to medium
    act(() => {
      fireEvent.click(zoomInBtn);
    });
    expect(screen.getByText("Średni")).toBeInTheDocument();

    // Zoom in from medium to close
    act(() => {
      fireEvent.click(zoomInBtn);
    });
    expect(screen.getByText("Zbliżenie")).toBeInTheDocument();
    expect(zoomInBtn).toBeDisabled();

    // Zoom out back to medium
    const zoomOutBtn = screen.getByLabelText("Oddal mapę (pokaż więcej okolicy)");
    act(() => {
      fireEvent.click(zoomOutBtn);
    });
    expect(screen.getByText("Średni")).toBeInTheDocument();
  });

  it("renders ~300m circle when backend coordinates are imprecise (isExact: false)", async () => {
    render(
      <OfferLocationMap
        location={{
          name: "Gdańsk, Wrzeszcz",
          latitude: 54.3812,
          longitude: 18.6015,
          isExact: false,
        }}
        approximateRadiusMeters={300}
      />
    );

    expect(screen.getByText("Obszar ~300m")).toBeInTheDocument();

    await waitFor(() => {
      const iframe = screen.getByTitle("Lokalizacja na mapie");
      expect(iframe).toBeInTheDocument();
      expect(iframe.getAttribute("srcdoc")).toContain("radius: 300");
      expect(iframe.getAttribute("srcdoc")).toContain("L.circle([54.3812, 18.6015]");
      expect(iframe.getAttribute("srcdoc")).toContain("L.circleMarker([54.3812, 18.6015]");
    });
  });

  it("supports configurable approximate radius in meters", async () => {
    render(
      <OfferLocationMap
        location={{
          name: "Poznań, Jeżyce",
          latitude: 52.41,
          longitude: 16.905,
          isExact: false,
        }}
        approximateRadiusMeters={500}
      />
    );

    await waitFor(() => {
      const iframe = screen.getByTitle("Lokalizacja na mapie");
      expect(iframe.getAttribute("srcdoc")).toContain("radius: 500");
    });
  });
});
