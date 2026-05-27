export interface ParsedCoordinates {
  lat: number
  lon: number
  label?: string
}

export function parseGoogleMapsUrl(url: string): ParsedCoordinates | null {
  const coordMatch = url.match(/@(-?\d+\.?\d*),(-?\d+\.?\d*)/)
  if (!coordMatch) return null

  const result: ParsedCoordinates = {
    lat: parseFloat(coordMatch[1]),
    lon: parseFloat(coordMatch[2]),
  }

  const placeMatch = url.match(/\/place\/([^/@]+)/)
  if (placeMatch) {
    result.label = decodeURIComponent(placeMatch[1]).replace(/\+/g, ' ')
  }

  return result
}
