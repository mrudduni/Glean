# Recommended stack

> Superseded on 2026-11-14 by [stack_v2.md](stack_v2.md). This file stays as the record of version 1 and its dependency research.

This file gives one stack for the hackathon demo (14 to 15 November 2026) and how it grows into the long-term portfolio app. Details and sources for each choice are in the other files in this folder: `backend.md`, `frontend.md`, `llm_layer.md`, `field_boundaries.md`, `misc_apis.md`, `deployment.md`, and `quality_tooling.md`.

## Architecture in one paragraph

A pure-Python package, `fieldshift_core`, holds all science and data access: adapters for NASA POWER, MPC and CMR STAC (HLS, MODIS, NASADEM), `earthaccess` (SMAP, IMERG, ECOSTRESS, GRACE), SSURGO through SDA, and CSB or FTW field polygons. It builds an evidence bundle per strategy, scores strategies with transparent rules and TOPSIS, and returns typed Pydantic objects. A thin FastAPI app exposes that package as a JSON API. A React, Vite, and TypeScript app with MapLibre shows the field, three or more strategies, charts, and evidence chips. An optional LLM step turns each evidence bundle into plain-language explanations, validated against the bundle, with a template fallback.

## Hackathon demo stack

| Layer | Choice |
| --- | --- |
| Language and env | Python 3.12 with uv; Node LTS with npm |
| Core engine | `fieldshift_core` (Pydantic models, xarray, rioxarray, geopandas, pymcdm) |
| Data access | httpx, pystac-client with `planetary-computer` signing, earthaccess, direct SDA SQL |
| Cache | diskcache on local disk, outside the repo |
| Storage | GeoParquet files queried with DuckDB |
| API | FastAPI with Uvicorn, run locally for the recording |
| Frontend | React, Vite, TypeScript, MapLibre GL JS, Terra Draw, Observable Plot, i18next (English plus one more language) |
| Basemap | OpenFreeMap vector tiles plus NASA GIBS true colour |
| Field polygons | CSB for the US demo field; FTW 2025 for a non-US example if time allows |
| Explanations | Claude API (`claude-opus-5-5`) with structured outputs and evidence-ID validation; template fallback |
| Public link | Static build on GitHub Pages reading precomputed JSON for 2 or 3 demo fields |
| Quality | ruff, pytest with recorded fixtures, one Playwright smoke test |

Fallback if no one on the team writes React: build the demo UI in Solara or Streamlit over the same `fieldshift_core` package (see `frontend.md`). The 30-second video can be recorded from either.

Why this shape for a 2-day event: the public link is static, so no cold start or API quota can break a judge's visit, and the video is recorded locally. All required NASA data sources show up as evidence chips, which supports Relevance and Validity.

## Long-term evolution

| Area | Change |
| --- | --- |
| API hosting | FastAPI in Docker on a small paid instance (Render, Fly.io, or Railway) |
| Jobs | arq workers on Valkey for AppEEARS tasks, HLS time series, and refreshes |
| Database | Postgres with PostGIS for saved farms, scenarios, and audit logs; DuckDB stays for read-only reference layers |
| Rasters | Per-farm Zarr v3 stores; COGs served through TiTiler routes mounted in the API; VirtualiZarr for IMERG and SMAP archives |
| Scheduled refresh | GitHub Actions cron (daily or weekly) with "data as of" dates shown in the UI |
| Frontend | PWA with offline last report, PMTiles extract, full i18n (Spanish, Hindi, others reviewed by fluent speakers), accessibility tests with axe |
| LLM | Provider interface so a local open-weight model can run offline; eval set in CI |
| Field boundaries | Click-to-select from CSB and FTW; optional SAM on NAIP for US users |
| Delivery | Printable one-page report first; WhatsApp Cloud API later, with opt-in |
| Science | Add LightGBM with SHAP and AquaCrop-OSPy (see `research/03_domain/open_source.md`) |

## Dependency licence table

All versions from PyPI (`https://pypi.org/pypi/<name>/json`) or npm (`https://registry.npmjs.org/<name>`) on 14 November 2026.

