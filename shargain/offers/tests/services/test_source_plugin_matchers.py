import pytest

from shargain.offers.services.source_plugins.matchers import DomainMatcher


class TestDomainMatcher:
    @pytest.mark.parametrize(
        ("url", "domain", "expected"),
        [
            ("https://www.olx.pl/oferta/something-123", "olx.pl", True),
            ("https://olx.pl/oferta/something-123", "olx.pl", True),
            ("https://www.olx.ro/oferta/something", "olx.ro", True),
            ("https://www.otodom.pl/oferta/something", "otodom.pl", True),
            ("https://www.olx.pl/oferta/something", "otodom.pl", False),
            ("https://www.example.com", "olx.pl", False),
            ("https://www.myolx.pl/oferta", "olx.pl", False),
            ("not-a-url", "olx.pl", False),
        ],
    )
    def test_matches(self, url: str, domain: str, expected: bool) -> None:
        matcher = DomainMatcher(domain)
        assert matcher.matches(url) is expected

    def test_substring_safety(self) -> None:
        matcher = DomainMatcher("olx.pl")
        assert matcher.matches("https://www.myolx.pl/item") is False
        assert matcher.matches("https://www.olxplus.pl/item") is False
