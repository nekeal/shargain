from abc import ABC, abstractmethod


class BaseLocationParser(ABC):
    def __init__(self, metadata: dict):
        self.metadata = metadata
        self.extra = self.metadata.get("extra", {})

    @abstractmethod
    def get_map_url(self) -> str | None:
        pass

    @abstractmethod
    def get_location_name(self) -> str | None:
        pass

    @abstractmethod
    def is_location_exact(self) -> bool:
        pass


class OlxLocationParser(BaseLocationParser):
    def get_map_url(self) -> str | None:
        map_data = self.extra.get("map", {})
        if not isinstance(map_data, dict):
            return None

        lat = map_data.get("lat")
        lon = map_data.get("lon")

        if lat is not None and lon is not None:
            return f"https://maps.google.com/?q={lat},{lon}"
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

    def get_map_url(self) -> str | None:
        return None

    def get_location_name(self) -> str | None:
        return None

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
        elif "otomoto" in domain:
            return OtomotoLocationParser(metadata)

        return DummyLocationParser(metadata)
