from datetime import UTC, date, datetime

from taplist_tracker.classify import czech_watch, euro_lager_watch, sour_watch
from taplist_tracker.compare import compare_snapshots
from taplist_tracker.models import BrewerySnapshot, SourceRecord, TapListEntry
from taplist_tracker.serialize import snapshots_to_json, source_records_to_json


def _entry(name: str, style: str | None) -> TapListEntry:
    return TapListEntry(
        brewery_id="four-points",
        name=name,
        normalized_name=name.casefold(),
        style=style,
        source="website",
    )


def test_compare_detects_add_remove_and_style_change() -> None:
    previous = [_entry("Rice Lager", "Lager"), _entry("Older Beer", "IPA")]
    current = [_entry("Rice Lager", "Japanese Rice Lager"), _entry("New Beer", "Pilsner")]

    result = compare_snapshots("four-points", previous, current)

    assert result.added == ["New Beer"]
    assert result.removed == ["Older Beer"]
    assert result.style_changes == [
        {"beer": "Rice Lager", "oldStyle": "Lager", "newStyle": "Japanese Rice Lager"}
    ]


def test_watch_classifications() -> None:
    entries = [
        _entry("Ceremonials", "Bohemian Pilsner"),
        _entry("House Sour", "Fruited Sour"),
        _entry("Simple Lager", "Helles"),
    ]

    assert [item.name for item in czech_watch(entries)] == ["Ceremonials"]
    assert [item.name for item in sour_watch(entries)] == ["House Sour"]
    assert [item.name for item in euro_lager_watch(entries)] == ["Ceremonials", "Simple Lager"]


def test_serialization_json_shapes() -> None:
    snapshot = BrewerySnapshot(
        snapshot_date=date(2026, 5, 29),
        brewery_id="four-points",
        entries=[_entry("A", "IPA")],
    )
    snapshot_json = snapshots_to_json([snapshot])
    assert '"snapshotDate": "2026-05-29"' in snapshot_json
    assert '"breweryId": "four-points"' in snapshot_json

    record = SourceRecord(
        brewery_id="four-points",
        source_type="website",
        scraped_at=datetime(2026, 5, 29, 14, 15, tzinfo=UTC),
        url="https://example.com",
        raw_payload="raw",
    )
    record_json = source_records_to_json([record])
    assert '"sourceType": "website"' in record_json
    assert '"rawPayload": "raw"' in record_json
