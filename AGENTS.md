# AGENTS.md

## Project

This repo builds a Pittsburgh brewery taplist tracker.

Before making scraping, data model, or report-generation changes, read:

- `docs/brewery-sources.md`
- `docs/data-model.md`
- `docs/scraping-rules.md`

## Non-negotiable rules

- Do not fabricate taplist data.
- Scrapers produce structured JSON first.
- AI only summarizes structured JSON.
- Every beer should include source attribution.
- Prefer live embedded Untappd/taplist widgets when available.
- Preserve historical snapshots for weekly comparison.
- The weekly report must include:
  - full lineup for each brewery
  - additions
  - removals
  - style changes
  - Czech lager watch
  - European lager watch
  - sour watch
  - approximate Untappd ratings when available