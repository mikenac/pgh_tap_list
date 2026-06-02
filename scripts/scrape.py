from __future__ import annotations

import json
import re
import unicodedata
from datetime import UTC, date, datetime
from pathlib import Path
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

try:
    from scripts.models import BREWERIES, HITCHHIKER_BASELINE, BeerEntry, entry_to_dict, now_iso
except ModuleNotFoundError:
    from models import BREWERIES, HITCHHIKER_BASELINE, BeerEntry, entry_to_dict, now_iso

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
HISTORY_DIR = DATA_DIR / "history"

UNTAPPD_MARKERS = ("untappd.com", "business.untappd.com", "embedded.untappd.com")
ABV_RE = re.compile(r"(\d{1,2}(?:\.\d{1,2})?)\s*%")
TRAILING_PUNCT_RE = re.compile(r"[\s\-–—:;,.!]+$")
PRICE_RE = re.compile(r"\$\s*\d")
UNTAPPD_PRELOAD_RE = re.compile(
    r'PreloadEmbedMenu\("(?P<container>[^"]+)",\s*(?P<location>\d+),\s*(?P<theme>\d+)\)'
)

# Deterministic fallback samples used only when live fetch/parsing yields nothing.
SAMPLE_MENU: dict[str, list[dict[str, str]]] = {
    "grist-house": [{"name": "Lucid Man's Sea", "style": "Hazy IPA", "abv": "6.5%"}],
    "dancing-gnome": [
        {"name": "Lustra", "style": "IPA", "abv": "6.8%"},
        {"name": "Dead Sleep", "style": "Helles Lager", "abv": "5.2%"},
    ],
    "four-points": [{"name": "Ceremonials", "style": "Bohemian Pilsner", "abv": "5.2%"}],
    "late-addition": [{"name": "Blend Logic", "style": "Mixed Culture Sour", "abv": "6.0%"}],
    "hitchhiker": [{"name": "Bane of Existence", "style": "Double IPA", "abv": "8.2%"}],
    "old-thunder": [{"name": "House Pils", "style": "Pilsner", "abv": "5.0%"}],
    "abjuration": [{"name": "Parfait Doom", "style": "Ice Cream Sour", "abv": "6.1%"}],
    "golden-age": [{"name": "Amber Hall", "style": "Czech Amber Lager", "abv": "5.4%"}],
}


def normalize_name(name: str) -> str:
    cleaned = name.replace("™", "").replace("®", "")
    cleaned = unicodedata.normalize("NFKC", cleaned)
    cleaned = cleaned.replace("’", "'").replace("‘", "'")
    cleaned = re.sub(r"\s+", " ", cleaned.strip())
    cleaned = TRAILING_PUNCT_RE.sub("", cleaned)
    return cleaned.casefold().strip()


def parse_abv(raw: str | None) -> float | None:
    if not raw:
        return None
    match = ABV_RE.search(raw)
    return float(match.group(1)) if match else None


