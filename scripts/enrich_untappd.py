from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

RATING_RE = re.compile(r"(\d\.\d{1,2})")
TRAILING_ABV_IN_NAME_RE = re.compile(r"\s*[–-]\s*\d{1,2}(?:\.\d+)?%\s*$")


def simplify_name(name: str) -> str:
    cleaned = TRAILING_ABV_IN_NAME_RE.sub("", name.strip().casefold())
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def fetch_untappd_rating(beer_name: str) -> float | None:
    query_url = f"https://untappd.com/search?q={quote_plus(beer_name)}"
    try:
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            response = client.get(query_url)
            response.raise_for_status()
    except Exception:  # noqa: BLE001
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Try direct rating nodes first.
    for selector in [".num", ".rating", "[data-rating]"]:
        for node in soup.select(selector):
            text = node.get_text(" ", strip=True)
            match = RATING_RE.search(text)
            if match:
                value = float(match.group(1))
                if 0 < value <= 5:
                    return value
            data_rating = node.attrs.get("data-rating")
            if data_rating:
                try:
                    value = float(data_rating)
                    if 0 < value <= 5:
                        return value
                except ValueError:
                    continue
    return None

def main() -> None:
    latest_path = Path("data/latest.json")
    latest = json.loads(latest_path.read_text(encoding="utf-8"))

    rating_path = Path("data/untappd_ratings.json")
    rating_map: dict[str, float] = {}
    if rating_path.exists():
        rating_map = json.loads(rating_path.read_text(encoding="utf-8"))

    alias_rating_map: dict[str, float] = {}
    for key, value in rating_map.items():
        if "::" not in key:
            continue
        brewery_id, beer_key = key.split("::", 1)
        alias_rating_map[f"{brewery_id}::{simplify_name(beer_key)}"] = float(value)

    for entry in latest.get("entries", []):
        key = f"{entry['breweryId']}::{entry['normalizedName']}"
        rating = rating_map.get(key)
        if rating is None:
            alias_key = f"{entry['breweryId']}::{simplify_name(entry['normalizedName'])}"
            rating = alias_rating_map.get(alias_key)
        if rating is None:
            rating = fetch_untappd_rating(entry["name"])
            if rating is not None:
                rating_map[key] = round(float(rating), 2)
        entry["untappdRating"] = float(rating) if rating is not None else None

    latest_path.write_text(json.dumps(latest, indent=2), encoding="utf-8")
    rating_path.write_text(json.dumps(rating_map, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
