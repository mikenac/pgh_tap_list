from datetime import UTC, datetime

from taplist_tracker.config import BREWERY_SOURCES
from taplist_tracker.scrapers.base import ScrapePayload
from taplist_tracker.scrapers.breweries import build_scraper

NOW = datetime(2026, 5, 29, 14, 30, tzinfo=UTC)


def test_dancing_gnome_merges_and_dedupes_sources() -> None:
    scraper = build_scraper(BREWERY_SOURCES["dancing-gnome"])
    website_payload = ScrapePayload(
        source_type="website",
        url="https://example.com/website",
        raw_payload="website text",
        extracted_items=[
            {"name": "Double Lustra", "style": "IPA", "abv": "8.0%"},
            {"name": "Czech Star", "style": "Bohemian Pilsner"},
        ],
        scraped_at=NOW,
    )
    untappd_payload = ScrapePayload(
        source_type="untappd",
        url="https://example.com/untappd",
        raw_payload="untappd text",
        extracted_items=[
            {"name": "double lustra", "style": "DIPA", "untappdRating": 4.2},
            {"name": "Foam Room", "style": "Helles"},
        ],
        scraped_at=NOW,
        looks_live=True,
    )

    entries = scraper.apply_rules([website_payload, untappd_payload], previous_entries=[])
    by_name = {entry.normalized_name: entry for entry in entries}

    assert set(by_name.keys()) == {"double lustra", "czech star", "foam room"}
    assert len(by_name["double lustra"].source_attribution) == 2


def test_grist_house_ignores_static_if_untappd_embed_detected() -> None:
    scraper = build_scraper(BREWERY_SOURCES["grist-house"])
    website_payload = ScrapePayload(
        source_type="website",
        url="https://gristhouse.com/millvale",
        raw_payload='<iframe src="https://embedded.untappd.com"></iframe>',
        extracted_items=[{"name": "Not Trusted Beer"}],
        scraped_at=NOW,
    )

    entries = scraper.apply_rules([website_payload], previous_entries=[])
    assert entries == []


def test_hitchhiker_uses_baseline_when_no_data_or_history() -> None:
    scraper = build_scraper(BREWERY_SOURCES["hitchhiker"])

    entries = scraper.apply_rules([], previous_entries=[])

    assert len(entries) == len(BREWERY_SOURCES["hitchhiker"].baseline_names)
    assert entries[0].source == "baseline"


def test_old_thunder_prefers_pdf() -> None:
    scraper = build_scraper(BREWERY_SOURCES["old-thunder"])
    website_payload = ScrapePayload(
        source_type="website",
        url="https://oldthunder.com",
        raw_payload="website",
        extracted_items=[{"name": "Fallback Lager", "style": "Lager"}],
        scraped_at=NOW,
    )
    pdf_payload = ScrapePayload(
        source_type="pdf",
        url="https://oldthunder.com/tap.pdf",
        raw_payload="pdf extract",
        extracted_items=[{"name": "Ceremonials", "style": "Bohemian Pilsner"}],
        scraped_at=NOW,
    )

    entries = scraper.apply_rules([website_payload, pdf_payload], previous_entries=[])

    assert len(entries) == 1
    assert entries[0].name == "Ceremonials"
