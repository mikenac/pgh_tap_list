from __future__ import annotations

import json
from pathlib import Path

from scripts import compare, enrich_untappd, generate_report, scrape


def test_scrape_helpers() -> None:
    assert scrape.parse_abv("6.5%") == 6.5
    entries = scrape.as_entries(
        brewery_id="x",
        brewery_name="X",
        source_type="website",
        source_url="https://example.com",
        items=[{"name": " Test Beer ", "style": "IPA", "abv": "7.1%"}],
        scraped_at="2026-05-29T00:00:00Z",
    )
    assert entries[0].normalizedName == "test beer"
    assert scrape.dedupe(entries + entries) == entries


def test_previous_entries_quality_helpers(tmp_path: Path) -> None:
    latest = {
        "entries": [
            {
                "breweryId": "late-addition",
                "breweryName": "Late Addition",
                "name": f"Beer {idx}",
                "normalizedName": f"beer-{idx}",
                "style": "IPA",
                "abv": 5.0,
                "untappdRating": None,
                "sourceType": "website",
                "sourceUrl": "https://lateadditionbrewing.com/#beers",
                "scrapedAt": "2026-06-03T00:00:00Z",
                "active": True,
            }
            for idx in range(8)
        ]
    }
    latest_path = tmp_path / "latest.json"
    latest_path.write_text(json.dumps(latest), encoding="utf-8")

    previous = scrape.load_previous_entries(latest_path)["late-addition"]
    degraded = previous[:1]

    assert scrape.entries_pass_quality("late-addition", previous)
    assert not scrape.entries_pass_quality("late-addition", degraded)


def test_compare_main_and_enrich_main(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data/history").mkdir(parents=True)
    latest = {
        "generatedAt": "2026-05-29T00:00:00Z",
        "entries": [
            {
                "breweryId": "x",
                "normalizedName": "beer-a",
                "name": "Beer A",
                "style": "IPA",
                "untappdRating": 4.0,
                "active": True,
            }
        ],
    }
    prev = {
        "generatedAt": "2026-05-28T00:00:00Z",
        "entries": [
            {
                "breweryId": "x",
                "normalizedName": "beer-a",
                "name": "Beer A",
                "style": "Pale Ale",
                "untappdRating": 3.7,
                "active": True,
            }
        ],
    }
    (tmp_path / "data/latest.json").write_text(json.dumps(latest), encoding="utf-8")
    (tmp_path / "data/history/2026-05-28.json").write_text(json.dumps(prev), encoding="utf-8")
    (tmp_path / "data/history/2026-05-29.json").write_text(json.dumps(latest), encoding="utf-8")

    compare.main()
    comparison = json.loads((tmp_path / "data/comparison.json").read_text(encoding="utf-8"))
    assert comparison["changes"][0]["styleChanges"]

    (tmp_path / "data/untappd_ratings.json").write_text(
        json.dumps({"x::beer-a": 4.22}), encoding="utf-8"
    )
    enrich_untappd.main()
    enriched = json.loads((tmp_path / "data/latest.json").read_text(encoding="utf-8"))
    assert enriched["entries"][0]["untappdRating"] == 4.22


def test_generate_report_main(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    latest = {
        "entries": [
            {
                "breweryId": "four-points",
                "breweryName": "Four Points",
                "name": "Ceremonials",
                "normalizedName": "ceremonials",
                "style": "Bohemian Pilsner",
                "abv": 5.2,
                "untappdRating": 3.9,
                "sourceType": "website",
            }
        ]
    }
    comparison = {
        "previousDate": "2026-05-28",
        "changes": [
            {
                "breweryId": "four-points",
                "additions": ["Ceremonials"],
                "removals": [],
                "styleChanges": [],
                "ratingChanges": [],
            }
        ],
    }
    (tmp_path / "data/latest.json").write_text(json.dumps(latest), encoding="utf-8")
    (tmp_path / "data/comparison.json").write_text(json.dumps(comparison), encoding="utf-8")
    (tmp_path / "data/untappd_ratings.json").write_text(
        json.dumps({"four-points::ceremonials": 3.9}), encoding="utf-8"
    )

    generate_report.main()

    latest_report = tmp_path / "content/reports/latest.md"
    assert latest_report.exists()
    report_text = latest_report.read_text(encoding="utf-8")
    assert "Czech Lager Watch" in report_text
    assert "★★★★☆ 3.90" in report_text


def test_report_uses_cached_rating_when_entry_rating_is_missing() -> None:
    rows = [
        {
            "breweryId": "four-points",
            "name": "Ceremonials",
            "normalizedName": "ceremonials",
            "style": "Bohemian Pilsner",
            "abv": 5.2,
            "untappdRating": None,
            "sourceType": "website",
        }
    ]

    rendered = generate_report.table(rows, {"four-points::ceremonials": 3.9})

    assert "★★★★☆ 3.90" in rendered