| Dependency | Version | Licence | Phase | Note |
| --- | --- | --- | --- | --- |
| FastAPI | 0.162.7 | MIT | Both | |
| Uvicorn | 0.54.0 | BSD-3-Clause | Both | |
| Pydantic | 2.14.3 | MIT | Both | |
| httpx | 0.28.1 | BSD-3-Clause | Both | Last release December 2024 |
| xarray | 2026.9.0 | Apache-2.0 | Both | |
| rasterio | 1.5.2 | BSD-3-Clause | Both | Needs Python 3.12 or later |
| geopandas | 1.2.0 | BSD-3-Clause | Both | |
| pyogrio | 0.13.0 | MIT | Both | |
| DuckDB | 2.0.0 | MIT | Both | |
| zarr | 3.4.2 | MIT | Both | |
| pystac-client | 0.9.1 | Apache-2.0 | Both | |
| planetary-computer | 1.0.0 | MIT | Both | Last release July 2023 |
| earthaccess | 0.19.0 | MIT | Both | Version from `research/03_domain/open_source.md` |
| diskcache | 5.6.3 | Apache-2.0 | Demo | Last release August 2023 |
| anthropic | 2.8.0 | Apache-2.0 | Both | Key stays server-side |
| titiler.core | 2.4.0 | MIT | Long term | |
| rio-tiler | 9.4.13 | BSD-3-Clause | Long term | |
| arq | 0.28.0 | MIT | Long term | |
| Valkey server | n/a | BSD-3-Clause | Long term | Used instead of Redis |
| psycopg | 3.3.9 | LGPL-3.0-only | Long term | Fine when unmodified |
| SQLAlchemy / GeoAlchemy2 | 2.1.8 / 0.21.0 | MIT | Long term | |
| PostGIS | n/a | GPL-2.0 or later (not confirmed) | Long term | Separate server, no code copied |
| VirtualiZarr | 2.8.0 | Apache-2.0 | Long term | |
| react | 19.3.1 | MIT | Both | |
| vite | 8.3.8 | MIT | Both | |
| typescript | 7.0.2 | Apache-2.0 | Both | Pin 5.x if tools lag |
| maplibre-gl | 6.18.0 | BSD-3-Clause | Both | |
| terra-draw | 1.39.0 | MIT | Both | |
| @observablehq/plot | 0.6.19 | ISC | Both | |
| i18next / react-i18next | 27.1.1 / 18.0.1 | MIT | Both | |
| @tanstack/react-query | 5.107.1 | MIT | Both | |
| pmtiles (JS) | 4.5.0 | BSD-3-Clause | Long term | |
| vite-plugin-pwa | 2.0.0 | MIT | Long term | |
| pytest | 9.2.0 | MIT | Both | |
| hypothesis | 6.170.15 | MPL-2.0 | Both | Dev only |
| ruff | 0.17.5 | MIT | Both | |
| pyright | 1.1.414 | MIT | Both | |
| playwright | 1.65.2 | Apache-2.0 | Both | |
| uv | 0.13.8 | MIT OR Apache-2.0 | Both | |

Data and service licences to list in the submission: OpenStreetMap (ODbL) through OpenFreeMap, FTW predictions (CC-BY-4.0), Open-Meteo data (CC BY 4.0) if used, NASS CDL and CSB (public domain per NASS), NASA data (cite each dataset), and the Claude API (service, not a dependency licence).

Flagged and excluded: Redis server 8+ (RSALv2, SSPLv1, or AGPLv3), pyDecision (GPL-3.0), Open-Elevation code (GPL-2.0), and Esri basemaps (proprietary terms, key needed). PCSE (EUPL) needs a licence review before adoption.

## Top 5 technical risks

1. Data access fails during the demo window. NASA, USDA SDA, and MPC endpoints can be slow, down, or need Earthdata app approvals. Mitigation: precompute demo fields, cache every response, record fixtures, and show "data as of" dates. The public link reads static JSON.
2. LLM explanations state things the evidence does not support. That would hurt Validity and farmer trust. Mitigation: structured outputs with evidence IDs, server checks on IDs and numbers, a template fallback, clear labelling, and a small eval set.
3. Spatial scale mismatch. IMERG (0.1 degree), SMAP (9 to 36 km), and GRACE (about 300 km native) are far coarser than a field, while CSB and FTW polygons are 10 to 30 m. Values could look more precise than they are. Mitigation: show each dataset's native resolution next to each value, use buffers or regional averages honestly, and list these as data gaps.
4. Free-tier and terms changes. Hugging Face already moved Docker Spaces to paid plans, Render free Postgres expires after 30 days, GitHub disables idle scheduled workflows after 60 days, and Nominatim and OpenTopography forbid patterns a naive app would use. Mitigation: static-first hosting, no dependency on Earth Engine, Valkey instead of Redis, our own proxy and cache for geocoding, and a short "terms we rely on" list reviewed each quarter.
5. Scope creep across two stacks. A Python engine plus a React app doubles the surface for a small team in two days. Mitigation: freeze the Pydantic contract between engine and UI first, generate TypeScript types from the OpenAPI schema, keep the Python-only UI as a fallback, and limit the demo to one US field with three strategies done well.

## Open questions for the team

- Does anyone on the team write React and TypeScript confidently? This decides React versus Solara for the demo.
- Which demo field and county? It drives which CSB and SSURGO extracts to prepare.
- Is a runtime LLM in the product acceptable to the team given the SI rules? The rules do not address it directly (not confirmed).
- Which second language for the demo: Spanish or Hindi?
