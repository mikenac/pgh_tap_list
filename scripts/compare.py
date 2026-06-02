from __future__ import annotations

import html
import json
import re
from pathlib import Path

RATING_DELTA = 0.15
TAG_RE = re.compile(r"<[^>]+>")
ESCAPED_TAG_RE = re.compile(r"<\\\/[^>]+>|<\\[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def clean_display_name(value: str | None, normalized_name: str | None = None) -> str:
    text = (value or "").strip()
    text = text.replace("\\/", "/")
    text = html.unescape(text)
    text = ESCAPED_TAG_RE.sub(" ", text)
    text = TAG_RE.sub(" ", text)
    text = text.replace("\\", " ")
    text = WHITESPACE_RE.sub(" ", text).strip()

    # If the source value was clearly corrupted, fall back to normalized name.
    if (not text) or len(text) > 120 or "$/" in text or "<" in text:
        if normalized_name:
            return " ".join(part.capitalize() for part in normalized_name.split())
    return text[:120]


def compare_entries(previous: list[dict], current: list[dict], brewery_id: str) -> dict:
    prev_map = {
        entry["normalizedName"]: entry
        for entry in previous
        if entry["breweryId"] == brewery_id and entry.get("active", True)
    }
    curr_map = {
        entry["normalizedName"]: entry
        for entry in current
        if entry["breweryId"] == brewery_id and entry.get("active", True)
    }

    added = sorted(curr_map.keys() - prev_map.keys())
    removed = sorted(prev_map.keys() - curr_map.keys())
    style_changes: list[dict[str, str]] = []
    rating_changes: list[dict[str, float | str]] = []

    for key in sorted(prev_map.keys() & curr_map.keys()):
        old = prev_map[key]
        new = curr_map[key]
        old_style = (old.get("style") or "").strip()
        new_style = (new.get("style") or "").strip()
        if old_style != new_style:
            style_changes.append(
                {
                    "beer": clean_display_name(new.get("name"), new.get("normalizedName")),
                    "oldStyle": old_style,
                    "newStyle": new_style,
                }
            )

        old_rating = old.get("untappdRating")
        new_rating = new.get("untappdRating")
        if isinstance(old_rating, (int, float)) and isinstance(new_rating, (int, float)):
            delta = round(float(new_rating) - float(old_rating), 3)
            if abs(delta) >= RATING_DELTA:
                rating_changes.append(
                    {
                        "beer": clean_display_name(new.get("name"), new.get("normalizedName")),
                        "oldRating": round(float(old_rating), 3),
                        "newRating": round(float(new_rating), 3),
                        "delta": delta,
                    }
                )

    return {
        "breweryId": brewery_id,
        "additions": [
            clean_display_name(
                curr_map[key].get("name"),
                curr_map[key].get("normalizedName"),
            )
            for key in added
        ],
        "removals": [
            clean_display_name(
                prev_map[key].get("name"),
                prev_map[key].get("normalizedName"),
            )
            for key in removed
        ],
        "styleChanges": style_changes,
        "ratingChanges": rating_changes,
    }


def main() -> None:
    latest = load_json(Path("data/latest.json"))
    history_files = sorted(Path("data/history").glob("*.json"))

    if len(history_files) < 2:
        comparison = {"generated": latest.get("generatedAt"), "previousDate": None, "changes": []}
    else:
        previous = load_json(history_files[-2])
        current_entries = latest["entries"]
        previous_entries = previous["entries"]
        brewery_ids = sorted({entry["breweryId"] for entry in current_entries})
        comparison = {
            "generated": latest.get("generatedAt"),
            "previousDate": history_files[-2].stem,
            "changes": [
                compare_entries(previous_entries, current_entries, brewery_id)
                for brewery_id in brewery_ids
            ],
        }

    Path("data/comparison.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
