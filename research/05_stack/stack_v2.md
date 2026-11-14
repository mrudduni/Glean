# Stack v2: a production-grade design

This file replaces the stack in `recommended_stack.md`. Version 1 was too thin: a static site, a local-only API, a disk cache, one LLM vendor, and a demo limited to one US field. Version 2 is a live system built the way a real product would be, while it keeps a safe fallback for judging. Versions and licences were checked on 2026-11-14 against PyPI (`https://pypi.org/pypi/<name>/json`), npm (`https://registry.npmjs.org/<name>/latest`), and GitHub, unless a row says otherwise.

## What changed from version 1

| Area | Version 1 | Version 2 | Why |
|---|---|---|---|
| Hosting | Static JSON on GitHub Pages | Live API on Cloud Run (Mumbai region) plus a static fallback | Judges and farmers can draw any field, not only three canned ones |
| Data | Fetched on demand, cached on disk | Precomputed "region packs" built by a Dagster pipeline, stored in R2, plus live point APIs | Fast and reliable for a demo, still real data, with lineage |
| Database | GeoParquet and DuckDB only | Postgres with PostGIS (Neon), plus DuckDB over GeoParquet for reference layers | Saved farms, scenarios, and an evidence ledger need a real database |
| Jobs | Valkey and arq | procrastinate, a task queue that runs inside Postgres | One less service to run and pay for |
| Science | Rules and TOPSIS | Three model tiers, Monte Carlo over 25 climate years, conformal intervals, rank stability | The challenge video asks us to "make uncertainty visible" |
| LLM | Claude only | Provider-agnostic. Grok is the default and Claude the fallback | The team has a Grok key |
| Evidence checks | Server compares cited IDs after the fact | Cited IDs are an `enum` in the output schema, so the model cannot cite an ID we did not compute. The server then checks every number | Guarantees from the API, not only from our own checks |
| Region | One US field | Haryana (Karnal, Kurukshetra, Kaithal) first, with Iowa and Kansas as US controls | Matches the team's direction and shows the tool works outside the US |
| Frontend | React, MapLibre, Observable Plot | React, TanStack Router and Query, Tailwind with shadcn/ui, MapLibre with deck.gl, ECharts | Polished UI, raster layers, and uncertainty bands |

## Architecture

```
                    Farmer or judge (browser, phone)
                                 |
              Cloudflare Pages: React SPA (PWA, i18n)
                                 |  typed client generated from OpenAPI
                                 v
        Cloud Run service: FastAPI  ----->  LLM gateway (Grok, Claude fallback)
          |          |          |
          |          |          +--> live point APIs: NASA POWER, SDA, SoilGrids,
          |          |               Open-Meteo, CropScape (cached, retried)
          |          v
          |     Postgres + PostGIS (Neon): farms, scenarios, runs,
          |     evidence ledger, task queue (procrastinate)
          v
     Cloudflare R2: region packs (Zarr v3, COG, GeoParquet)
          ^
          |  writes
     Dagster pipeline (Cloud Run Jobs or GitHub Actions)
       pulls SMAP, IMERG, HLS, MODIS, ECOSTRESS, GRACE, SRTM, CHIRPS,
       WorldCereal, FTW boundaries through earthaccess, CMR-STAC, and
       Planetary Computer, then harmonises them to one grid per region
```

### The four Python packages (one uv workspace)

| Package | Job | Depends on |
|---|---|---|
| `fieldshift-domain` | Pure types and rules: crops, seasons (kharif, rabi, zaid, and US seasons), rotations, constraints, evidence records. No I/O. | Pydantic only |
| `fieldshift-data` | One adapter per source. Each adapter returns values plus a provenance record (dataset, version, CMR concept ID, native resolution, time range, retrieval time). Retries, rate limits, and caching live here. | httpx, earthaccess, pystac-client, odc-stac, rioxarray |
| `fieldshift-engine` | Water balance, crop models, soil health, ML, uncertainty, and ranking. Takes domain objects in and returns results with evidence IDs. | numpy, xarray, aquacrop, lightgbm, mapie, shap, pymcdm |
| `fieldshift-api` | FastAPI app, database models, task queue, LLM gateway. | FastAPI, SQLAlchemy, GeoAlchemy2, procrastinate, openai SDK |

The pipeline (`fieldshift-pipeline`, Dagster) reuses `fieldshift-data` and `fieldshift-engine`, so the precompute and the live path run the same code.

