from __future__ import annotations

from .models import ComparisonResult, TapListEntry


def compare_snapshots(
    brewery_id: str,
    previous_entries: list[TapListEntry],
    current_entries: list[TapListEntry],
) -> ComparisonResult:
    previous_map = {entry.normalized_name: entry for entry in previous_entries}
    current_map = {entry.normalized_name: entry for entry in current_entries}

    added = sorted(current_map.keys() - previous_map.keys())
    removed = sorted(previous_map.keys() - current_map.keys())

    style_changes: list[dict[str, str]] = []
    for key in sorted(previous_map.keys() & current_map.keys()):
        old = previous_map[key].style or ""
        new = current_map[key].style or ""
        if old.strip() != new.strip() and (old or new):
            style_changes.append(
                {
                    "beer": current_map[key].name,
                    "oldStyle": old,
                    "newStyle": new,
                }
            )

    return ComparisonResult(
        brewery_id=brewery_id,
        added=[current_map[name].name for name in added],
        removed=[previous_map[name].name for name in removed],
        style_changes=style_changes,
    )
