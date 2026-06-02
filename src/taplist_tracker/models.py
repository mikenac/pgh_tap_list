from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any


@dataclass(slots=True)
class Brewery:
    id: str
    name: str
    website: str
    taplist_url: str


@dataclass(slots=True)
class SourceAttribution:
    source_type: str
    url: str
    scraped_at: datetime
    details: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "sourceType": self.source_type,
            "url": self.url,
            "scrapedAt": self.scraped_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        }
        if self.details:
            payload["details"] = self.details
        return payload


@dataclass(slots=True)
class TapListEntry:
    brewery_id: str
    name: str
    normalized_name: str
    source: str
    active: bool = True
    style: str | None = None
    abv: float | None = None
    untappd_rating: float | None = None
    source_attribution: list[SourceAttribution] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "breweryId": self.brewery_id,
            "name": self.name,
            "normalizedName": self.normalized_name,
            "style": self.style,
            "abv": self.abv,
            "untappdRating": self.untappd_rating,
            "source": self.source,
            "active": self.active,
            "sourceAttribution": [source.as_dict() for source in self.source_attribution],
        }


@dataclass(slots=True)
class SourceRecord:
    brewery_id: str
    source_type: str
    scraped_at: datetime
    url: str
    raw_payload: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "breweryId": self.brewery_id,
            "sourceType": self.source_type,
            "scrapedAt": self.scraped_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            "url": self.url,
            "rawPayload": self.raw_payload,
        }


@dataclass(slots=True)
class BrewerySnapshot:
    snapshot_date: date
    brewery_id: str
    entries: list[TapListEntry]

    def as_dict(self) -> dict[str, Any]:
        return {
            "snapshotDate": self.snapshot_date.isoformat(),
            "breweryId": self.brewery_id,
            "entries": [entry.as_dict() for entry in self.entries],
        }


@dataclass(slots=True)
class ComparisonResult:
    brewery_id: str
    added: list[str]
    removed: list[str]
    style_changes: list[dict[str, str]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "breweryId": self.brewery_id,
            "added": self.added,
            "removed": self.removed,
            "styleChanges": self.style_changes,
        }


BeerEntry = TapListEntry