## The science engine in three tiers

The video asks teams to "compare rotations, reveal trade-offs, understand risk, make uncertainty visible". Each tier answers part of that.

| Tier | Method | Output per rotation | Runs |
|---|---|---|---|
| 1. Transparent core | FAO-56 dual-Kc daily soil water balance, run over each of the last 25 years of NASA POWER weather (CHIRPS or IMERG rain where better) on the field's soil (SSURGO in the US, SoilGrids elsewhere) | Distribution of irrigation need, water stress days, deep drainage, and bare-soil days | Live, under one second per field |
| 2. Process model | AquaCrop-OSPy for the main grain crops, with the same weather years | Yield distribution under water limits | Live for the top strategies, or queued |
| 3. Statistical model | LightGBM trained on district yields (India) and county yields (US) with NASA features (SMAP root-zone anomaly, IMERG totals, heat days, NDVI peak). MAPIE conformal intervals around each prediction. SHAP values for drivers | Yield anomaly with a calibrated 80 percent interval, plus the top drivers | Trained offline, served live |

Soil health sits beside the tiers: RUSLE erosion with C factors per rotation, the NRCS Soil Conditioning Index, and a simple soil carbon model (ICBM or RothC). The method and coefficient sources are in `research/03_domain/soil_health_methods.md`.

### How uncertainty becomes visible

- Every output is a distribution over 25 climate years, not one number. The UI shows the median with a band from the 10th to the 90th percentile.
- Scenario sliders shift the climate inputs (for example, rain down 20 percent or temperature up 2 C) and rerun tier 1 live.
- Rank stability: we draw farmer weights at random around the chosen values 1,000 times and rerun TOPSIS. The UI then says how often each strategy ranks first, for example "first in 71 percent of draws".
- Resolution badges: each value shows the native resolution of its source (SMAP at 9 km, IMERG at about 11 km, GRACE at about 300 km). A coarse source next to a small field carries a visible warning.
- Each LightGBM prediction carries a conformal interval with stated coverage, checked on held-out years.

## The evidence ledger and the LLM layer

### Evidence ledger

Every number the tool shows is a row in Postgres. Each row records an ID, the value, unit, uncertainty, source dataset and version, CMR concept ID where one exists, native resolution, time window, method, and the code version. A strategy card is just a set of ledger IDs. The "why", "evidence", "gains", "gaps", and "risks" sections in the challenge map to tagged ledger rows.

### LLM gateway

