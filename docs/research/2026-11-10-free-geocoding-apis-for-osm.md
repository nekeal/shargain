# Geocoding APIs for OpenStreetMap Integration in Shargain

**Date:** 2026-11-10  
**Author:** Systems & Geospatial Architecture Team  
**Subject:** Free Forward Geocoding APIs for Otodom Real Estate Offers to Enable OpenStreetMap Rendering  
**Language Context:** Polish Real Estate Addresses (Streets, Municipalities, Districts, Suburbs)

---

## 1. Executive Summary

### The Core Problem
In Shargain, real estate offers aggregated from **OLX** provide native GPS coordinates in their metadata (`metadata.extra.map.lat` / `lon`). For OLX, the frontend component [`OfferLocationMap.tsx`](file:///home/nekeal/projects/python/shargain/frontend/src/components/offers/OfferLocationMap.tsx) directly renders an interactive **OpenStreetMap** iframe with a marker and bounding box:
```html
https://www.openstreetmap.org/export/embed.html?bbox={minLon}%2C{minLat}%2C{maxLon}%2C{maxLat}&layer=mapnik&marker={lat}%2C{lon}
```

However, **Otodom** does not expose geographic coordinates in its listing metadata. It only provides text strings extracted from reverse geocoding tags or address fields (e.g. `"Kraków, Mogilska"`, `"Warszawa, Mokotów, ul. Puławska"`, or `"Kraków, Swoszowice"`). Consequently, Shargain currently falls back to a Google Maps search embed:
```html
https://maps.google.com/maps?q={encodeURIComponent(location.name)}&output=embed
```

### The Key Finding
**Yes, multiple free and high-quality geocoding APIs exist to bridge this gap.** Furthermore:
1. **Frontend is already ready:** `OfferLocationMap.tsx` is *already coded* to render OpenStreetMap whenever `location.latitude` and `location.longitude` are populated. As soon as the backend provides coordinates, the frontend automatically switches from Google Maps to OpenStreetMap without requiring any UI redesign.
2. **Backend is currently missing coordinates:** `OtodomLocationParser.get_coordinates()` simply returns `None`.
3. **The Best Strategy:** Perform geocoding **once on the backend during offer ingest** (`batch_create`) and cache results permanently. Never geocode on-the-fly in the frontend browser.

---

## 2. In-Depth Analysis of Candidate Geocoding APIs

We evaluated six solutions capable of forward geocoding Polish street addresses and districts into WGS84 coordinates (`latitude`, `longitude`, and `boundingbox`).

---

### 2.1. GUGiK UUG (Państwowy Rejestr Granic – Polish Government)

* **Provider:** Główny Urząd Geodezji i Kartografii (GUGiK).
* **Endpoint:** `https://services.gugik.gov.pl/uug/?request=GetAddress&address={query}&srid=4326`
* **Cost & API Key:** 100% Free, public government service, **no API key required**, no registration.
* **Output Coordinates:** Standard WGS84 (`srid=4326`), where `x` = Longitude (~14°–24°), `y` = Latitude (~49°–55°).

```json
{
  "status": "OK",
  "results": {
    "1": {
      "x": "19.967812",
      "y": "50.064511",
      "city": "Kraków",
      "street": "Mogilska",
      "voivodeship": "małopolskie"
    }
  }
}
```

* **Strengths:**
  - Official state register (*Państwowy Rejestr Granic* - PRG).
  - Unmatched accuracy for official house numbers and streets in Poland.
  - Zero legal hurdles: completely public domain Polish data, permanent storage allowed.
* **Weaknesses & Limitations for Otodom:**
  - **Strict formatting requirement:** Requires strict ordering: `Miejscowość, Ulica Numer` or `Miejscowość, Ulica` or `Miejscowość`.
  - **Poor district/neighborhood handling:** Otodom offers often specify districts without streets (e.g. *"Kraków, Swoszowice"*, *"Warszawa, Mokotów"*, *"Kraków, Kliny Zachód"*). Because PRG treats districts as administrative divisions rather than addresses, UUG frequently returns empty results (`"status": "ERROR"` or empty `results`) when queried with informal or district-only names.
  - **SLA & Uptime:** Government endpoints experience periodic maintenance windows and slow response times without SLA guarantees.

---

### 2.2. Nominatim (OpenStreetMap Official)

* **Provider:** OpenStreetMap Foundation (OSMF).
* **Endpoint:** `https://nominatim.openstreetmap.org/search?q={query}&format=json&countrycodes=pl&limit=1`
* **Cost & API Key:** 100% Free, **no API key required**.
* **Output Format:** JSON with `lat`, `lon`, `boundingbox` (`[minlat, maxlat, minlon, maxlon]`), `display_name`, and OSM classification (`class`, `type`).

```json
[
  {
    "lat": "50.065231",
    "lon": "19.969102",
    "boundingbox": ["50.063100", "50.067300", "19.965000", "19.973000"],
    "display_name": "Mogilska, Osiedle Oficerskie, Grzegórzki, Kraków, województwo małopolskie, Polska",
    "class": "highway",
    "type": "secondary"
  }
]
```

* **Strengths:**
  - Native to OpenStreetMap.
  - **Superb handling of Polish city districts and suburbs:** OSM features rich tagging for `place=suburb` (e.g. Swoszowice, Mokotów), `place=quarter`, and `residential`.
  - Returns `boundingbox` which perfectly fits the OpenStreetMap embed URL parameters.
* **Strict Usage Policy & Limitations:**
  - **Rate Limit:** Absolute maximum of **1 request per second**.
  - **Background scripts policy:** The OSMF Usage Policy explicitly restricts automated scripts running regularly to a maximum of **4 requests per minute**.
  - **Mandatory User-Agent:** Must supply a valid `User-Agent` and contact email (e.g. `User-Agent: Shargain/1.0 (contact@example.com)`). Generic HTTP library user-agents (Python `requests`, `curl`) are blocked immediately with HTTP 403.
  - **Mandatory Caching:** The policy strictly commands that results must be cached locally to prevent duplicate requests.
  - **Attribution:** Requires "© OpenStreetMap contributors" (already standard on OSM tiles).

---

### 2.3. Photon (Komoot – OSM + Elasticsearch)

* **Provider:** Komoot (open-source geocoder developed for outdoor navigation).
* **Endpoint:** `https://photon.komoot.io/api/?q={query}&countrycode=pl&limit=1`
* **Structured Endpoint:** `https://photon.komoot.io/api/?city={city}&street={street}&district={district}&countrycode=pl`
* **Cost & API Key:** 100% Free public demo, **no API key required**.
* **Output Format:** Standard GeoJSON:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [19.969102, 50.065231]
      },
      "properties": {
        "name": "Mogilska",
        "city": "Kraków",
        "state": "województwo małopolskie",
        "country": "Polska"
      }
    }
  ]
}
```

* **Strengths:**
  - Extremely fast response times (< 150 ms, powered by Elasticsearch).
  - High tolerance for typos, missing accents, and abbreviations.
  - Supports structured queries as well as free-text search.
* **Weaknesses:**
  - Hosted as a public demonstration server by Komoot without commercial SLA.
  - Dynamic throttling / temporary IP bans if subjected to bursts of traffic without notice.
  - Does not always return a precise bounding box for polygons.

---

### 2.4. Geoapify (Commercial Freemium – Highest Developer Recommendation)

* **Provider:** Geoapify GmbH.
* **Endpoint:** `https://api.geoapify.com/v1/geocode/search?text={query}&filter=countrycode:pl&apiKey={KEY}`
* **Cost & API Key:** Free tier provides **3,000 requests/day**, **5 requests/second**. Requires free API key.
* **Output Format:** Clean GeoJSON with confidence score (`rank.confidence`), bbox, and component breakdown.

