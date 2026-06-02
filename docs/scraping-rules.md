# Scraping Rules

## Principles

The system must prioritize accuracy over completeness.

It is acceptable to miss a beer.

It is NOT acceptable to invent a beer.

---

# Source Priority

Priority order:

1. Embedded Untappd menu
2. Embedded taplist widget
3. Brewery draft list page
4. Brewery PDF
5. Static website text

---

# Untappd Detection

Attempt to detect:

```html
untappd.com
business.untappd.com
embedded.untappd.com
```

or embedded iframes.

If present:

- Use Untappd as primary source.
- Record source type as `untappd`.

---

# Dancing Gnome Special Rules

Sources:

- Website On Tap page
- Untappd venue taplist

Process:

1. Scrape both.
2. Normalize beer names.
3. Merge.
4. Deduplicate.
5. Preserve source attribution.

Goal:

Construct the most complete board possible.

---

# Grist House Special Rules

Source:

Embedded Untappd menu.

If Untappd exists:

Ignore visible website list.

Untappd is authoritative.

---

# Old Thunder Special Rules

Source:

PDF menu.

Process:

1. Download PDF.
2. Extract text.
3. If extraction quality poor:
   - Render PDF pages to images.
   - Perform visual extraction.
4. Parse beer list.

Store extracted text for debugging.

---

# Hitchhiker Baseline

If no historical snapshot exists:

Use baseline:

- Bane of Existence
- Double Dry Hopped Double Bane of Existence
- Slow Bane
- Drinky & the Brain
- High Hop
- So Soft
- 16oz Trip to Ireland
- Triple Thick
- Point of Confusion
- YoRazberry
- True
- Airwave
- Double Airwave
- Shadow Walker
- You'll Shoot Your Eye Out
- Mango Bottle Service
- mmHmmm Raspberry Grape Strawberry
- Subsurface Blueberry Peach
- Whole Punch Blueberry Pie
- Sprout
- People-Watching

---

# Name Normalization

Before comparison:

- Trim whitespace
- Collapse repeated spaces
- Convert curly apostrophes
- Convert unicode punctuation
- Remove trailing punctuation

Example:

```text
Double Lustra
double lustra
Double Lustra™

→ double lustra
```

---

# Style Change Detection

Style change occurs when:

```text
same beer name
different style
```

Example:

```text
Old:
Rice Lager

New:
Japanese Rice Lager
```

Flag as:

```json
{
  "beer": "Rice Lager",
  "oldStyle": "Lager",
  "newStyle": "Japanese Rice Lager"
}
```

---

# Untappd Rating Enrichment

Ratings are enrichment only.

Rules:

- Never use ratings to identify beers.
- Never use ratings to determine additions/removals.
- Ratings may be null.

Store:

```json
{
  "untappdRating": 4.12
}
```

---

# Weekly Report Requirements

Every report must contain:

## Brewery Section

- Changes
- Full lineup
- Ratings
- Source attribution

## Czech Lager Watch

Highlight:

- Ceremonials
- Tmavé
- Any new Czech lagers

## European Lager Watch

Highlight:

- Helles
- Pilsner
- Vienna Lager
- Schwarzbier
- Dunkel
- Festbier
- Märzen
- Kellerbier
- Bock variants

## Sour Watch

Highlight:

- Fruited sours
- Mixed culture beers
- Kettle sours
- Berliner Weisse
- Gose

## Rotation Summary

Table:

| Brewery | Added | Removed |