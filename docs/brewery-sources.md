# Brewery Sources and Caveats

## Global rules

- Always prefer embedded live taplist widgets over static marketing pages.
- If an Untappd menu/widget is embedded, use that as the primary source of truth.
- Normalize brewery, beer name, style, ABV, source URL, and scrape timestamp.
- Store the raw source payload or extracted raw text for debugging.
- Do not let AI invent beers, styles, or ratings.
- AI may summarize only structured JSON produced by deterministic scrapers.
- For each beer, optionally enrich with Untappd rating using brewery + beer name.
- Mark ratings as approximate and nullable.

## Tracked breweries

### Grist House — Millvale
URL: https://gristhouse.com/millvale/

Rules:
- Auto-detect embedded Untappd menu.
- Use embedded Untappd as the primary source of truth.
- Do not rely only on visible website text if the Untappd embed is present.

### Dancing Gnome
URL: https://dancinggnomebeer.com/location/1025-main/#on-tap

Rules:
- Combine the website On Tap page with the Untappd venue taplist.
- Build the most complete current tap list from both sources.
- Deduplicate by normalized beer name.
- If website and Untappd disagree, keep source attribution and prefer the more recently updated/live-looking source.

### Four Points
URL: https://fourpointsbrewing.com/draftlist

Rules:
- Scrape the draft list page.
- Watch especially for Czech lagers and European-style lagers.

### Late Addition
URL: https://lateadditionbrewing.com/#beers

Rules:
- Scrape the beers section.
- Watch for European-style lagers, saisons, blends, and sours.

### Hitchhiker
URL: https://hitchhiker.beer

Rules:
- Scrape current taplist from the site or embedded live menu if present.
- Compare against the known baseline below when no prior snapshot exists.

Baseline list:
Bane of Existence; Double Dry Hopped Double Bane of Existence; Slow Bane; Drinky & the Brain; High Hop; So Soft; 16oz Trip to Ireland; Triple Thick; Point of Confusion; YoRazberry; True; Airwave; Double Airwave; Shadow Walker; You’ll Shoot Your Eye Out; Mango Bottle Service; mmHmmm Raspberry Grape Strawberry; Subsurface Blueberry Peach; Whole Punch Blueberry Pie; Sprout; People-Watching.

### Old Thunder
URL: https://www.oldthunderbrewing.com/_files/ugd/1dde72_2d9ec5c4e9574e7bb3f6c65d4f033297.pdf

Rules:
- Source is a PDF.
- Download and parse PDF text.
- If text extraction is weak, render/screenshot pages and parse visually.
- Track full lineup and highlight lagers/pilsners.

### Abjuration
URL: https://www.abjurationbrewing.com

Rules:
- Auto-detect embedded taplist widgets if present.
- Strong sour program; highlight all sour/fruited/kettle sour/parfait/ice cream sour styles.

### Golden Age
URL: https://www.goldenagebeer.com/menu

Rules:
- Scrape menu page.
- Strong lager focus; highlight Czech, German, Austrian, Polish, and other European-style lagers.