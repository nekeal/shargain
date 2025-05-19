import json
from dataclasses import dataclass
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests import Response


@dataclass
class OlxOffer:
    _data: dict[str, Any]

    @classmethod
    def from_response(cls, response: Response):
        return cls.from_content(response.content)

    @classmethod
    def from_content(cls, content):
        soup = BeautifulSoup(content, "html.parser")
        parsed_prerendered_state = cls.get_parsed_prerendered_state(soup)
        return cls(json.loads(parsed_prerendered_state))

    @classmethod
    def get_script_tag(cls, soup: BeautifulSoup):
        return soup.select_one("#olx-init-config")

    @classmethod
    def get_parsed_prerendered_state(cls, soup: BeautifulSoup):
        script = cls.get_script_tag(soup)
        return (
            script.string.splitlines()[4]
            .split('"', 1)[1]
            .rsplit('"', 1)[0]
            .replace('\\"', '"')
            .replace('\\\\"', '\\\\\\"')
            .replace("\\\\u", "\\u")
        )

    @classmethod
    def from_url(cls, url: str):
        response = requests.get(url)
        return cls.from_response(response)

    @property
    def offer_data(self):
        return self._data["ad"].get("ad")

    @property
    def price(self):
        return self.offer_data["price"]["regularPrice"]["value"]

    @property
    def title(self):
        return self.offer_data["title"]

    @property
    def photos(self):
        return self.offer_data["photos"]

    @property
    def is_active(self):
        return bool(self.offer_data and self.offer_data["isActive"])
