from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from ..config import BrewerySourceConfig
from ..models import SourceAttribution, SourceRecord, TapListEntry
from ..normalize import normalize_beer_name, normalize_style, parse_abv


@dataclass(slots=True)
class ScrapePayload:
    source_type: str
    url: str
    raw_payload: str
    extracted_items: list[dict[str, object]]
    scraped_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    looks_live: bool = False


class BreweryScraper:
    def __init__(self, config: BrewerySourceConfig) -> None:
        self.config = config

    def apply_rules(
        self,
        payloads: list[ScrapePayload],
        previous_entries: list[TapListEntry],
    ) -> list[TapListEntry]:
        raise NotImplementedError

    def to_source_records(self, payloads: list[ScrapePayload]) -> list[SourceRecord]:
        return [
            SourceRecord(
                brewery_id=self.config.brewery.id,
                source_type=payload.source_type,
                scraped_at=payload.scraped_at,
                url=payload.url,
                raw_payload=payload.raw_payload,
            )
            for payload in payloads
        ]

    def _entries_from_payload(self, payload: ScrapePayload) -> list[TapListEntry]:
        entries: list[TapListEntry] = []
        for item in payload.extracted_items:
            name = str(item.get("name", "")).strip()
            if not name:
                continue
            attribution = SourceAttribution(
                source_type=payload.source_type,
                url=payload.url,
                scraped_at=payload.scraped_at,
                details="live" if payload.looks_live else None,
            )
            style_value = item.get("style")
            normalized_style = normalize_style(
                style_value if isinstance(style_value, str) else None
            )
            entries.append(
                TapListEntry(
                    brewery_id=self.config.brewery.id,
                    name=name,
                    normalized_name=normalize_beer_name(name),
                    style=normalized_style,
                    abv=parse_abv(item.get("abv")),
                    source=payload.source_type,
                    untappd_rating=(
                        float(item["untappdRating"])
                        if item.get("untappdRating") is not None
                        else None
                    ),
                    source_attribution=[attribution],
                )
            )
        return entries


def choose_by_priority(
    payloads: list[ScrapePayload],
    priorities: list[str],
    merge_sources: bool,
) -> list[ScrapePayload]:
    if not payloads:
        return []

    ordered = sorted(
        payloads,
        key=lambda payload: (
            (
                priorities.index(payload.source_type)
                if payload.source_type in priorities
                else len(priorities)
            ),
            0 if payload.looks_live else 1,
            -payload.scraped_at.timestamp(),
        ),
    )

    if merge_sources:
        return ordered

    primary_type = ordered[0].source_type
    return [payload for payload in ordered if payload.source_type == primary_type]
