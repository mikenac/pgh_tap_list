# Report Format

Each generated report must include:

1. Metadata
- Report date
- Previous snapshot date
- Generated timestamp

2. What changed this week
- Additions
- Removals
- Style changes
- Material rating changes (enrichment-only)

3. Full lineup by brewery
- Beer name
- Style
- ABV
- Untappd rating (approximate, nullable)
- Source attribution

4. Style watches
- Czech Lager Watch
- European Lager Watch
- Sour Watch

Rules:
- Markdown tables must be deterministic.
- All facts must come from structured JSON produced by deterministic scripts.
- AI narrative text must not be used as source-of-truth data.
