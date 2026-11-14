# Deployment, cost, and licence compatibility

This file compares free hosting for the frontend and the Python backend, scheduled data refresh, containers, and the licence of every recommended dependency. We read the hosts' own docs and pricing pages on 14 November 2026.

## Key constraint

The backend needs Python with GDAL-based wheels (rasterio, pyogrio, pyproj), several hundred MB of memory for raster clipping, and outbound HTTPS to NASA, USDA, and MPC. Edge platforms (Cloudflare Workers, Vercel Edge) cannot run that stack. NASA S3 direct access works only from AWS us-west-2 (`research/01_datasets/nasa/access_tooling.md`), so any free host will use HTTPS.

## Hosting options

| Host | Free tier facts | Python backend? | Cold start | Source |
| --- | --- | --- | --- | --- |
| GitHub Pages | Static only, public repo | No | None | https://pages.github.com/ (size and bandwidth limits not fetched, not confirmed) |
| Cloudflare Workers and static assets | Free plan: 100,000 requests per day; 10 ms CPU per request; files up to 25 MiB; 20,000 files per version | Python Workers exist but cannot load GDAL wheels (not confirmed) | Very low | https://developers.cloudflare.com/workers/platform/limits/ |
| Netlify | Free plan with "300 credit limit / month" covering bandwidth, builds, and functions | Functions are JS or Go (Python not confirmed) | Low | https://www.netlify.com/pricing/ |
| Vercel Hobby | Functions up to 300 s, 2 GB memory, 1 vCPU; 100 MB CLI upload; cannot connect to repos owned by a GitHub organisation | Python functions supported (size limits may block GDAL wheels, not confirmed) | Medium | https://vercel.com/docs/limits |
| Render Free | Web service spins down after 15 minutes idle; 750 free instance hours per month; free Postgres expires after 30 days | Yes, Docker or native Python | Spin-up delay on first request (length not stated on the page) | https://render.com/docs/free |
| Hugging Face Spaces | 16 GB RAM, 2 CPU, 50 GB non-persistent disk by default. Gradio or Docker Spaces now need a paid plan, except up to 2 ZeroGPU Gradio Spaces on free personal accounts. Static Spaces are free. Free Spaces sleep when unused | Only on a paid plan, or ZeroGPU Gradio | Wake-up delay | https://huggingface.co/docs/hub/spaces-overview |
| Fly.io | Pricing page lists pay-as-you-go machines, volumes at $0.15 per GB per month, first 10 GB of snapshots free; no free compute allowance listed | Yes, Docker | Machines can stop when idle | https://fly.io/docs/about/pricing/ |
| Railway | Free plan with $1 of credit per month; Hobby $5 per month including $5 of usage | Yes, Docker or Nixpacks | Low | https://docs.railway.com/reference/pricing/plans |

Notes:

- Vercel's Hobby plan is widely described as for personal, non-commercial use (not confirmed on the pages we fetched; check https://vercel.com/docs/plans/hobby).
- The Render free Postgres expiry makes it unsuitable for stored user data.
- The Hugging Face change matters: older guides say free CPU Spaces run any Docker app, which the current docs contradict.

## Recommended deployment

Hackathon:

1. Precompute results for 2 or 3 demo fields on a laptop or in GitHub Actions. Write JSON reports, small COGs or PNG overlays, and GeoParquet extracts.
2. Build the React app as static files that read those JSON reports. Host on GitHub Pages or Cloudflare static assets. No backend is needed for the public link, so cold starts cannot break the judges' visit.
3. Run the live FastAPI backend on a laptop for the recorded demo, or on Render Free with a "warming up" message in the UI.

Long term:

