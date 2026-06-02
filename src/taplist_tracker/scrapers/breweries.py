from __future__ import annotations

from ..config import BrewerySourceConfig
from ..models import TapListEntry
from ..normalize import has_untappd_embed, normalize_beer_name
from .base import BreweryScraper, ScrapePayload, choose_by_priority


class GenericBreweryScraper(BreweryScraper):
    def apply_rules(
        self,
        payloads: list[ScrapePayload],
        previous_entries: list[TapListEntry],
    ) -> list[TapListEntry]:
        selected = choose_by_priority(
            payloads,
            priorities=self.config.source_priority,
            merge_sources=self.config.merge_sources,
        )
        return dedupe_entries(self._entries_from_many(selected), self.config.merge_sources)

    def _entries_from_many(self, payloads: list[ScrapePayload]) -> list[TapListEntry]:
        entries: list[TapListEntry] = []
        for payload in payloads:
            entries.extend(self._entries_from_payload(payload))
        return entries


class GristHouseScraper(GenericBreweryScraper):
    def apply_rules(
        self,
        payloads: list[ScrapePayload],
        previous_entries: list[TapListEntry],
    ) -> list[TapListEntry]:
        untappd_payloads = [payload for payload in payloads if payload.source_type == "untappd"]
        if untappd_payloads:
            return dedupe_entries(self._entries_from_many(untappd_payloads), merge=True)

        website_payloads = [
            payload for payload in payloads if payload.source_type in {"website", "static"}
        ]
        for payload in website_payloads:
            if has_untappd_embed(payload.raw_payload):
                return []

        return super().apply_rules(payloads, previous_entries)


class DancingGnomeScraper(GenericBreweryScraper):
    def apply_rules(
        self,
        payloads: list[ScrapePayload],
        previous_entries: list[TapListEntry],
    ) -> list[TapListEntry]:
        merged = self._entries_from_many(
            choose_by_priority(
                payloads,
                priorities=self.config.source_priority,
                merge_sources=True,
            )
        )
        return dedupe_entries(merged, merge=True)


class HitchhikerScraper(GenericBreweryScraper):
    def apply_rules(
        self,
        payloads: list[ScrapePayload],
        previous_entries: list[TapListEntry],
    ) -> list[TapListEntry]:
        entries = super().apply_rules(payloads, previous_entries)
        if entries:
            return entries
        if previous_entries:
            return previous_entries

        baseline: list[TapListEntry] = []
        for name in self.config.baseline_names:
            baseline.append(
                TapListEntry(
                    brewery_id=self.config.brewery.id,
                    name=name,
                    normalized_name=normalize_beer_name(name),
                    source="baseline",
                    active=True,
                )
            )
        return baseline


class OldThunderScraper(GenericBreweryScraper):
    def apply_rules(
        self,
        payloads: list[ScrapePayload],
        previous_entries: list[TapListEntry],
    ) -> list[TapListEntry]:
        pdf_payloads = [payload for payload in payloads if payload.source_type == "pdf"]
        if pdf_payloads:
            entries = self._entries_from_many(pdf_payloads)
            return dedupe_entries(entries, merge=True)
        return super().apply_rules(payloads, previous_entries)


def dedupe_entries(entries: list[TapListEntry], merge: bool) -> list[TapListEntry]:
    by_name: dict[str, TapListEntry] = {}
    for entry in entries:
        existing = by_name.get(entry.normalized_name)
        if existing is None:
            by_name[entry.normalized_name] = entry
            continue

        if merge:
            existing.source_attribution.extend(entry.source_attribution)
            if not existing.style and entry.style:
                existing.style = entry.style
            if existing.abv is None and entry.abv is not None:
                existing.abv = entry.abv
            if existing.untappd_rating is None and entry.untappd_rating is not None:
                existing.untappd_rating = entry.untappd_rating

    return sorted(by_name.values(), key=lambda item: item.normalized_name)


def build_scraper(config: BrewerySourceConfig) -> BreweryScraper:
    if config.brewery.id == "grist-house":
        return GristHouseScraper(config)
    if config.brewery.id == "dancing-gnome":
        return DancingGnomeScraper(config)
    if config.brewery.id == "hitchhiker":
        return HitchhikerScraper(config)
    if config.brewery.id == "old-thunder":
        return OldThunderScraper(config)
    return GenericBreweryScraper(config)