- The OpenAI Python SDK (3.51.0, Apache-2.0) talks to any OpenAI-compatible endpoint. Grok is the default: base URL `https://api.x.ai/v1`, model `grok-4.7`, with a 500k token context, at $2.00 per million input tokens and $6.00 per million output tokens. Source: https://docs.x.ai/developers/models
- xAI structured outputs guarantee that a response matches the JSON schema we send. They support `enum`, and enums are fully enforced. Source: https://docs.x.ai/developers/model-capabilities/text/structured-outputs
- We build the schema per request, and the `evidence_ids` field is an `enum` of that request's ledger IDs. The model therefore cannot cite evidence we did not compute. A second server check confirms that every number in the text matches its cited ledger row within rounding. Any failure falls back to a template sentence.
- Claude is the fallback provider behind the same interface. A template-only mode works with no key at all.
- The same gateway translates the final cards into Hindi and Punjabi. A fluent speaker on the team should review the demo strings.
- xAI also offers speech-to-text and text-to-speech (https://docs.x.ai/developers/models). It could later power voice input and read-aloud cards. Hindi and Punjabi support is not confirmed.
- Keys stay on the server in `XAI_API_KEY` and `ANTHROPIC_API_KEY`, set as environment variables from Secret Manager. They never ship to the browser and never enter git.
- Every generated sentence carries a "generated by AI from the evidence above" label. The Space Apps rules do not address an LLM inside the product (see `research/02_hackathon/rules_judging.md`), so the label keeps us safe either way.

## Frontend

| Need | Choice | Version | Licence |
|---|---|---|---|
| Framework | React with Vite and TypeScript | react 19.3.1, vite 8.3.8 | MIT |
| Routing and server state | TanStack Router and TanStack Query | 1.170.46, 5.107.1 | MIT |
| Local state | Zustand | 5.1.0 | MIT |
| Styling and components | Tailwind CSS with shadcn/ui | 4.3.5, 4.23.0 | MIT |
| Base map | MapLibre GL JS | 6.18.0 | BSD-3-Clause |
| Data layers on the map | deck.gl (raster tiles, heatmaps, field polygons) | 9.4.1 | MIT |
| Field drawing | Terra Draw | 1.39.0 | MIT |
| Geometry in the browser | Turf | 7.4.0 | MIT |
| Charts with uncertainty bands | Apache ECharts | 6.1.0 | Apache-2.0 |
| API client | Generated from the FastAPI OpenAPI schema by @hey-api/openapi-ts, with zod validation | 0.99.0, zod 4.6.7 | MIT |
| Languages | i18next with react-i18next | 27.1.1, 18.0.1 | MIT |
| Offline | vite-plugin-pwa, last report cached | 2.0.0 | MIT |
| Errors | Sentry for React | 11.12.0 | MIT |

Next.js (16.4.6) was considered and rejected. The app needs no server rendering, and a plain SPA on Cloudflare Pages keeps one backend, not two.

### Screens

1. Find your field: search a village or click the map, then pick a boundary from Fields of The World or draw one.
2. Your field today: soil, water, heat, and crop history, each with a resolution badge.
3. Your priorities: sliders for water, income, soil health, and risk, plus constraints (irrigation, equipment, market).
4. Compare strategies: three or more cards side by side (current rotation first), with fan charts, a trade-off radar, and rank stability.
5. Strategy detail: why, evidence, gains, gaps, and risks to check locally, each line linked to a ledger row.
6. Report: a printable and shareable one-page summary in the farmer's language.

## Backend and data

| Need | Choice | Version | Licence |
|---|---|---|---|
| API | FastAPI with Uvicorn and Pydantic 2 | 0.162.7, 0.54.0, 2.14.3 | MIT, BSD-3-Clause, MIT |
| ORM and migrations | SQLAlchemy 2 with GeoAlchemy2 and Alembic | 2.1.8, 0.21.0, 1.20.1 | MIT |
| Database | Postgres with PostGIS on Neon | n/a | Neon free plan: 100 CU-hours a month per project, 1 GB storage per project. PostGIS installs on any Neon project. https://neon.com/pricing and https://neon.com/docs/extensions/postgis |
| Task queue | procrastinate (runs inside Postgres) | 3.11.0 | MIT |
| Pipeline | Dagster software-defined assets | 1.13.30 | Apache-2.0 |
| Object store | Cloudflare R2, through obstore | obstore 0.12.1 | R2 free tier: 10 GB-month storage, 1 million Class A and 10 million Class B operations a month, free egress. https://developers.cloudflare.com/r2/pricing/ |
| Rasters | xarray, rioxarray, odc-stac, dask, Zarr v3 | 2026.9.0, 0.24.0, 0.5.3, 2026.8.0, 3.4.2 | Apache-2.0, Apache-2.0, Apache-2.0, BSD-3-Clause, MIT |
| Tables | Polars and DuckDB | 2.1.0, 2.0.0 | MIT |
| Data contracts | pandera schemas on every adapter output | 0.36.0 | MIT |
| NASA access | earthaccess, pystac-client, planetary-computer | 0.19.0, 0.9.1, 1.0.0 | MIT, Apache-2.0, MIT |
| Resilience | tenacity retries with per-source rate limits | 9.2.1 | Apache-2.0 |
| Logging | structlog with JSON output | 26.1.0 | MIT or Apache-2.0 |
| Errors | sentry-sdk | 2.75.0 | MIT |
| Models | aquacrop, lightgbm, mapie, shap, pymcdm | 3.1.0, 4.7.0, 1.6.0, 0.54.1, 1.4.0 | MIT, MIT (not rechecked today), BSD-3-Clause, MIT, MIT |

pyDecision is GPL-3.0 (PyPI, checked 2026-11-14), so pymcdm does the ranking instead.

### Region packs

A region pack is everything slow about a region, computed once. It holds the harmonised daily weather for 25 years, SMAP and IMERG climatologies, HLS NDVI time series per field polygon, ECOSTRESS ET summaries, the GRACE groundwater trend, SRTM slope, soil layers, and crop-history maps. Dagster builds each pack as a set of assets with lineage, writes it to R2, and records its hash in the evidence ledger. The live API then answers a new field in a second or two by reading the pack and calling only fast point APIs.

First packs: the Karnal, Kurukshetra, and Kaithal districts of Haryana; Story County, Iowa; and Finney County, Kansas.

## Deployment

| Piece | Where | Free tier fact |
|---|---|---|
| Frontend | Cloudflare Pages | Static hosting; see `deployment.md` |
| API | Google Cloud Run service in `asia-south1` (Mumbai), container from GitHub Actions | Request-based billing: 2 million requests, 180,000 vCPU-seconds, and 360,000 GiB-seconds free each month. https://cloud.google.com/run/pricing |
| Pipeline runs | Cloud Run Jobs, or GitHub Actions on a schedule | Jobs: 240,000 vCPU-seconds and 450,000 GiB-seconds free each month. Same source |
| Database | Neon | Above |
| Object store | Cloudflare R2 | Above |
| Secrets | Google Secret Manager for the API; GitHub encrypted secrets for CI | Earthdata, xAI, and Anthropic keys never enter git |
| Local development | Docker Compose with `postgis/postgis` and MinIO, so local mirrors production | n/a |
| Judge fallback | A static snapshot of the three demo fields on Cloudflare Pages, switched on if the API is down | n/a |

Cloud Run needs a billing account with a card, even inside the free tier. If the team cannot add one, Fly.io or Render can host the same container (see `deployment.md` for their current terms).

## Quality and engineering practice

- One uv workspace for Python, and pnpm for the frontend. Docker images are built in CI.
- ruff for lint and format, and pyright in strict mode on `fieldshift-domain` and `fieldshift-engine`.
- pytest with these layers:
  - Unit tests on every formula, checked against the FAO-56 worked examples.
  - Property tests with hypothesis. The water balance must close every day: rain plus irrigation equals ET plus drainage plus runoff plus the change in storage.
  - Adapter tests that replay recorded responses with pytest-recording, so CI never calls NASA.
  - pandera checks on every DataFrame between layers.
- Playwright end-to-end tests on the three demo fields, plus an axe accessibility check.
- GitHub Actions on every push runs lint, types, tests, a licence scan, and a build. Dependabot and CodeQL stay on.
- OpenTelemetry traces through FastAPI and the adapters, with errors in Sentry. Each run's trace ID is stored with its ledger rows, so any number on screen can be traced to the request that made it.

## What we build in the hackathon window

The event closes on 15 November at 23:59 local time. Two days do not fit the whole design, so we build the spine of it:

1. `fieldshift-domain` and the evidence ledger schema, first and frozen.
2. Adapters for NASA POWER, SMAP (L4 root zone), IMERG, MODIS or HLS NDVI, SoilGrids, and SSURGO, with recorded fixtures.
3. Tier 1 water balance over 25 years, RUSLE, and TOPSIS with rank stability.
4. The FastAPI app on Cloud Run, the Neon database, and one region pack for Karnal built by a plain script. Dagster comes later.
5. The four core screens, plus the LLM cards on Grok with the enum guard and the template fallback.
6. The static fallback snapshot, and the 30-second video.

After the event: AquaCrop and LightGBM tiers, the Dagster pipeline, more regions, the PWA, voice, and the full test suite.

## Top risks and how this design handles them

1. NASA services or Earthdata Login fail during judging. Region packs plus the static fallback mean the demo never depends on a live NASA call.
2. The LLM states something false. The enum guard, the number check, the template fallback, and the AI label together contain this.
3. Small fields against coarse data. Resolution badges and per-value warnings make this a visible gap, not a hidden one.
4. Free tiers change. Every piece runs in Docker, so we can move hosts in an hour, and the README lists every term we rely on.
5. Too much stack for the team. The four-package split lets people work in parallel. If the frontend slips, the API docs page and the printable report still show the work.

## Sources

- https://docs.x.ai/developers/models
- https://docs.x.ai/developers/model-capabilities/text/structured-outputs
- https://docs.x.ai/overview
- https://neon.com/pricing
- https://neon.com/docs/extensions/postgis
- https://developers.cloudflare.com/r2/pricing/
- https://cloud.google.com/run/pricing
- PyPI JSON API and npm registry entries for each package named above, read on 2026-11-14
- https://api.github.com/repos/opendatacube/odc-stac (Apache-2.0), https://api.github.com/repos/developmentseed/obstore (MIT), https://api.github.com/repos/dagster-io/dagster (Apache-2.0), https://api.github.com/repos/valkey-io/valkey (BSD-3-Clause)
- The challenge video: https://www.youtube.com/watch?v=cF0U2WXsM7o
