# Testing, quality, and reproducible environments

This file covers the tools that keep Field Shift correct and reproducible on Windows and Linux. Versions and licences come from the PyPI JSON API (`https://pypi.org/pypi/<name>/json`) and the npm registry (`https://registry.npmjs.org/<name>`) on 14 November 2026.

## Python tools

| Tool | Version (date) | Licence | Role |
| --- | --- | --- | --- |
| pytest | 9.2.0 (2026-10-27) | MIT | Test runner |
| pytest-cov | 7.1.0 (2026-03-21) | MIT | Coverage |
| hypothesis | 6.170.15 (2026-11-06) | MPL-2.0 | Property-based tests |
| playwright (Python) | 1.65.2 (2026-11-14) | Apache-2.0 | Browser tests |
| pytest-playwright | 0.10.0 (2026-10-08) | Apache-2.0 | pytest plugin for Playwright |
| ruff | 0.17.5 (2026-11-12) | MIT | Linter and formatter |
| mypy | 2.4.1 (2026-10-28) | MIT | Type checker |
| pyright | 1.1.414 (2026-09-10) | MIT | Type checker (PyPI wrapper of the Node tool) |
| pre-commit | 4.7.0 (2026-10-12) | MIT | Git hook runner |
| fakeredis | 2.40.0 (2026-10-14) | BSD-3-Clause | In-memory Redis or Valkey for tests |
| uv | 0.13.8 (2026-11-12) | MIT OR Apache-2.0 | Package and environment manager |

## JavaScript tools

| Tool | Version (date) | Licence | Source |
| --- | --- | --- | --- |
| vitest | 5.1.0 (2026-11-02) | MIT | https://registry.npmjs.org/vitest |
| @playwright/test | 1.65.1 (2026-11-13) | Apache-2.0 | https://registry.npmjs.org/@playwright/test |
| eslint | 10.15.0 (2026-11-13) | MIT | https://registry.npmjs.org/eslint |
| @biomejs/biome | 2.6.7 (2026-11-11) | MIT OR Apache-2.0 | https://registry.npmjs.org/@biomejs/biome |

Biome replaces ESLint and Prettier with one fast tool, at the cost of fewer plugins. For a small team, Biome is simpler.

## What to test

- Science functions (GDD, FAO-56 ETo, nitrogen credits, RUSLE, TOPSIS) against worked examples from the cited sources in `research/03_domain/agronomy_rotations.md`. Each test names its source URL.
- Properties with hypothesis: scores stay in range, TOPSIS ranks do not change when all weights scale by a constant, adding a strictly better strategy never lowers the best score, and unit conversions round-trip.
- Data adapters with recorded responses. Save small real responses from POWER, SDA, and STAC as test fixtures (a few KB each) and test parsing offline. Mark live calls with `@pytest.mark.live` and run them only on a schedule.
- LLM layer: schema validation, evidence-ID checks, and the number-matching guard with fixed model outputs. Do not call the API in unit tests.
- End to end with Playwright: load a demo field, change a priority weight, see the ranking update, open an evidence chip. Run in CI against the static build.
- Accessibility: run axe-core inside Playwright (`@axe-core/playwright`, version not checked) on the main pages.

## Type checking

Use pyright in strict mode on `fieldshift_core` and basic mode elsewhere, or mypy if the team prefers. Pydantic v2 and FastAPI work well with both. xarray and rasterio types are partial, so allow `Any` at those edges.

## Pre-commit hooks

Run ruff (lint and format), a type check on changed files, a secrets scanner (for example gitleaks or detect-secrets, versions not checked), and a large-file check that blocks files over a few MB. The secrets scanner matters because `CLAUDE.md` forbids committing Earthdata tokens and `.netrc` files.

## Reproducible environments

### uv (recommended default)

uv manages Python versions, virtual environments, and a cross-platform `uv.lock`. It installs from PyPI wheels. The geospatial stack now ships Windows wheels with bundled native libraries: on PyPI we found `win_amd64` wheels for rasterio 1.5.2, pyproj 3.8.0, pyogrio 0.13.0, shapely 2.2.0, and DuckDB 2.0.0 (checked 14 November 2026). rasterio 1.5.2 requires Python 3.12 or later. So `uv` alone works on Windows for our recommended stack.

The `gdal` Python bindings (3.13.3) publish no Windows wheels on PyPI (https://pypi.org/pypi/gdal/json). Avoid `from osgeo import gdal`; use rasterio and pyogrio instead.

### pixi (fallback for GDAL-heavy work)

pixi (https://github.com/prefix-dev/pixi, BSD-3-Clause, release v0.84.2 on 2026-11-10 per the GitHub releases API) installs conda-forge packages with a lock file, and can mix in PyPI packages. Use it if we need full GDAL command-line tools, xESMF (which needs ESMF from conda-forge), or PCSE system libraries on Windows. Note: the `pixi` package on PyPI is an unrelated 2020 upload; install pixi from its own installer or GitHub releases.

Recommendation: start with uv and Python 3.12. Switch the data pipeline to pixi only if xESMF or another conda-only package becomes necessary.

## Continuous integration

GitHub Actions jobs on each push: ruff, type check, pytest without live calls, frontend lint and unit tests, a static build, and Playwright end to end on the build. A separate scheduled job runs live data tests and refreshes demo data (see `deployment.md` for schedule limits).

## Sources

- PyPI JSON API, queried 14 November 2026: https://pypi.org/pypi/{package}/json
- npm registry, queried 14 November 2026: https://registry.npmjs.org/{package}
- pixi releases: https://api.github.com/repos/prefix-dev/pixi/releases/latest
- pixi repository: https://github.com/prefix-dev/pixi