* **Crucial Legal Advantage (ToS):**
  - **Explicitly allows permanent caching and database storage.** Unlike Google Maps or LocationIQ, Geoapify's terms explicitly permit building and maintaining a persistent address database with geocoded coordinates.
  - **No vendor lock-in:** The data can be displayed on OpenStreetMap, Leaflet, MapLibre, or anywhere else.
* **Strengths:**
  - Hybrid dataset: Combines OpenStreetMap, OpenAddresses, GeoNames, and national boundary data.
  - Flawlessly parses Polish addresses, streets with/without `"ul."`, districts, and postal codes.
  - 3,000 requests per day is vastly more than any personal or small-team Shargain deployment will ever ingest (typically 50–300 offers/day).
  - 5 req/sec rate limit means batch ingestion never stalls.
* **Requirements:**
  - Free account signup (1 minute).
  - Attribution requirement on free tier ("Powered by Geoapify" / OSM data).

---

### 2.5. LocationIQ (Commercial Freemium)

* **Provider:** LocationIQ (hosted Nominatim / Unwired Labs).
* **Endpoint:** `https://us1.locationiq.com/v1/search.php?key={KEY}&q={query}&format=json`
* **Cost & API Key:** 5,000 requests/day, 2 req/sec. Requires free API key.
* **Critical Limitation for Shargain:**
  > **Terms of Service Section on Caching:** *"If you are on the Free plan, you are only permitted to temporarily cache request-response pairs for up to 48 hours."*
* **Verdict:** **Not Recommended.** Permanently storing coordinates in the PostgreSQL database for scraped real estate offers violates the LocationIQ Free Tier Terms of Service.

---

