"""
Set of utilites validators for supported websites
"""

from urllib.parse import ParseResult, urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


class OlxWebsiteValidator:
    """
    Validator for OLX website
    """

    DOMAIN = "olx.pl"

    def _parse_url(self, url: str) -> ParseResult | None:
        """
        Validates whether url is valid OLX url
        """
        try:
            URLValidator()(url)
            return urlparse(url)
        except ValidationError:
            return None

    def _validate_list_url(self, url: ParseResult) -> bool:
        """
        Validates whether url is url with list of offers
        """
        return url.netloc == self.DOMAIN and "/d/oferta" not in url.path

    def validate_list_url(self, url: str | ParseResult) -> bool:
        """
        Validates whether url is url with list of offers
        """
        parsed_url = url if isinstance(url, ParseResult) else self._parse_url(url)
        if not parsed_url:
            return False

        return self._validate_list_url(parsed_url)
