from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class BreweryConfig:
    id: str
    name: str
    url: str
    rule: str


@dataclass(slots=True)
class BeerEntry:
    breweryId: str
    breweryName: str
    name: str
    normalizedName: str
    style: str | None
    abv: float | None
    untappdRating: float | None
    sourceType: str
    sourceUrl: str
    scrapedAt: str
    active: bool


@dataclass(slots=True)
class ComparisonResult:
    breweryId: str
    additions: list[str]
    removals: list[str]
    styleChanges: list[dict[str, str]]
    ratingChanges: list[dict[str, float | str]]


BREWERIES: list[BreweryConfig] = [
    BreweryConfig(
        "grist-house",
        "Grist House",
        "https://gristhouse.com/millvale/",
        "untappd_primary",
    ),
    BreweryConfig(
        "eleventh-hour",
        "11th Hour",
        "https://www.11thhourbrews.com/draft-list",
        "untappd_primary",
    ),
    BreweryConfig(
        "dancing-gnome",
        "Dancing Gnome",
        "https://dancinggnomebeer.com/location/1025-main/#on-tap",
        "merge_website_untappd",
    ),
    BreweryConfig(
        "four-points",
        "Four Points",
        "https://fourpointsbrewing.com/draftlist",
        "draftlist",
    ),
    BreweryConfig(
        "late-addition",
        "Late Addition",
        "https://lateadditionbrewing.com/#beers",
        "beers_section",
    ),
    BreweryConfig(
        "hitchhiker",
        "Hitchhiker",
        "https://hitchhiker.beer",
        "taplist_or_baseline",
    ),
    BreweryConfig(
        "old-thunder",
        "Old Thunder",
        "https://www.oldthunderbrewing.com/_files/ugd/1dde72_2d9ec5c4e9574e7bb3f6c65d4f033297.pdf",
        "pdf",
    ),
    BreweryConfig(
        "abjuration",
        "Abjuration",
        "https://www.abjurationbrewing.com",
        "widget_or_site",
    ),
    BreweryConfig("golden-age", "Golden Age", "https://www.goldenagebeer.com/menu", "menu_page"),
    BreweryConfig("lolev", "Lolev", "https://lolev.beer/beer?avail=tap", "taplist_page"),
]

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


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def entry_to_dict(entry: BeerEntry) -> dict[str, Any]:
    return asdict(entry)
