import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { ExternalLink, MapPin, Navigation, ZoomIn, ZoomOut } from "lucide-react";
import type { OfferLocationSchema } from "@/lib/api/types.gen";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface PhotonFeature {
  geometry?: {
    coordinates?: [number, number];
  };
}

interface PhotonResponse {
  features?: Array<PhotonFeature>;
}

export const photonCache = new Map<string, { lat: number; lon: number } | null>();

interface OfferLocationMapProps {
  location?: OfferLocationSchema | null;
  interactiveMap?: boolean;
  mapHeightClassName?: string;
  defaultZoom?: "wide" | "medium" | "close";
  approximateRadiusMeters?: number;
}

export function buildOsmLeafletHtml(
  lat: number,
  lon: number,
  zoomLevel: number,
  isExact: boolean,
  radiusMeters: number = 300,
): string {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="referrer" content="strict-origin-when-cross-origin" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    html, body, #map { height: 100%; width: 100%; margin: 0; padding: 0; background: #f3f4f6; }
    .leaflet-control-attribution { font-size: 10px; background: rgba(255,255,255,0.7) !important; }
  </style>
</head>
<body>
  <div id="map"></div>
  <script>
    const map = L.map('map', { zoomControl: false }).setView([${lat}, ${lon}], ${zoomLevel});
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>'
    }).addTo(map);

    if (L.Icon && L.Icon.Default) {
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png'
      });
    }

    ${
      isExact
        ? `L.marker([${lat}, ${lon}]).addTo(map);`
        : `L.circle([${lat}, ${lon}], {
            color: '#4f46e5',
            fillColor: '#6366f1',
            fillOpacity: 0.22,
            weight: 2,
            radius: ${radiusMeters}
          }).addTo(map);
          L.circleMarker([${lat}, ${lon}], {
            radius: 4,
            color: '#4338ca',
            fillColor: '#ffffff',
            fillOpacity: 1,
            weight: 2
          }).addTo(map);`
    }
  </script>
