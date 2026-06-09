from urllib.parse import urlparse


class DomainMatcher:
    def __init__(self, domain: str) -> None:
        self._domain = domain.lower()

    def matches(self, url: str) -> bool:
        try:
            host = urlparse(url).netloc.lower()
        except ValueError:
            return False
        return host == self._domain or host.endswith("." + self._domain)
