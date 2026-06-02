from __future__ import annotations

import re
import unicodedata

UNTAPPD_MARKERS = (
    "untappd.com",
    "business.untappd.com",
    "embedded.untappd.com",
)
TRAILING_PUNCT_RE = re.compile(r"[\s\-–—:;,.!]+$")
ABV_RE = re.compile(r"(?P<value>\d{1,2}(?:\.\d{1,2})?)\s*%")


def normalize_beer_name(name: str) -> str:
    cleaned = name.replace("™", "").replace("®", "")
    cleaned = unicodedata.normalize("NFKC", cleaned)
    cleaned = cleaned.replace("’", "'").replace("‘", "'")
    cleaned = cleaned.replace("“", '"').replace("”", '"')
    cleaned = re.sub(r"\s+", " ", cleaned.strip())
    cleaned = TRAILING_PUNCT_RE.sub("", cleaned)
    return cleaned.casefold().strip()


def normalize_style(style: str | None) -> str | None:
    if style is None:
        return None
    normalized = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", style).strip())
    return normalized or None


def parse_abv(value: str | float | int | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = ABV_RE.search(value)
    if match:
        return float(match.group("value"))
    return None


def has_untappd_embed(raw_html: str) -> bool:
    lowered = raw_html.casefold()
    return any(marker in lowered for marker in UNTAPPD_MARKERS)