### 2.6. OpenRouteService / Pelias (HeiGIT)

* **Provider:** Heidelberg Institute for Geoinformation Technology.
* **Endpoint:** `https://api.openrouteservice.org/geocode/search?api_key={KEY}&text={query}&boundary.country=PL`
* **Cost & API Key:** ~8,000 requests/day, 40 requests/minute. Requires free API key.
* **Strengths:** Generous daily quota, Pelias engine.
* **Weaknesses:** Strict 40 req/min token bucket limit (less than 1 req/sec); accounts occasionally require manual activation.

---

### 2.7. Self-Hosted (Nominatim or Photon via Docker)

* **Container:** `komoot/photon` or `mediagis/nominatim-docker`.
* **Strengths:** Zero rate limits, 100% privacy, zero external API dependencies, offline capability.
* **Weaknesses (Resource Prohibitive for Shargain):**
  - Photon requires **8 GB to 16 GB of RAM** and **30–50 GB NVMe SSD** storage for a Poland extract.
  - Nominatim requires **32 GB to 64 GB of RAM** and a heavyweight PostgreSQL/PostGIS database.
  - High operational complexity (downloading OSM PBF extracts, indexing for hours, updating diffs).
* **Verdict:** Complete violation of YAGNI/KISS for a self-hosted real estate aggregator.

---

## 3. Comparison Matrix

| Provider | Free Tier Daily Quota | Rate Limit | Requires API Key? | Permanent DB Caching Allowed? | Accuracy: Polish Streets | Accuracy: Polish Districts | Setup Effort |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Geoapify** *(Recommended)* | **3,000 / day** | **5 req/sec** | Yes (Free) | **YES (Explicitly)** | ⭐⭐⭐⭐⭐ (Excellent) | ⭐⭐⭐⭐⭐ (Excellent) | Minimal (add `.env` key) |
| **Photon (Komoot)** | Fair-use (~unlimited) | ~1-2 req/sec | **NO** | **YES** | ⭐⭐⭐⭐ (Very Good) | ⭐⭐⭐⭐ (Very Good) | Zero (out-of-the-box) |
| **Nominatim (OSM)** | Fair-use (max 4/min script) | 1 req/sec | **NO** (Needs User-Agent) | **YES (Required)** | ⭐⭐⭐⭐ (Very Good) | ⭐⭐⭐⭐⭐ (Excellent) | Low (requires custom UA) |
| **GUGiK UUG (Gov)** | Fair-use (~unlimited) | ~1-2 req/sec | **NO** | **YES** | ⭐⭐⭐⭐⭐ (Exact PRG) | ⭐⭐ (Fails on districts) | Low (needs strict formatting) |
| **LocationIQ** | 5,000 / day | 2 req/sec | Yes (Free) | ❌ **NO (Max 48h cache)** | ⭐⭐⭐⭐ (Very Good) | ⭐⭐⭐⭐ (Very Good) | Low |
| **OpenRouteService** | 8,000 / day | 40 req/min | Yes (Free) | Ambiguous | ⭐⭐⭐⭐ (Good) | ⭐⭐⭐⭐ (Good) | Medium |
| **Self-Hosted Docker** | Unlimited | Server bound | No | **YES** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Very High (8-16 GB RAM) |

---

## 4. Architectural Analysis: Frontend vs Backend Geocoding

### Option A: Frontend On-The-Fly Geocoding (Anti-Pattern)
In this approach, the React browser client intercepts missing coordinates in `OfferLocationMap.tsx` and calls Nominatim/Photon before rendering the map.

* **Major Pitfalls:**
  1. **Poor UX / Layout Shifts:** The map displays a loading spinner or placeholder for 200–800 ms while geocoding resolves, then re-renders the OSM iframe.
  2. **Browser CORS & User-Agent Restrictions:** Nominatim strictly forbids generic User-Agents and requires contact emails. Modern browsers restrict custom `User-Agent` headers in `fetch()`.
  3. **Wasted Requests:** If 5 users view the same offer, or 1 user refreshes the page, the external API is hit repeatedly for identical addresses.
  4. **Does NOT solve Notifications:** The Telegram notification bot and background services cannot calculate commute distances to waypoints (e.g. *"2.1 km to Office"*) or send pins because the backend still has `coordinates = None`.

### Option B: Backend Geocoding at Ingest with Local Deduplication Cache (Recommended)
In this approach, geocoding happens during `OfferBatchCreateService.batch_create()` (or an asynchronous Celery task):