def fetch_text(url: str) -> str:
    with httpx.Client(timeout=20, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text


def fetch_pdf_text(url: str) -> str:
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        pdf_path = RAW_DIR / "old-thunder-latest.pdf"
        pdf_path.write_bytes(response.content)
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def has_untappd_embed(html: str) -> bool:
    lowered = html.casefold()
    return any(marker in lowered for marker in UNTAPPD_MARKERS)


def parse_html_taplist(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    lines: list[str] = []
    for node in soup.select("li, tr, .beer, .tap, .menu-item, .product, h3"):
        text = " ".join(node.get_text(" ", strip=True).split())
        if len(text) > 3:
            lines.append(text)

    items: list[dict[str, str]] = []
    for line in lines:
        if len(items) >= 40:
            break
        if any(
            word in line.casefold()
            for word in ["tap", "abv", "%", "lager", "ipa", "sour", "stout", "pils"]
        ):
            parts = [part.strip() for part in re.split(r"[\-|•]", line) if part.strip()]
            name = parts[0]
            style = parts[1] if len(parts) > 1 else None
            items.append({"name": name, "style": style, "abv": line})
    return items


def normalize_spaced_text(value: str) -> str:
    # Old Thunder PDF extraction may emit one-character spaced tokens.
    collapsed = re.sub(r"(?<=\b[A-Za-z])\s(?=[A-Za-z]\b)", "", value)
    collapsed = re.sub(r"(?<=\d)\s+(?=\d)", "", collapsed)
    collapsed = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", collapsed)
    collapsed = re.sub(r"\s*%\s*", "% ", collapsed)
    collapsed = re.sub(r"\babv\b", "ABV", collapsed, flags=re.IGNORECASE)
    collapsed = re.sub(r"\s+", " ", collapsed).strip()
    return collapsed


def split_name_style_abv(text: str) -> tuple[str, str | None, float | None]:
    cleaned = normalize_spaced_text(text)
    abv_match = re.search(r"(\d{1,2}(?:\.\d{1,2})?)\s*%?\s*ABV", cleaned, re.IGNORECASE)
    abv = float(abv_match.group(1)) if abv_match else parse_abv(cleaned)
    if abv_match:
        cleaned = cleaned[: abv_match.start()].strip(" -|")

    for sep in ("|", " - ", " — ", " – ", ": "):
        if sep in cleaned:
            left, right = cleaned.split(sep, 1)
            return left.strip(), right.strip() or None, abv

    tokens = cleaned.split()
    if len(tokens) >= 3:
        for style_len in range(4, 1, -1):
            if len(tokens) > style_len:
                name = " ".join(tokens[:-style_len]).strip()
                style = " ".join(tokens[-style_len:]).strip()
                if len(name) > 1 and len(style) > 2:
                    return name, style, abv
    return cleaned.strip(), None, abv


def parse_old_thunder_pdf(raw_text: str) -> list[dict[str, str]]:
    lines = [normalize_spaced_text(line) for line in raw_text.splitlines()]
    lines = [line for line in lines if line]
    items: list[dict[str, str]] = []

    for index, line in enumerate(lines):
        if "|" not in line:
            continue
        left, right = [part.strip() for part in line.split("|", 1)]
        if not left or not right:
            continue
        if re.fullmatch(r"[0-9 ]+LAGER", left.upper()):
            left = re.sub(r"\s+", " ", left).strip()
        upper_name = left.upper()
        if any(skip in upper_name for skip in ["NON-BEER", "COCKTAIL", "SNACK", "OPTION"]):
            continue
        if len(left) < 3 or PRICE_RE.search(left):
            continue

        style = right
        style = re.split(r"[a-z]{2,}", style, maxsplit=1)[0].strip() or style
        window = " ".join(lines[index : index + 4])
        abv = parse_abv(window)
        if abv is None:
            continue
        items.append({"name": left, "style": style.title(), "abv": f"{abv}%"})
    return items


def parse_late_addition_html(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]

    items: list[dict[str, str]] = []
    for idx, line in enumerate(lines):
        if "ABV" not in line.upper() or "%" not in line:
            continue
        if any(
            token in line.lower()
            for token in ["trivia", "taproom events", "pm", "calendar", "hours", "address"]
        ):
            continue
        style_line = lines[idx - 1] if idx > 0 else ""
        name_line = lines[idx - 2] if idx > 1 else ""
        if not name_line or any(
            token in name_line.lower()
            for token in ["our beers", "upcoming", "now on tap", "food trucks", "contact us"]
        ):
            continue
        name = re.sub(r"^[•*-]\s*", "", name_line).strip()
        style = style_line.strip() or None
        abv = parse_abv(line)
        if len(name) < 3 or name.lower().startswith("june "):
            continue
        if style and any(token in style.lower() for token in ["trivia", "events", "calendar"]):
            style = None
        items.append({"name": name, "style": style, "abv": f"{abv}%" if abv else None})
    return items


def parse_dancing_gnome_html(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    items: list[dict[str, str]] = []
    seen: set[str] = set()

    # Preferred source: embedded Untappd/Craftpeak tap module.
    for row in soup.select(".module--untappd-wot .list-item"):
        title_node = row.select_one(".item-title")
        descriptor_node = row.select_one(".item-descriptor")
        if not title_node:
            continue
        name = re.sub(r"\s+", " ", title_node.get_text(" ", strip=True)).strip(" -|")
        style = (
            re.sub(r"\s+", " ", descriptor_node.get_text(" ", strip=True)).strip(" -|")
            if descriptor_node
            else None
        )
        row_text = re.sub(r"\s+", " ", row.get_text(" ", strip=True))
        abv = parse_abv(row_text)
        key = normalize_name(name)
        if len(name) > 1 and key not in seen:
            seen.add(key)
            items.append({"name": name, "style": style, "abv": f"{abv}%" if abv else None})

    # Craftpeak often exposes beers in title attributes like "Beer Name – 6.5%".
    for node in soup.select("[title]"):
        title = node.attrs.get("title", "").strip()
        match = re.match(r"^(?P<name>.+?)\s*[–-]\s*(?P<abv>\d{1,2}(?:\.\d+)?)%$", title)
        if not match:
            continue
        name = match.group("name").strip()
        if len(name) < 2:
            continue
        key = normalize_name(name)
        if key in seen:
            continue
        seen.add(key)
        items.append({"name": name, "style": None, "abv": f"{match.group('abv')}%"})
    return items


def extract_embed_html_from_js(js_text: str) -> str | None:
    marker = 'container.innerHTML = "'
    start = js_text.find(marker)
    if start == -1:
        return None
    start += len(marker)
    end = js_text.find('";\n', start)
    if end == -1:
        end = js_text.find('";', start)
    if end == -1:
        return None
    encoded = js_text[start:end]
    decoded = encoded
    decoded = decoded.replace("\\n", "\n")
    decoded = decoded.replace('\\"', '"')
    decoded = decoded.replace("\\/", "/")
    decoded = decoded.replace("\\t", "\t")
    return decoded


def parse_untappd_embed_html(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    items: list[dict[str, str]] = []
    for row in soup.select(".menu-item"):
        name_node = row.select_one(".item-name")
        style_node = row.select_one(".item-style")
        abv_node = row.select_one(".item-abv")
        if not name_node:
            continue
        name = re.sub(r"\s+", " ", name_node.get_text(" ", strip=True)).strip(" -|")
        style = (
            re.sub(r"\s+", " ", style_node.get_text(" ", strip=True)).strip(" -|")
            if style_node
            else None
        )
        if style:
            lowered_name = name.casefold()
            lowered_style = style.casefold()
            if lowered_name.endswith(lowered_style):
                name = name[: -len(style)].strip(" -|")
        abv = parse_abv(abv_node.get_text(" ", strip=True) if abv_node else None)
        if len(name) < 2:
            continue
        items.append({"name": name, "style": style, "abv": f"{abv}%" if abv is not None else None})
    return items


def parse_grist_house_html(html: str) -> list[dict[str, str]]:
    preload_match = UNTAPPD_PRELOAD_RE.search(html)
    if not preload_match:
        return []

    location_id = preload_match.group("location")
    theme_id = preload_match.group("theme")
    embed_js_url = f"https://business.untappd.com/locations/{location_id}/themes/{theme_id}/js"
    try:
        with httpx.Client(timeout=20, follow_redirects=True) as client:
            response = client.get(embed_js_url)
            response.raise_for_status()
    except Exception:  # noqa: BLE001
        return []

    embed_html = extract_embed_html_from_js(response.text)
    if not embed_html:
        return []
    return parse_untappd_embed_html(embed_html)


def parse_golden_age_html(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    items: list[dict[str, str]] = []

    for block in soup.select(".menu-item"):
        title_node = block.select_one(".menu-item-title")
        description_node = block.select_one(".menu-item-description")
        if not title_node:
            continue
        name = re.sub(r"\s+", " ", title_node.get_text(" ", strip=True)).strip()
        if not name or name.startswith("$"):
            continue
        if any(token in name.lower() for token in ["menu", "food", "drinks"]):
            continue

        description = ""
        if description_node:
            description = re.sub(r"\s+", " ", description_node.get_text(" ", strip=True)).strip()
        abv = parse_abv(description)
        style = None
        if description:
            style = re.split(r"\d{1,2}(?:\.\d+)?\s*%", description)[0].strip(" -|")
            if len(style) < 3:
                style = None
        items.append({"name": name, "style": style, "abv": f"{abv}%" if abv else None})
    return items


def parse_four_points_html(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    items: list[dict[str, str]] = []

    for paragraph in soup.select("p"):
        strong_nodes = paragraph.select("strong")
        em_nodes = paragraph.select("em")
        text = re.sub(r"\s+", " ", paragraph.get_text(" ", strip=True)).strip()
        if not strong_nodes or not em_nodes or "%" not in text:
            continue
        name = re.sub(r"\s+", " ", strong_nodes[0].get_text(" ", strip=True)).strip(" -|")
        style = None
        for node in em_nodes:
            candidate = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip(" -|")
            if candidate and not candidate.startswith("*"):
                style = candidate
                break
        if style is None:
            style = re.sub(r"\s+", " ", em_nodes[0].get_text(" ", strip=True)).strip(" -|")
        abv = parse_abv(text)
        if not name or abv is None:
            continue
        if any(token in style.lower() for token in ["cocktail", "vodka soda"]):
            continue
        if any(token in name.lower() for token in ["available cans", "stateside / surfside"]):
            continue
        items.append({"name": name, "style": style or None, "abv": f"{abv}%"})
    return items


def parse_abjuration_on_tap_html(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    items: list[dict[str, str]] = []
    seen: set[str] = set()

    for anchor in soup.select("a.ontapbeer"):
        name = re.sub(r"\s+", " ", anchor.get_text(" ", strip=True)).strip()
        if len(name) < 2:
            continue
        key = normalize_name(name)
        if key in seen:
            continue
        seen.add(key)

        style = re.split(r"\s*(?:\[|\()", name, maxsplit=1)[0].strip()
        items.append({"name": name, "style": style or None, "abv": None})
    return items


def abjuration_location_id(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    selected = soup.select_one("#LocationId option[selected]")
    if selected and selected.get("value"):
        return str(selected["value"])
    first_option = soup.select_one("#LocationId option[value]")
    if first_option and first_option.get("value"):
        return str(first_option["value"])
    hidden = soup.select_one("#locationId[value]")
    if hidden and hidden.get("value"):
        return str(hidden["value"])
    return "1"


def slug_to_name(slug: str) -> str:
    cleaned = slug.strip("/").split("/")[-1]
    cleaned = cleaned.replace("-", " ").replace("_", " ").strip()
    return " ".join(part.capitalize() for part in cleaned.split())


def parse_hitchhiker_html(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    items: list[dict[str, str]] = []
    seen: set[str] = set()

    for anchor in soup.select('a[href*="/our-beers/"]'):
        href = anchor.get("href", "")
        text = re.sub(r"\s+", " ", anchor.get_text(" ", strip=True)).strip()
        if not text:
            text = slug_to_name(href)
        if len(text) < 3:
            continue
        lowered = text.casefold()
        if any(
            token in lowered
            for token in ["our beer", "tap room", "hitchhiker brewing", "scroll for current"]
        ):
            continue
        key = normalize_name(text)
        if key in seen:
            continue
        seen.add(key)
        items.append({"name": text, "style": None, "abv": None})
    return items


def parse_pdf_menu_text(text: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        if len(line) < 3:
            continue
        if any(token in line.casefold() for token in ["lager", "pils", "ipa", "sour", "%"]):
            parts = [part.strip() for part in re.split(r"[\-|•]", line) if part.strip()]
            items.append(
                {
                    "name": parts[0],
                    "style": parts[1] if len(parts) > 1 else None,
                    "abv": line,
                }
            )
    return items


def as_entries(
    brewery_id: str,
    brewery_name: str,
    source_type: str,
    source_url: str,
    items: list[dict[str, str]],
    scraped_at: str,
) -> list[BeerEntry]:
    entries: list[BeerEntry] = []
    for item in items:
        name = (item.get("name") or "").strip()
        if not name:
            continue
        entries.append(
            BeerEntry(
                breweryId=brewery_id,
                breweryName=brewery_name,
                name=name,
                normalizedName=normalize_name(name),
                style=item.get("style"),
                abv=parse_abv(item.get("abv")),
                untappdRating=None,
                sourceType=source_type,
                sourceUrl=source_url,
                scrapedAt=scraped_at,
                active=True,
            )
        )
    return entries


def dedupe(entries: list[BeerEntry]) -> list[BeerEntry]:
    by_name: dict[str, BeerEntry] = {}
    for entry in entries:
        if entry.normalizedName not in by_name:
            by_name[entry.normalizedName] = entry
    return sorted(by_name.values(), key=lambda item: (item.breweryId, item.normalizedName))


def scrape_brewery(brewery_id: str, name: str, url: str, rule: str) -> tuple[list[BeerEntry], str]:
    scraped_at = now_iso()
    raw_text = ""
    source_type = "website"
    items: list[dict[str, str]] = []

    try:
        if rule == "pdf":
            source_type = "pdf"
            raw_text = fetch_pdf_text(url)
            items = parse_old_thunder_pdf(raw_text)
        else:
            raw_text = fetch_text(url)
            if brewery_id == "late-addition":
                parsed = parse_late_addition_html(raw_text)
            elif brewery_id == "grist-house":
                parsed = parse_grist_house_html(raw_text)
            elif brewery_id == "dancing-gnome":
                parsed = parse_dancing_gnome_html(raw_text)
            elif brewery_id == "golden-age":
                parsed = parse_golden_age_html(raw_text)
            elif brewery_id == "four-points":
                parsed = parse_four_points_html(raw_text)
            elif brewery_id == "hitchhiker":
                parsed = parse_hitchhiker_html(raw_text)
            elif brewery_id == "abjuration":
                location_id = abjuration_location_id(raw_text)
                partial_url = urljoin(url, f"PartialView/OnTap?locationId={location_id}")
                partial_text = fetch_text(partial_url)
                parsed = parse_abjuration_on_tap_html(partial_text)
                raw_text = (
                    f"{raw_text}\n\n"
                    f"<!-- Abjuration OnTap partial: {partial_url} -->\n"
                    f"{partial_text}"
                )
            else:
                parsed = parse_html_taplist(raw_text)

            if brewery_id == "grist-house" and has_untappd_embed(raw_text):
                source_type = "untappd"
            if brewery_id == "dancing-gnome":
                source_type = "merged"
            if brewery_id == "abjuration" and parsed:
                source_type = "widget"
            items = parsed
    except Exception as exc:  # noqa: BLE001
        raw_text = f"FETCH_ERROR: {exc}"

    if not items:
        items = SAMPLE_MENU[brewery_id]
        source_type = f"{source_type}_fallback"

    if brewery_id == "hitchhiker" and not items:
        items = [{"name": beer, "style": None, "abv": None} for beer in HITCHHIKER_BASELINE]
        source_type = "baseline"

    entries = dedupe(as_entries(brewery_id, name, source_type, url, items, scraped_at))
    return entries, raw_text


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    all_entries: list[BeerEntry] = []
    for brewery in BREWERIES:
        entries, raw_text = scrape_brewery(brewery.id, brewery.name, brewery.url, brewery.rule)
        all_entries.extend(entries)
        raw_path = RAW_DIR / f"{brewery.id}-{date.today().isoformat()}.txt"
        raw_path.write_text(raw_text, encoding="utf-8")

    latest_payload = {
        "generatedAt": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "entries": [entry_to_dict(entry) for entry in all_entries],
    }

    latest_path = DATA_DIR / "latest.json"
    latest_path.write_text(json.dumps(latest_payload, indent=2), encoding="utf-8")

    history_path = HISTORY_DIR / f"{date.today().isoformat()}.json"
    history_path.write_text(json.dumps(latest_payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
