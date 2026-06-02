from __future__ import annotations

from dataclasses import dataclass, field

from .models import Brewery

HITCHHIKER_BASELINE = [
    "Bane of Existence",
    "Double Dry Hopped Double Bane of Existence",
    "Slow Bane",
    "Drinky & the Brain",
    "High Hop",
    "So Soft",
    "16oz Trip to Ireland",
    "Triple Thick",
    "Point of Confusion",
    "YoRazberry",
    "True",
    "Airwave",
    "Double Airwave",
    "Shadow Walker",
    "You'll Shoot Your Eye Out",
    "Mango Bottle Service",
    "mmHmmm Raspberry Grape Strawberry",
    "Subsurface Blueberry Peach",
    "Whole Punch Blueberry Pie",
    "Sprout",
    "People-Watching",
]


@dataclass(slots=True)
class BrewerySourceConfig:
    brewery: Brewery
    source_priority: list[str]
    merge_sources: bool = False
    untappd_authoritative: bool = False
    is_pdf_source: bool = False
    baseline_names: list[str] = field(default_factory=list)
    watch_tags: list[str] = field(default_factory=list)


BREWERY_SOURCES: dict[str, BrewerySourceConfig] = {
    "grist-house": BrewerySourceConfig(
        brewery=Brewery(
            id="grist-house",
            name="Grist House",
            website="https://gristhouse.com",
            taplist_url="https://gristhouse.com/millvale/",
        ),
        source_priority=["untappd", "widget", "website", "static"],
        untappd_authoritative=True,
    ),
    "dancing-gnome": BrewerySourceConfig(
        brewery=Brewery(
            id="dancing-gnome",
            name="Dancing Gnome",
            website="https://dancinggnomebeer.com",
            taplist_url="https://dancinggnomebeer.com/location/1025-main/#on-tap",
        ),
        source_priority=["untappd", "website", "static"],
        merge_sources=True,
    ),
    "four-points": BrewerySourceConfig(
        brewery=Brewery(
            id="four-points",
            name="Four Points",
            website="https://fourpointsbrewing.com",
            taplist_url="https://fourpointsbrewing.com/draftlist",
        ),
        source_priority=["website", "static"],
        watch_tags=["czech-watch", "euro-lager-watch"],
    ),
    "late-addition": BrewerySourceConfig(
        brewery=Brewery(
            id="late-addition",
            name="Late Addition",
            website="https://lateadditionbrewing.com",
            taplist_url="https://lateadditionbrewing.com/#beers",
        ),
        source_priority=["website", "static"],
        watch_tags=["euro-lager-watch", "sour-watch"],
    ),
    "hitchhiker": BrewerySourceConfig(
        brewery=Brewery(
            id="hitchhiker",
            name="Hitchhiker",
            website="https://hitchhiker.beer",
            taplist_url="https://hitchhiker.beer",
        ),
        source_priority=["untappd", "widget", "website", "static"],
        baseline_names=HITCHHIKER_BASELINE,
    ),
    "old-thunder": BrewerySourceConfig(
        brewery=Brewery(
            id="old-thunder",
            name="Old Thunder",
            website="https://www.oldthunderbrewing.com",
            taplist_url="https://www.oldthunderbrewing.com/_files/ugd/1dde72_2d9ec5c4e9574e7bb3f6c65d4f033297.pdf",
        ),
        source_priority=["pdf", "website", "static"],
        is_pdf_source=True,
        watch_tags=["euro-lager-watch"],
    ),
    "abjuration": BrewerySourceConfig(
        brewery=Brewery(
            id="abjuration",
            name="Abjuration",
            website="https://www.abjurationbrewing.com",
            taplist_url="https://www.abjurationbrewing.com",
        ),
        source_priority=["untappd", "widget", "website", "static"],
        watch_tags=["sour-watch"],
    ),
    "golden-age": BrewerySourceConfig(
        brewery=Brewery(
            id="golden-age",
            name="Golden Age",
            website="https://www.goldenagebeer.com",
            taplist_url="https://www.goldenagebeer.com/menu",
        ),
        source_priority=["website", "static"],
        watch_tags=["czech-watch", "euro-lager-watch"],
    ),
}
