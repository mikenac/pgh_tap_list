# Deployment

## GitHub Pages

The public site is deployed with GitHub Pages at:

```text
https://mikenac.github.io/pgh_tap_list/
```

The repository is public because GitHub Pages was not available for this private repository on the current GitHub plan.

## Site Configuration

Astro is configured as a GitHub project Pages site:

- `site`: `https://mikenac.github.io`
- `base`: `/pgh_tap_list`
- `output`: `static`

Because this is a project Pages deployment, internal links must include the `/pgh_tap_list` base path. Avoid hard-coded root links like `/archive/...` or `/`.

## Workflows

### Deploy Pages

`.github/workflows/deploy-pages.yml` deploys the site on:

- pushes to `main`
- manual `workflow_dispatch`

The workflow:

1. Installs Node dependencies with `npm ci`.
2. Builds the Astro site with `npm run build`.
3. Uploads `dist` as a Pages artifact.
4. Publishes with `actions/deploy-pages`.

### Update Taplists

`.github/workflows/update-taplists.yml` runs on Tuesday and Friday at 13:00 UTC, or manually.

The workflow:

1. Installs Python dependencies with uv.
2. Runs the deterministic scrape/enrich/compare pipeline.
3. Runs Python checks and UI smoke tests.
4. Builds and deploys the Astro site.
5. Commits updated `data` and `content` files back to `main` if anything changed.

## uv Index Policy

CI must not use private Python package indexes.

The update workflow installs dependencies with:

```bash
uv sync --group dev --locked --default-index https://pypi.org/simple --no-config
```

This ensures:

- `uv.lock` is used without being rewritten.
- PyPI is the explicit dependency index.
- Runner-level uv config is ignored.
- Private indexes such as `repo.teledev.io` are not used.

## Local Validation

Before changing deployment config, run:

```bash
npm run build
ruby -e 'require "yaml"; YAML.load_file(".github/workflows/deploy-pages.yml")'
ruby -e 'require "yaml"; YAML.load_file(".github/workflows/update-taplists.yml")'
```

For broader validation, also run:

```bash
uv run --group dev ruff check scripts src tests
uv run --group dev pytest
npm run test:ui
```
