from __future__ import annotations

from collections.abc import Iterable

CZECH = {
    "czech pilsner",
    "bohemian pilsner",
    "czech dark lager",
    "czech amber lager",
    "czech pale lager",
    "czech lager",
}
EURO = {
    "helles",
    "vienna lager",
    "german pils",
    "kellerbier",
    "festbier",
    "märzen",
    "marzen",
    "dortmunder",
    "schwarzbier",
    "dunkel",
    "bock",
    "doppelbock",
    "rauchbier",
    "bohemian pilsner",
    "czech pilsner",
    "czech dark lager",
    "czech amber lager",
    "czech pale lager",
}
SOUR = {
    "sour",
    "fruited sour",
    "kettle sour",
    "berliner weisse",
    "gose",
    "wild ale",
    "mixed culture",
    "lambic",
}


def classify_style(style: str | None) -> str:
    if not style:
        return "other"
    text = style.casefold()
    if any(token in text for token in CZECH):
        return "czech_lager"
    if any(token in text for token in EURO):
        return "european_lager"
    if any(token in text for token in SOUR):
        return "sour"
    if "ipa" in text:
        return "ipa"
    if "stout" in text:
        return "stout"
    return "other"


def filter_by_tag(entries: Iterable[dict], tag: str) -> list[dict]:
    return [entry for entry in entries if entry.get("styleFlag") == tag]
