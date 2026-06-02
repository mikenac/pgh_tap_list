# Data Model

## Goals

The system must:

1. Track current tap lists for each brewery.
2. Track historical tap lists over time.
3. Detect additions, removals, and style changes.
4. Support AI-generated summaries.
5. Preserve source attribution.
6. Never allow AI-generated beer data to become system-of-record data.

---

# Brewery

Represents a tracked brewery.

```json
{
  "id": "dancing-gnome",
  "name": "Dancing Gnome",
  "website": "https://dancinggnomebeer.com",
  "taplistUrl": "https://dancinggnomebeer.com/location/1025-main/#on-tap"
}
```

Fields:

| Field | Description |
|---------|---------|
| id | Stable system identifier |
| name | Display name |
| website | Brewery website |
| taplistUrl | Primary source URL |

---

# Beer

Represents a beer currently or historically observed.

Beer identity is:

```text
brewery_id + normalized_name
```

Example:

```json
{
  "breweryId": "four-points",
  "name": "Ceremonials",
  "normalizedName": "ceremonials"
}
```

---

# TapListEntry

Represents a beer observed on a brewery's board.

```json
{
  "breweryId": "four-points",
  "name": "Ceremonials",
  "style": "Bohemian Pilsner",
  "abv": 5.2,
  "untappdRating": 3.94,
  "source": "draftlist",
  "active": true
}
```

Fields:

| Field | Required |
|---------|---------|
| breweryId | Yes |
| name | Yes |
| style | No |
| abv | No |
| untappdRating | No |
| source | Yes |
| active | Yes |

---

# Source Record

Stores raw scrape information.

```json
{
  "breweryId": "gristhouse",
  "sourceType": "untappd",
  "scrapedAt": "2026-05-29T14:15:00Z",
  "url": "https://gristhouse.com/millvale/",
  "rawPayload": "..."
}
```

Purpose:

- Debugging
- Source validation
- Historical reprocessing

---

# Snapshot

A complete brewery board at a moment in time.

```json
{
  "snapshotDate": "2026-05-29",
  "breweryId": "dancing-gnome",
  "entries": [...]
}
```

Stored at:

```text
data/history/2026-05-29.json
```

---

# Comparison Result

Output of comparing snapshots.

```json
{
  "breweryId": "dancing-gnome",
  "added": [
    "Double Lustra",
    "History Center"
  ],
  "removed": [
    "Cubism"
  ],
  "styleChanges": []
}
```

---

# Weekly Report Model

```json
{
  "generatedAt": "2026-05-29T14:30:00Z",
  "breweryReports": [...],
  "lagerWatch": [...],
  "czechWatch": [...],
  "sourWatch": [...]
}
```

---

# Classification Rules

## Czech Lager

Styles matching:

- Czech Pilsner
- Bohemian Pilsner
- Czech Dark Lager
- Czech Amber Lager
- Czech Pale Lager

---

## European Lager

Styles matching:

- Helles
- Vienna Lager
- German Pils
- Kellerbier
- Festbier
- Märzen
- Dortmunder
- Schwarzbier
- Dunkel
- Bock
- Doppelbock
- Rauchbier
- Czech Lager

---

## Sour

Styles matching:

- Sour
- Fruited Sour
- Kettle Sour
- Berliner Weisse
- Gose
- Wild Ale
- Mixed Culture
- Lambic