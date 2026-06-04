from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REQUIRED_FIELDS = {
    "breweryId",
    "breweryName",
    "name",
    "normalizedName",
    "style",
    "abv",
    "untappdRating",
    "sourceType",
    "sourceUrl",
    "scrapedAt",
    "active",
}

EXPECTED_BREWERIES = {
    "grist-house",
    "eleventh-hour",
    "acclamation",
    "dancing-gnome",
    "four-points",
    "late-addition",
    "hitchhiker",
    "old-thunder",
    "abjuration",
    "golden-age",
    "lolev",
}

# Lower bounds to catch obvious parser breakage while allowing real taplist changes.
MIN_ENTRIES_PER_BREWERY = {
    "grist-house": 8,
    "eleventh-hour": 5,
    "acclamation": 8,
    "dancing-gnome": 8,
    "four-points": 8,
    "late-addition": 8,
    "hitchhiker": 1,
    "old-thunder": 8,
    "abjuration": 8,
    "golden-age": 6,
    "lolev": 5,
}

MIN_ABV_NON_NULL = {
    "grist-house": 6,
    "eleventh-hour": 5,
    "acclamation": 8,
    "dancing-gnome": 6,
    "four-points": 10,
    "late-addition": 8,
    "old-thunder": 8,
    "golden-age": 5,
    "lolev": 5,
}

MAX_NAME_LENGTH = 120
ALLOWED_SOURCE_TYPES = {
    "website",
    "static",
    "pdf",
    "merged",
    "widget",
    "untappd",
    "baseline",
    "website_fallback",
    "static_fallback",
    "pdf_fallback",
    "merged_fallback",
    "widget_fallback",
    "untappd_fallback",
}

HTML_LEAK_RE = re.compile(r"<\\?/|\\/span|\\/div|\\/a|\\/p|\\/strong")


def load_latest() -> dict:
    latest_path = Path("data/latest.json")
    assert latest_path.exists(), "data/latest.json does not exist; run scripts/scrape.py first"
    return json.loads(latest_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def latest_entries() -> list[dict]:
    latest = load_latest()
    entries = latest.get("entries")
    assert isinstance(entries, list), "latest.json must contain an entries list"
    return entries


def test_expected_breweries_present(latest_entries: list[dict]) -> None:
    observed = {entry["breweryId"] for entry in latest_entries}
    missing = EXPECTED_BREWERIES - observed
    assert not missing, f"Missing brewery IDs in latest.json: {sorted(missing)}"


def test_required_fields_exist(latest_entries: list[dict]) -> None:
    for idx, entry in enumerate(latest_entries):
        missing = REQUIRED_FIELDS - set(entry.keys())
        assert not missing, f"Entry {idx} missing required fields: {sorted(missing)}"


def test_no_escaped_html_in_name(latest_entries: list[dict]) -> None:
    bad = [entry for entry in latest_entries if HTML_LEAK_RE.search(entry["name"])]
    assert not bad, f"Found escaped HTML fragments in names: {[entry['name'] for entry in bad[:3]]}"


def test_name_length_and_shape(latest_entries: list[dict]) -> None:
    bad = []
    for entry in latest_entries:
        name = entry["name"]
        if not isinstance(name, str):
            bad.append((entry["breweryId"], name))
            continue
        if not (1 < len(name) <= MAX_NAME_LENGTH):
            bad.append((entry["breweryId"], name))
            continue
        if name.strip() != name:
            bad.append((entry["breweryId"], name))
    assert not bad, f"Malformed names found: {bad[:5]}"


def test_unique_normalized_name_per_brewery(latest_entries: list[dict]) -> None:
    seen: dict[tuple[str, str], str] = {}
    dupes: list[tuple[str, str]] = []
    for entry in latest_entries:
        key = (entry["breweryId"], entry["normalizedName"])
        if key in seen:
            dupes.append(key)
        else:
            seen[key] = entry["name"]
    assert not dupes, f"Duplicate normalized names per brewery: {dupes[:10]}"


def test_source_type_is_allowed(latest_entries: list[dict]) -> None:
    bad = sorted(
        {
            entry["sourceType"]
            for entry in latest_entries
            if entry["sourceType"] not in ALLOWED_SOURCE_TYPES
        }
    )
    assert not bad, f"Unknown sourceType values found: {bad}"


def test_per_brewery_minimum_counts(latest_entries: list[dict]) -> None:
    counts: dict[str, int] = {}
    for entry in latest_entries:
        counts[entry["breweryId"]] = counts.get(entry["breweryId"], 0) + 1

    failures = []
    for brewery_id, minimum in MIN_ENTRIES_PER_BREWERY.items():
        actual = counts.get(brewery_id, 0)
        if actual < minimum:
            failures.append((brewery_id, actual, minimum))

    assert not failures, f"Entry count quality gate failures: {failures}"


def test_per_brewery_abv_minimums(latest_entries: list[dict]) -> None:
    by_brewery: dict[str, list[dict]] = {}
    for entry in latest_entries:
        by_brewery.setdefault(entry["breweryId"], []).append(entry)

    failures = []
    for brewery_id, minimum in MIN_ABV_NON_NULL.items():
        rows = by_brewery.get(brewery_id, [])
        non_null_abv = sum(1 for row in rows if isinstance(row.get("abv"), (int, float)))
        if non_null_abv < minimum:
            failures.append((brewery_id, non_null_abv, minimum))

    assert not failures, f"ABV completeness quality gate failures: {failures}"
