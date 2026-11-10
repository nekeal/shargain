"""Text and HTML cleaning utilities for field extraction."""

from __future__ import annotations

import html
import re

from django.utils.html import strip_tags


def clean_html_description(val: str | None) -> str | None:
    if not val:
        return None
    val = val.replace(r"\n", "\n")
    text = re.sub(r"(?i)<br\s*/?>", "\n", val)
    text = re.sub(r"(?i)</p>", "\n", text)
    text = strip_tags(text)
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    cleaned = text.strip()
    return cleaned or None
