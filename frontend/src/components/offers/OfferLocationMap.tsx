import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Check,
  Copy,
  ExternalLink,
  LocateFixed,
  MapPin,
  Navigation,
  Ruler,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import type {
  OfferLocationSchema,
  OfferWaypointSchema,
} from "@/lib/api/types.gen";
import { formatDistance, haversineKm } from "@/lib/geo";
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
  waypoints?: Array<OfferWaypointSchema> | null;
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
  waypoints: Array<OfferWaypointSchema> = [],
  fitWaypoints: boolean = false,
): string {
  const waypointsScript = waypoints
    .map(
      (wp) => `
      L.circleMarker([${wp.lat}, ${wp.lon}], {
        radius: 6,
        color: '#059669',
        fillColor: '#10b981',
        fillOpacity: 0.9,
        weight: 2
      }).addTo(map).bindTooltip(${JSON.stringify(wp.name)}, { permanent: true, direction: 'top', offset: [0, -6] });`,
    )
    .join("\n");

  const fitBoundsScript =
    fitWaypoints && waypoints.length > 0
      ? `map.fitBounds(${JSON.stringify([[lat, lon], ...waypoints.map((wp) => [wp.lat, wp.lon])])}, { padding: [28, 28] });`
      : "";

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
    ${waypointsScript}
    ${fitBoundsScript}
  </script>
</body>
</html>`;
}

export function OfferLocationMap({
  location,
  waypoints,
  interactiveMap = true,
  mapHeightClassName = "h-[260px] sm:h-[320px]",
  defaultZoom = "wide",
  approximateRadiusMeters = 300,
}: OfferLocationMapProps) {
  const { t } = useTranslation();
  const [zoomMode, setZoomMode] = useState<"wide" | "medium" | "close">(defaultZoom);
  const [fitWaypoints, setFitWaypoints] = useState(false);
  const [isMapActive, setIsMapActive] = useState(false);
  const [copiedCoords, setCopiedCoords] = useState(false);
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

  const effectiveCoords = useMemo(
    () =>
      hasCoords
        ? { lat: location.latitude as number, lon: location.longitude as number }
        : geocodedCoords,
    [hasCoords, location?.latitude, location?.longitude, geocodedCoords],
  );

  const isExactLocation = Boolean(hasCoords && location.isExact);
  const activeWaypoints = useMemo(() => waypoints ?? [], [waypoints]);

  const distances = useMemo(() => {
    if (!effectiveCoords || activeWaypoints.length === 0) {
      return [];
    }
    return activeWaypoints
      .map((wp) => {
        const km = haversineKm(
          effectiveCoords.lat,
          effectiveCoords.lon,
          wp.lat,
          wp.lon,
        );
        return {
          name: wp.name,
          km,
          formatted: `${isExactLocation ? "" : "~"}${formatDistance(km)}`,
        };
      })
      .sort((a, b) => a.km - b.km);
  }, [effectiveCoords, activeWaypoints, isExactLocation]);

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
        approximateRadiusMeters,
        activeWaypoints,
        fitWaypoints,
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
    setFitWaypoints(false);
    if (zoomMode === "close") setZoomMode("medium");
    else if (zoomMode === "medium") setZoomMode("wide");
  };

  const handleZoomIn = () => {
    setFitWaypoints(false);
    if (zoomMode === "wide") setZoomMode("medium");
    else if (zoomMode === "medium") setZoomMode("close");
  };

  const handleCopyCoords = () => {
    if (!effectiveCoords) return;
    const text = `${effectiveCoords.lat.toFixed(5)}, ${effectiveCoords.lon.toFixed(5)}`;
    navigator.clipboard.writeText(text).catch(() => {});
    setCopiedCoords(true);
    setTimeout(() => setCopiedCoords(false), 1500);
  };

  const zoomLabel =
    zoomMode === "wide"
      ? t("offers.map.zoomArea")
      : zoomMode === "medium"
        ? t("offers.map.zoomMedium")
        : t("offers.map.zoomClose");

  return (
    <div className="rounded-xl border border-border overflow-hidden bg-card">
      {/* Header Bar */}
      <div className="px-3 py-2 bg-muted/30 border-b border-border flex items-center justify-between gap-2 flex-wrap">
        <div className="flex items-center gap-2 min-w-0">
          <MapPin className="w-3.5 h-3.5 text-primary shrink-0" />
          <span className="text-xs font-semibold text-foreground truncate">
            {location.name || t("offers.map.defaultTitle")}
          </span>
          <Badge
            variant={isExactLocation ? "default" : "secondary"}
            className="text-[10px] uppercase tracking-wider font-medium"
          >
            {locationTypeBadge}
          </Badge>
        </div>

        <div className="flex items-center gap-1.5 shrink-0">
          {effectiveCoords && activeWaypoints.length > 0 && (
            <Button
              type="button"
              variant={fitWaypoints ? "default" : "outline"}
              size="sm"
              onClick={() => setFitWaypoints((prev) => !prev)}
              className="h-7 px-2 text-[11px] gap-1 cursor-pointer"
              title={t("offers.map.fitWaypoints")}
            >
              <LocateFixed className="w-3 h-3" />
              <span>{t("offers.map.fitWaypoints")}</span>
            </Button>
          )}

          {effectiveCoords && (
            <div className="flex items-center bg-muted/60 p-0.5 rounded-lg border border-border text-xs">
              <button
                type="button"
                onClick={handleZoomOut}
                disabled={!fitWaypoints && zoomMode === "wide"}
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
                disabled={!fitWaypoints && zoomMode === "close"}
                aria-label={t("offers.map.zoomIn")}
                className="p-1 rounded text-muted-foreground hover:text-foreground disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                title={t("offers.map.zoomIn")}
              >
                <ZoomIn className="w-3 h-3" />
              </button>
            </div>
          )}

          {mapUrl && (
            <Button
              asChild
              variant="ghost"
              size="sm"
              className="h-7 px-2 text-xs gap-1"
            >
              <a
                href={mapUrl}
                target="_blank"
                rel="noopener noreferrer"
                title={t("offers.map.openGoogleMaps")}
              >
                <Navigation className="w-3 h-3 text-primary" />
                <span>{t("offers.map.openGoogleMaps")}</span>
                <ExternalLink className="w-2.5 h-2.5 text-muted-foreground" />
              </a>
            </Button>
          )}
        </div>
      </div>

      {/* Map Viewport */}
      {interactiveMap && (
        embedUrl ? (
          <div
            className={`relative bg-muted/40 w-full group ${mapHeightClassName}`}
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
          <div className="flex flex-col items-center justify-center p-6 bg-muted/20 text-center gap-2">
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

      {/* Footer Bar: Waypoint Distances & Copyable Coordinates */}
      <div className="px-3 py-2.5 bg-muted/20 border-t border-border flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        {distances.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-x-4 gap-y-1 flex-1 min-w-0">
            {distances.map((d) => (
              <div
                key={d.name}
                title={
                  isExactLocation
                    ? undefined
                    : t("offers.map.distanceApproxTitle")
                }
                className="flex items-center gap-1.5 text-xs min-w-0"
              >
                <Ruler className="w-3 h-3 text-primary shrink-0" />
                <span className="font-mono font-semibold text-foreground shrink-0">
                  {d.formatted}
                </span>
                <span className="text-muted-foreground truncate">
                  → {d.name}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <span className="text-[11px] text-muted-foreground">
            {!effectiveCoords ? t("offers.map.streetSearch") : null}
          </span>
        )}

        {effectiveCoords && (
          <button
            type="button"
            onClick={handleCopyCoords}
            title={t("offers.map.copyCoordinates")}
            className={`inline-flex items-center gap-1.5 font-mono text-[11px] text-muted-foreground hover:text-foreground transition-colors cursor-pointer shrink-0 ${
              distances.length > 0
                ? "sm:border-l sm:border-border/70 sm:pl-3"
                : ""
            }`}
          >
            <span>
              {t("offers.map.coordinates", {
                lat: effectiveCoords.lat.toFixed(4),
                lng: effectiveCoords.lon.toFixed(4),
              })}
            </span>
            {copiedCoords ? (
              <Check className="w-3 h-3 text-emerald-500" />
            ) : (
              <Copy className="w-3 h-3 opacity-60" />
            )}
          </button>
        )}
      </div>
    </div>
  );
}
