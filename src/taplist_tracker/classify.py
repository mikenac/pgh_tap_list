from __future__ import annotations

from .models import TapListEntry

CZECH_LAGER_KEYWORDS = [
    "czech pilsner",
    "bohemian pilsner",
    "czech dark lager",
    "czech amber lager",
    "czech pale lager",
    "czech lager",
    "tmave",
    "tmav",
]

EURO_LAGER_KEYWORDS = [
    "helles",
    "vienna lager",
    "german pils",
    "kellerbier",
    "festbier",
    "marzen",
    "märzen",
    "dortmunder",
    "schwarzbier",
    "dunkel",
    "bock",
    "doppelbock",
    "rauchbier",
    "pilsner",
    "lager",
]

SOUR_KEYWORDS = [
    "sour",
    "fruited sour",
    "kettle sour",
    "berliner weisse",
    "gose",
    "wild ale",
    "mixed culture",
    "lambic",
    "parfait",
    "ice cream sour",
]


def _matches(entry: TapListEntry, keywords: list[str]) -> bool:
    style = (entry.style or "").casefold()
    return any(keyword in style for keyword in keywords)


def czech_watch(entries: list[TapListEntry]) -> list[TapListEntry]:
    return [entry for entry in entries if _matches(entry, CZECH_LAGER_KEYWORDS)]


def euro_lager_watch(entries: list[TapListEntry]) -> list[TapListEntry]:
    return [entry for entry in entries if _matches(entry, EURO_LAGER_KEYWORDS)]


def sour_watch(entries: list[TapListEntry]) -> list[TapListEntry]:
    return [entry for entry in entries if _matches(entry, SOUR_KEYWORDS)]
