import { describe, expect, it } from 'vitest'
import { parseGoogleMapsUrl } from './google-maps-url'

describe('parseGoogleMapsUrl', () => {
  it('parses a viewport URL with @lat,lon', () => {
    const url = 'https://www.google.pl/maps/@50.0608773,19.9477836,16.39z?entry=ttu'
    const result = parseGoogleMapsUrl(url)
    expect(result).toEqual({ lat: 50.0608773, lon: 19.9477836 })
  })

  it('parses a place URL and extracts label', () => {
    const url = 'https://www.google.pl/maps/place/St.+Mary\'s+Basilica/@50.0608773,19.9477836,16.39z/data=!4m6!3m5!1s0x47165b11f53a5077:0xdd371e3071dcbf32!8m2!3d50.0616411!4d19.9393903!16zL20vMDJsd2Q1?entry=ttu'
    const result = parseGoogleMapsUrl(url)
    expect(result).toEqual({ lat: 50.0608773, lon: 19.9477836, label: "St. Mary's Basilica" })
  })

  it('returns null for non-maps URLs', () => {
    expect(parseGoogleMapsUrl('https://example.com')).toBeNull()
  })

  it('returns null for short goo.gl/maps URLs', () => {
    expect(parseGoogleMapsUrl('https://goo.gl/maps/abc123')).toBeNull()
  })

  it('returns null for malformed place URL without coordinates', () => {
    expect(parseGoogleMapsUrl('https://www.google.pl/maps/place/Some+Place')).toBeNull()
  })
})