</body>
</html>`;
}

export function OfferLocationMap({
  location,
  interactiveMap = true,
  mapHeightClassName = "h-[260px] sm:h-[320px]",
  defaultZoom = "wide",
  approximateRadiusMeters = 300,
}: OfferLocationMapProps) {
  const { t } = useTranslation();
  const [zoomMode, setZoomMode] = useState<"wide" | "medium" | "close">(defaultZoom);
  const [isMapActive, setIsMapActive] = useState(false);
  const [debouncedEmbedUrl, setDebouncedEmbedUrl] = useState<string | null>(null);
  const [debouncedSrcDoc, setDebouncedSrcDoc] = useState<string | null>(null);

  const hasCoords =
    location != null &&
    typeof location.latitude === "number" &&
    typeof location.longitude === "number";

  const [geocodedCoords, setGeocodedCoords] = useState<{ lat: number; lon: number } | null>(() => {
    if (!hasCoords && location?.name) {
      return photonCache.get(location.name) ?? null;
    }
    return null;
  });

  useEffect(() => {
    if (hasCoords || !location?.name) {
      setGeocodedCoords(null);
      return;
    }

    const query = location.name;
    const cached = photonCache.get(query);
    if (cached !== undefined) {
      setGeocodedCoords(cached);
      return;
    }

    setGeocodedCoords(null);
    const controller = new AbortController();

    fetch(`https://photon.komoot.io/api/?q=${encodeURIComponent(query)}&countrycode=pl&limit=1`, {
      signal: controller.signal,
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Photon API error: ${res.status}`);
        }
        return res.json() as Promise<PhotonResponse>;
      })
      .then((data) => {
        const feature = data.features?.[0];
        if (feature?.geometry?.coordinates) {
          const [lon, lat] = feature.geometry.coordinates;
          photonCache.set(query, { lat, lon });
          setGeocodedCoords({ lat, lon });
        } else {
          photonCache.set(query, null);
          setGeocodedCoords(null);
        }
      })
      .catch((_err: unknown) => {
        if (controller.signal.aborted) return;
        photonCache.set(query, null);
        setGeocodedCoords(null);
      });

    return () => {
      controller.abort();
    };
  }, [hasCoords, location?.name]);

  const effectiveCoords = hasCoords
    ? { lat: location.latitude as number, lon: location.longitude as number }
    : geocodedCoords;

  const isExactLocation = Boolean(hasCoords && location.isExact);

  const osmDelta =
    zoomMode === "wide"
      ? { lon: 0.024, lat: 0.016 }
      : zoomMode === "medium"
        ? { lon: 0.014, lat: 0.010 }
        : { lon: 0.007, lat: 0.005 };

  const zoomLevel = zoomMode === "wide" ? 14 : zoomMode === "medium" ? 15 : 16;

  const srcDoc = effectiveCoords
    ? buildOsmLeafletHtml(
        effectiveCoords.lat,
        effectiveCoords.lon,
        zoomLevel,
        isExactLocation,
        approximateRadiusMeters
      )
    : null;

  // Generate embed URL:
  // 1. When effective coordinates are present (backend or geocoded): use OpenStreetMap with marker and bounding box.
  // 2. When only street / city / location name is present and geocoding failed: use Google Maps search query embed.
  const embedUrl = effectiveCoords
    ? `https://www.openstreetmap.org/export/embed.html?bbox=${effectiveCoords.lon - osmDelta.lon}%2C${effectiveCoords.lat - osmDelta.lat}%2C${effectiveCoords.lon + osmDelta.lon}%2C${effectiveCoords.lat + osmDelta.lat}&layer=mapnik&marker=${effectiveCoords.lat}%2C${effectiveCoords.lon}`
    : location?.name
      ? `https://maps.google.com/maps?q=${encodeURIComponent(location.name)}&output=embed`
      : null;

  // Debounce iframe mounting to avoid lag and thrashing during rapid offer switching
  useEffect(() => {
    if (!embedUrl) {
      setDebouncedEmbedUrl(null);
      setDebouncedSrcDoc(null);
      return;
    }
    const timer = setTimeout(() => {
      setDebouncedEmbedUrl(embedUrl);
      setDebouncedSrcDoc(srcDoc);
    }, 250);
    return () => clearTimeout(timer);
  }, [embedUrl, srcDoc]);

  if (!location || (!location.name && !location.mapUrl && location.latitude == null)) {
    return (
      <div className="flex items-center gap-2 text-xs text-muted-foreground py-2 italic">
        <MapPin className="w-3.5 h-3.5 text-muted-foreground/50 shrink-0" />
        <span>{t("offers.map.noLocation")}</span>
      </div>
    );
  }

  const mapUrl =
    location.mapUrl ||
    (effectiveCoords
      ? `https://maps.google.com/?q=${effectiveCoords.lat},${effectiveCoords.lon}`
      : location.name
        ? `https://maps.google.com/?q=${encodeURIComponent(location.name)}`
        : undefined);

  const locationTypeBadge = isExactLocation
    ? t("offers.map.gpsPoint")
    : effectiveCoords
      ? t("offers.map.approximateRadius")
      : location.name?.toLowerCase().includes("ul.") || location.name?.includes(",")
        ? t("offers.map.streetArea")
        : t("offers.map.cityArea");

  const handleZoomOut = () => {
    if (zoomMode === "close") setZoomMode("medium");
    else if (zoomMode === "medium") setZoomMode("wide");
  };

  const handleZoomIn = () => {
    if (zoomMode === "wide") setZoomMode("medium");
    else if (zoomMode === "medium") setZoomMode("close");
  };

  const zoomLabel =
    zoomMode === "wide"
      ? t("offers.map.zoomArea")
      : zoomMode === "medium"
        ? t("offers.map.zoomMedium")
        : t("offers.map.zoomClose");

  return (
    <div className="space-y-2.5">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2 min-w-0">
          <MapPin className="w-4 h-4 text-primary shrink-0 mt-0.5" />
          <div className="min-w-0">
            <p className="text-sm font-semibold text-foreground leading-snug break-words">
              {location.name || t("offers.map.defaultTitle")}
            </p>
            {effectiveCoords ? (
              <p className="text-[11px] text-muted-foreground font-mono mt-0.5">
                {t("offers.map.coordinates", {
                  lat: effectiveCoords.lat.toFixed(4),
                  lng: effectiveCoords.lon.toFixed(4),
                })}
              </p>
            ) : (
              <p className="text-[11px] text-muted-foreground mt-0.5">
                {t("offers.map.streetSearch")}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1.5 shrink-0">
          {/* Zoom Level Switcher only when map has coordinates */}
          {effectiveCoords && (
            <div className="flex items-center bg-muted/60 p-0.5 rounded-lg border border-border text-xs">
              <button
                type="button"
                onClick={handleZoomOut}
                disabled={zoomMode === "wide"}
                aria-label={t("offers.map.zoomOut")}
                className="p-1 rounded text-muted-foreground hover:text-foreground disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                title={t("offers.map.zoomOut")}
              >
                <ZoomOut className="w-3 h-3" />
              </button>

              <span className="px-1.5 text-[10px] font-medium text-foreground select-none">
                {zoomLabel}
              </span>

              <button
                type="button"
                onClick={handleZoomIn}
                disabled={zoomMode === "close"}
                aria-label={t("offers.map.zoomIn")}
                className="p-1 rounded text-muted-foreground hover:text-foreground disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                title={t("offers.map.zoomIn")}
              >
                <ZoomIn className="w-3 h-3" />
              </button>
            </div>
          )}

          <Badge
            variant={isExactLocation ? "default" : "secondary"}
            className="text-[10px] uppercase tracking-wider font-medium"
          >
            {locationTypeBadge}
          </Badge>

          {mapUrl && (
            <Button
              asChild
              variant="outline"
              size="sm"
              className="h-7 px-2.5 text-xs gap-1"
            >
              <a
                href={mapUrl}
                target="_blank"
                rel="noopener noreferrer"
                title={t("offers.map.openGoogleMaps")}
              >
                <Navigation className="w-3 h-3 text-primary" />
                <span>{t("offers.map.openGoogleMaps")}</span>
                <ExternalLink className="w-2.5 h-2.5 ml-0.5 text-muted-foreground" />
              </a>
            </Button>
          )}
        </div>
      </div>

      {interactiveMap && (
        embedUrl ? (
          <div
            className={`relative rounded-xl overflow-hidden border border-border bg-muted/40 w-full shadow-inner group ${mapHeightClassName}`}
            onMouseLeave={() => setIsMapActive(false)}
          >
            {debouncedEmbedUrl ? (
              <iframe
                title={t("offers.detail.map")}
                src={debouncedEmbedUrl}
                srcDoc={debouncedSrcDoc ?? undefined}
                referrerPolicy="strict-origin-when-cross-origin"
                className={`w-full h-full border-0 transition-opacity ${
                  isMapActive ? "pointer-events-auto" : "pointer-events-none"
                }`}
                loading="lazy"
              />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center bg-muted/20 text-muted-foreground gap-2 animate-pulse">
                <MapPin className="w-5 h-5 text-primary/40" />
                <span className="text-xs text-muted-foreground/70">
                  {t("offers.map.loadingMap")}
                </span>
              </div>
            )}

            {debouncedEmbedUrl && !isMapActive && (
              <button
                type="button"
                onClick={() => setIsMapActive(true)}
                className="absolute inset-0 w-full h-full bg-transparent hover:bg-black/5 flex items-end justify-center pb-3 cursor-pointer transition-colors"
                title={t("offers.map.clickToInteract")}
                aria-label={t("offers.map.clickToInteract")}
              >
                <span className="px-3 py-1 rounded-full bg-background/95 text-foreground text-xs font-medium shadow-md border border-border backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity">
                  {t("offers.map.clickToInteract")}
                </span>
              </button>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-6 rounded-xl border border-dashed border-border/80 bg-muted/20 text-center gap-2">
            <MapPin className="w-6 h-6 text-muted-foreground/60" />
            <p className="text-xs text-muted-foreground max-w-sm">
              {t("offers.map.noGpsNotice")}
            </p>
            {mapUrl && (
              <Button asChild variant="outline" size="sm" className="mt-1 h-7 text-xs gap-1">
                <a href={mapUrl} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-3 h-3 mr-1" />
                  <span>{t("offers.map.openGoogleMaps")}</span>
                </a>
              </Button>
            )}
          </div>
        )
      )}
    </div>
  );
}