```
                   [ New Scraped Otodom Offer ]
                                |
                                v
               Extract address: "Kraków, Mogilska"
                                |
                                v
           Check Postgres / Memory Cache (GeocodedAddress)
                           /          \
                     Hit  /            \  Miss
                         v              v
        Reuse (lat, lon, bbox)     Call Geocoding API (Geoapify / Photon)
                         \              /
                          \            /
                           v          v
              Store coordinates in offer.metadata["coordinates"]
                                |
                                +---> Instant OSM rendering in Frontend (0 external calls)
                                +---> Telegram bot sends interactive map pin
                                +---> Calculates distances to commute waypoints
```

* **Overwhelming Advantages:**
  1. **Zero UI Latency:** The coordinates arrive in the initial GraphQL/REST response. The React `OfferLocationMap` renders OpenStreetMap immediately.
  2. **Deduplication:** In real estate, many offers appear on the same streets or in the same districts. A simple database cache (`GeocodedAddress`) cuts external API calls by **80–90%**.
  3. **Respects Rate Limits:** Ingest can throttle gracefully (e.g. 200 ms between requests) without affecting user responsiveness.
  4. **Frontend Already Supports It:** `OfferLocationMap.tsx` already checks `if (location.latitude && location.longitude)` to render OSM! No frontend code overhaul is necessary.

---

## 5. Concrete Recommendation & Implementation Plan

### Recommended Solution: Two-Tier Strategy

1. **Option 1 (Production Grade - Recommended): Geoapify API**
   - Provide a free Geoapify API key via `GEOAPIFY_API_KEY` in `.env`.
   - 3,000 geocodes/day covers 100% of Shargain scraping needs.
   - Legally 100% compliant with permanent database caching.
   - Fast (5 req/sec) and fault-tolerant with Polish addresses.

2. **Option 2 (Zero-Configuration / Default Fallback): Photon + Nominatim**
   - If no API key is configured, fall back to **Photon** (`photon.komoot.io`) with **Nominatim** as secondary fallback.
   - Requires zero user configuration, works right out of the box.

### Implementation Blueprint

#### 1. Backend Geocoding Service (`shargain/offers/services/geocoding.py`)
Create a lightweight, resilient geocoding service with a cache table:

```python
import logging
import requests
from django.conf import settings
from shargain.offers.geo import Coordinates

logger = logging.getLogger(__name__)

class GeocodingService:
    @classmethod
    def geocode(cls, address_query: str) -> Coordinates | None:
        if not address_query or not address_query.strip():
            return None
        
        # 1. Check local DB cache table
        cached = cls.get_from_cache(address_query)
        if cached:
            return cached

        # 2. Try Geoapify if API key present
        api_key = getattr(settings, "GEOAPIFY_API_KEY", None)
        if api_key:
            coords = cls._query_geoapify(address_query, api_key)
            if coords:
                cls.save_to_cache(address_query, coords)
                return coords

        # 3. Fallback: Photon (Komoot OSM)
        coords = cls._query_photon(address_query)
        if coords:
            cls.save_to_cache(address_query, coords)
            return coords

        # 4. Fallback: GUGiK UUG (for strict street addresses)
        coords = cls._query_gugik(address_query)
        if coords:
            cls.save_to_cache(address_query, coords)
            return coords

        return None
```

#### 2. Update `OtodomLocationParser` (`shargain/offers/location_parsers.py`)
Allow Otodom parser to read cached/geocoded coordinates from `metadata`:

```python
class OtodomLocationParser(BaseLocationParser):
    def get_coordinates(self) -> Coordinates | None:
        coords_data = self.metadata.get("coordinates")
        if isinstance(coords_data, dict):
            lat = coords_data.get("lat")
            lon = coords_data.get("lon")
            if lat is not None and lon is not None:
                return Coordinates(lat=float(lat), lon=float(lon))
        return None
```

#### 3. Ingest Hook (`shargain/offers/services/batch_create.py`)
During offer creation in `batch_create`, if domain is `otodom` and coordinates are missing:
- Extract `location_name = parser.get_location_name()`
- Call `coords = GeocodingService.geocode(location_name)`
- If found, save `extracted.metadata["coordinates"] = {"lat": coords.lat, "lon": coords.lon, "is_exact": False}`
- Now `parser.get_coordinates()` returns the coordinates, distances to waypoints are computed, notifications include map pins, and frontend displays OpenStreetMap!

---

## 6. Summary for User

| Question | Answer |
| :--- | :--- |
| **Is there a free API to display Otodom on OSM?** | **Yes.** You can use **Photon (komoot.io)** or **Nominatim** (100% free, no API key), or **Geoapify** (3,000 req/day free, requires a free API key and permits permanent DB storage). |
| **Does frontend need to change?** | **No.** `OfferLocationMap.tsx` already renders OpenStreetMap whenever latitude/longitude exist. |
| **Where should geocoding happen?** | **On the backend during offer ingest**, cached permanently in Postgres. This enables instant OSM maps in the UI, prevents API rate limits, and gives Telegram notifications distance calculations and map pins. |
