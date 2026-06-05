from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

try:
    from scripts.classify import classify_style
    from scripts.models import BREWERIES
except ModuleNotFoundError:
    from classify import classify_style
    from models import BREWERIES

REPORT_RETENTION_COUNT = 5
DATED_REPORT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


TRAILING_ABV_IN_NAME_RE = re.compile(r"\s*[–-]\s*\d{1,2}(?:\.\d+)?%\s*$")


def simplify_name(name: str) -> str:
    cleaned = TRAILING_ABV_IN_NAME_RE.sub("", name.strip().casefold())
    return re.sub(r"\s+", " ", cleaned)


def load_rating_cache(path: Path = Path("data/untappd_ratings.json")) -> dict[str, float]:
    if not path.exists():
        return {}
    return {
        str(key): float(value)
        for key, value in json.loads(path.read_text(encoding="utf-8")).items()
    }


def cached_rating(row: dict, rating_cache: dict[str, float]) -> float | None:
    rating = row.get("untappdRating")
    if isinstance(rating, (int, float)):
        return float(rating)

    brewery_id = row["breweryId"]
    keys = [
        f"{brewery_id}::{row.get('normalizedName', '')}",
        f"{brewery_id}::{simplify_name(str(row.get('normalizedName', '')))}",
        f"{brewery_id}::{simplify_name(str(row.get('name', '')))}",
    ]
    for key in keys:
        if key in rating_cache:
            return rating_cache[key]
    return None


def rating_stars(rating: float) -> str:
    full_stars = round(max(0.0, min(5.0, rating)))
    return f"{'★' * full_stars}{'☆' * (5 - full_stars)}"


def format_rating(rating: float | None) -> str:
    if rating is None:
        return ""
    return f"{rating_stars(rating)} {rating:.2f}"


def snapshot_date(latest: dict) -> str:
    generated_at = latest.get("generatedAt")
    if isinstance(generated_at, str) and len(generated_at) >= 10:
        return generated_at[:10]
    return datetime.now().date().isoformat()


def grouped(entries: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for entry in entries:
        entry["styleFlag"] = classify_style(entry.get("style"))
        out.setdefault(entry["breweryId"], []).append(entry)
    for items in out.values():
        items.sort(key=lambda row: row["normalizedName"])
    return out


def table(rows: list[dict], rating_cache: dict[str, float] | None = None) -> str:
    if not rows:
        return "_No beers found._"
    header = "| Beer | Style | ABV | Rating | Source |"
    sep = "|---|---|---:|---|---|"
    lines = [header, sep]
    ratings = rating_cache or {}
    for row in rows:
        abv = "" if row.get("abv") is None else f"{row['abv']:.1f}%"
        rating = format_rating(cached_rating(row, ratings))
        lines.append(
            f"| {row['name']} | {row.get('style') or ''} | {abv} | {rating} | {row['sourceType']} |"
        )
    return "\n".join(lines)


def watch(entries: list[dict], tag: str) -> list[dict]:
    return [entry for entry in entries if entry.get("styleFlag") == tag]


def build_report(
    latest: dict,
    comparison: dict,
    ai_summary: str | None,
    rating_cache: dict[str, float] | None = None,
) -> str:
    entries = latest.get("entries", [])
    by_brewery = grouped(entries)
    generated = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    ratings = rating_cache or {}
    report_date = snapshot_date(latest)

    lines: list[str] = [
        f"# Pittsburgh Taplist Report ({report_date})",
        "",
        f"Generated: `{generated}`",
        f"Previous snapshot: `{comparison.get('previousDate')}`",
        "",
        "## What changed this week",
    ]

    for change in comparison.get("changes", []):
        lines.append(f"### {change['breweryId']}")
        lines.append(f"- Added: {', '.join(change['additions']) or 'None'}")
        lines.append(f"- Removed: {', '.join(change['removals']) or 'None'}")
        if change["styleChanges"]:
            lines.append("- Style changes:")
            for item in change["styleChanges"]:
                lines.append(f"  - {item['beer']}: {item['oldStyle']} -> {item['newStyle']}")
        else:
            lines.append("- Style changes: None")
        rating_change_count = (
            len(change["ratingChanges"]) if change["ratingChanges"] else 0
        )
        lines.append(f"- Material rating changes: {rating_change_count}")
        lines.append("")

    if ai_summary:
        lines += ["## Narrative summary (AI)", "", ai_summary.strip(), ""]

    lines.append("## Full lineup")
    for brewery in BREWERIES:
        lines.append(f"### {brewery.name}")
        lines.append(table(by_brewery.get(brewery.id, []), ratings))
        lines.append("")

    lines.append("## Czech Lager Watch")
    lines.append(table(watch(entries, "czech_lager"), ratings))
    lines.append("")
    lines.append("## European Lager Watch")
    lines.append(table(watch(entries, "european_lager"), ratings))
    lines.append("")
    lines.append("## Sour Watch")
    lines.append(table(watch(entries, "sour"), ratings))
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def retained_report_dates(limit: int = REPORT_RETENTION_COUNT) -> set[str]:
    history_dir = Path("data/history")
    if history_dir.exists():
        return {path.stem for path in sorted(history_dir.glob("*.json"))[-limit:]}
    return set()


def prune_report_files(
    out_dir: Path,
    limit: int = REPORT_RETENTION_COUNT,
    current_date: str | None = None,
) -> None:
    retained_dates = retained_report_dates(limit)
    if current_date:
        retained_dates.add(current_date)
    if not retained_dates:
        return

    for report_file in sorted(out_dir.glob("*.md")):
        if report_file.name == "latest.md" or not DATED_REPORT_RE.match(report_file.name):
            continue
        if report_file.stem not in retained_dates:
            report_file.unlink()


def main() -> None:
    latest = load_json("data/latest.json")
    comparison_path = Path("data/comparison.json")
    comparison = load_json(str(comparison_path)) if comparison_path.exists() else {"changes": []}
    ai_path = Path("data/ai-summary.md")
    ai_summary = ai_path.read_text(encoding="utf-8") if ai_path.exists() else None

    report_text = build_report(latest, comparison, ai_summary, load_rating_cache())
    date_slug = snapshot_date(latest)
    out_dir = Path("content/reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / f"{date_slug}.md").write_text(report_text, encoding="utf-8")
    (out_dir / "latest.md").write_text(report_text, encoding="utf-8")
    prune_report_files(out_dir, current_date=date_slug)


if __name__ == "__main__":
    main()
