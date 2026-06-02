from __future__ import annotations

import json
from pathlib import Path

from scripts import scrape


class DummyDate:
    @staticmethod
    def today():
        class _Day:
            @staticmethod
            def isoformat() -> str:
                return "2026-05-29"

        return _Day()


def test_scrape_brewery_rule_paths(monkeypatch) -> None:
    monkeypatch.setattr(
        scrape,
        "fetch_text",
        lambda url: (
            '<iframe src="https://embedded.untappd.com"></iframe>'
            "<li>Lustra - IPA - 6.8%</li>"
        ),
    )
    monkeypatch.setattr(scrape, "fetch_pdf_text", lambda url: "HOUSE PILS | PILSNER\n5.0% ABV")

    grist_entries, raw = scrape.scrape_brewery("grist-house", "Grist House", "u", "untappd_primary")
    assert grist_entries[0].sourceType.startswith("untappd")
    assert "embedded.untappd.com" in raw

    old_entries, _ = scrape.scrape_brewery("old-thunder", "Old Thunder", "u", "pdf")
    assert old_entries[0].sourceType == "pdf"


def test_scrape_abjuration_fetches_on_tap_partial(monkeypatch) -> None:
    def fake_fetch(url: str) -> str:
        if "PartialView/OnTap" in url:
            return """
            <a href="/Beer/112?v=2.0" class="ontapbeer">
              <strong>Fruited India Pale Ale [Grapefruit] (FRIPA v2.0)</strong>
            </a>
            <a href="/Beer/82?v=1.32" class="ontapbeer">
              <strong>Fruited Sour [Pineapple/Honeydew] (FS v1.32)</strong>
            </a>
            """
        return """
        <select id="LocationId" name="LocationId">
          <option value="1">McKees Rocks - The Lab</option>
        </select>
        <div id="ontaplist"></div>
        """

    monkeypatch.setattr(scrape, "fetch_text", fake_fetch)

    entries, raw = scrape.scrape_brewery(
        "abjuration",
        "Abjuration",
        "https://example.com",
        "widget_or_site",
    )

    assert len(entries) == 2
    assert entries[0].sourceType == "widget"
    assert "Abjuration OnTap partial" in raw


def test_scrape_brewery_error_fallback(monkeypatch) -> None:
    def boom(_: str) -> str:
        raise RuntimeError("boom")

    monkeypatch.setattr(scrape, "fetch_text", boom)
    entries, raw = scrape.scrape_brewery("four-points", "Four Points", "u", "draftlist")

    assert entries
    assert entries[0].sourceType.endswith("fallback")
    assert raw.startswith("FETCH_ERROR")


def test_main_writes_latest_and_history(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scrape, "date", DummyDate)
    monkeypatch.setattr(
        scrape,
        "scrape_brewery",
        lambda brewery_id, name, url, rule: (
            [
                scrape.BeerEntry(
                    breweryId=brewery_id,
                    breweryName=name,
                    name=f"{name} Beer",
                    normalizedName=scrape.normalize_name(f"{name} Beer"),
                    style="IPA",
                    abv=6.0,
                    untappdRating=None,
                    sourceType="test",
                    sourceUrl=url,
                    scrapedAt="2026-05-29T00:00:00Z",
                    active=True,
                )
            ],
            "raw",
        ),
    )

    scrape.main()

    latest = json.loads((tmp_path / "data/latest.json").read_text(encoding="utf-8"))
    assert len(latest["entries"]) == len(scrape.BREWERIES)
    assert (tmp_path / "data/history/2026-05-29.json").exists()
