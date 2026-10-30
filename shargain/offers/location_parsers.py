from abc import ABC, abstractmethod
from urllib.parse import quote

from shargain.offers.geo import Coordinates


class BaseLocationParser(ABC):
    def __init__(self, metadata: dict):
        self.metadata = metadata
        self.extra = self.metadata.get("extra", {})

    @abstractmethod
    def get_coordinates(self) -> Coordinates | None:
        pass

    @abstractmethod
    def get_map_url(self, map_center: Coordinates | None = None) -> str | None:
        pass

    @abstractmethod
    def get_location_name(self) -> str | None:
        pass

    @abstractmethod
    def is_location_exact(self) -> bool:
        pass


class OlxLocationParser(BaseLocationParser):
    def get_coordinates(self) -> Coordinates | None:
        map_data = self.extra.get("map", {})
        if not isinstance(map_data, dict):
            return None

        lat = map_data.get("lat")
        lon = map_data.get("lon")

        if lat is not None and lon is not None:
            return Coordinates(lat=lat, lon=lon)
        return None

    def get_map_url(self, map_center: Coordinates | None = None) -> str | None:
        coords = self.get_coordinates()
        if coords:
            return f"https://maps.google.com/?q={coords.lat},{coords.lon}&ll={coords.lat},{coords.lon}&z=13"
        return None

    def get_location_name(self) -> str | None:
        location_data = self.extra.get("location", {})
        if not isinstance(location_data, dict):
            return None

        city = location_data.get("cityName")
        district = location_data.get("districtName")

        if city and district:
            return f"{city}, {district}"
        return city or district or None

    def is_location_exact(self) -> bool:
        map_data = self.extra.get("map", {})
        if not isinstance(map_data, dict):
            return False
        return bool(map_data.get("show_detailed", False))


class DummyLocationParser(BaseLocationParser):
    """Fallback parser that returns no location data."""

    def get_coordinates(self) -> Coordinates | None:
        return None

    def get_map_url(self, map_center: Coordinates | None = None) -> str | None:
        return None

    def get_location_name(self) -> str | None:
        return None

    def is_location_exact(self) -> bool:
        return False


class OtodomLocationParser(BaseLocationParser):
    def get_coordinates(self) -> Coordinates | None:
        return None

    def get_map_url(self, map_center: Coordinates | None = None) -> str | None:
        location_name = self.get_location_name()
        if not location_name:
            return None
        base = f"https://maps.google.com/?q={quote(location_name)}"
        if map_center:
            base += f"&ll={map_center.lat},{map_center.lon}&z=13"
        return base

    @staticmethod
    def _reverse_geocoding_name(location: dict, level: str) -> str | None:
        locations = (location.get("reverseGeocoding") or {}).get("locations") or []
        for item in locations:
            if item.get("locationLevel") == level and item.get("name"):
                return str(item["name"])
        return None

    def get_location_name(self) -> str | None:
        location = self.extra.get("location") or {}
        address = location.get("address") or {}
        city_name = (address.get("city") or {}).get("name") or self._reverse_geocoding_name(location, "city_or_village")

        if street_name := (address.get("street") or {}).get("name"):
            return f"{city_name}, {street_name}" if city_name else str(street_name)

        if not city_name:
            return None

        district_name = self._reverse_geocoding_name(location, "district") or self._reverse_geocoding_name(
            location, "residential"
        )
        if district_name and district_name != city_name:
            return f"{city_name}, {district_name}"
        return str(city_name)

    def is_location_exact(self) -> bool:
        return False


class OtomotoLocationParser(DummyLocationParser):
    """Placeholder for Otomoto location parser once the format is known."""

    pass


class LocationParserFactory:
    @staticmethod
    def get_parser(domain: str, metadata: dict) -> BaseLocationParser:
        if "olx" in domain:
            return OlxLocationParser(metadata)
        elif "otodom" in domain:
            return OtodomLocationParser(metadata)
        elif "otomoto" in domain:
            return OtomotoLocationParser(metadata)

        return DummyLocationParser(metadata)