1. Frontend: static site on Cloudflare or GitHub Pages.
2. API: FastAPI in a Docker image on Render, Fly.io, or Railway (paid tier around $5 to $7 per month, not confirmed for Render's lowest paid plan).
3. Database: managed Postgres with PostGIS from a provider with a lasting free or low-cost tier (provider not chosen; Neon and Supabase offer PostGIS but were not checked here).
4. Cache and queue: Valkey with arq, either on the same host or a managed service.
5. Object storage for COGs, Zarr, and PMTiles: Cloudflare R2 or Source Cooperative for public open data (terms not checked, not confirmed).

## Docker

Use one Dockerfile for the API, based on `python:3.12-slim`. Install dependencies with `uv sync --frozen` from `uv.lock`. rasterio 1.5.2, pyproj 3.8.0, pyogrio 0.13.0, and shapely 2.2.0 publish manylinux and Windows wheels with bundled libraries, so the image needs no system GDAL (Windows wheel files checked on PyPI on 14 November 2026; Linux wheels assumed, not confirmed). rasterio 1.5.2 requires Python 3.12 or later (https://pypi.org/pypi/rasterio/json).

## Scheduled data refresh with GitHub Actions

From the GitHub docs (https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows):

- "The shortest interval you can run scheduled workflows is once every 5 minutes."
- Scheduled runs "can be delayed during periods of high loads", and "some queued jobs may be dropped".
- "In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred in 60 days."

Use a daily or weekly cron job to refresh POWER, IMERG, SMAP, and NDVI summaries for demo fields, and to rebuild the static site. Store Earthdata credentials as repository secrets, never in the workflow file. Because runs can be dropped or disabled, the app must show the "data as of" date for every layer. Put large outputs in object storage or release assets, not in git.

## Licence compatibility with Apache 2.0

The project licence is Apache 2.0 (`CLAUDE.md`). Permissive licences (MIT, BSD, ISC, Apache-2.0) are compatible. Weak copyleft (LGPL, MPL) is fine when we use the library unmodified. Strong copyleft (GPL, AGPL) is a problem if we link or copy the code into our distribution, but not when we only call a separate service over the network.

| Dependency | Licence | Status |
| --- | --- | --- |
| FastAPI, Pydantic, SQLAlchemy, GeoAlchemy2, arq, zarr, kerchunk, titiler, pyproj, pyogrio, DuckDB, Dash, Solara, Shiny, leafmap, ruff, mypy, pyright, pytest, pre-commit, Ollama client, llama-cpp-python, twilio, geopy, pymcdm (see `research/03_domain/open_source.md`) | MIT | OK |
| Starlette, Uvicorn, httpx, Django, Flask, Celery, rio-tiler, rasterio, geopandas, shapely, python-dotenv, fakeredis, pmtiles (Python) | BSD | OK |
| RQ | BSD-2-Clause | OK |
| xarray, VirtualiZarr, pystac-client, diskcache, earthengine-api, Streamlit, Gradio, anthropic SDK, vLLM, playwright, fiboa-cli | Apache-2.0 | OK |
| uv | MIT OR Apache-2.0 | OK |
| pixi | BSD-3-Clause (https://github.com/prefix-dev/pixi) | OK |
| React, Vite, Next.js, SvelteKit, deck.gl, terra-draw, Recharts, i18next, react-i18next, Zustand, TanStack Query, vite-plugin-pwa, Turf | MIT | OK |
| maplibre-gl, Vega-Lite, pmtiles (JS), @protomaps/basemaps, react-intl | BSD-3-Clause | OK |
| Leaflet, OpenLayers | BSD-2-Clause | OK |
| Observable Plot, Mapbox GL Draw | ISC | OK |
| ECharts, TypeScript, @playwright/test | Apache-2.0 | OK |
| psycopg 3 | LGPL-3.0-only | OK if used unmodified as a library |
| hypothesis | MPL-2.0 | OK; dev dependency only |
| PostGIS | GPL-2.0 or later (not confirmed on the PostGIS site) | OK as a separate database server; do not copy its code |
| Redis server 8+ | RSALv2, SSPLv1, or AGPLv3 (https://redis.io/legal/licenses/) | Flag. Use Valkey (BSD-3-Clause) instead |
| Open-Meteo server | AGPLv3 (https://open-meteo.com/en/pricing) | Flag only if self-hosted and modified; the hosted API is fine |
| Open-Elevation | GPL-2.0 (https://github.com/Jorl17/open-elevation) | Flag; call the API only, do not copy code |
| pyDecision | GPL-3.0 (see `research/03_domain/open_source.md`) | Flag; do not use |
| soilDB (R) | GPL-3.0 | Flag; reference only |
| PCSE | EUPL 1.1 or later | Flag for review; EUPL is copyleft with a compatibility list (not checked) |
| OpenStreetMap data (via OpenFreeMap or Protomaps) | ODbL | Data licence; attribution required, share-alike applies to derived databases, not to our code |
| FTW predictions | CC-BY-4.0 | Data licence; attribution required |

Sources for each version and licence are the PyPI JSON API (`https://pypi.org/pypi/<name>/json`) and npm registry (`https://registry.npmjs.org/<name>`), queried 14 November 2026, unless a row gives another URL.

## Sources

- GitHub Pages: https://pages.github.com/
- Cloudflare Workers limits: https://developers.cloudflare.com/workers/platform/limits/
- Netlify pricing: https://www.netlify.com/pricing/
- Vercel limits: https://vercel.com/docs/limits
- Vercel Hobby plan: https://vercel.com/docs/plans/hobby
- Render free tier: https://render.com/docs/free
- Hugging Face Spaces: https://huggingface.co/docs/hub/spaces-overview
- Fly.io pricing: https://fly.io/docs/about/pricing/
- Railway plans: https://docs.railway.com/reference/pricing/plans
- GitHub Actions events: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- Redis licences: https://redis.io/legal/licenses/
- pixi: https://github.com/prefix-dev/pixi
- Open-Meteo: https://open-meteo.com/en/pricing
- Open-Elevation: https://github.com/Jorl17/open-elevation
