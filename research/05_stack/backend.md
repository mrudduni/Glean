# Backend stack

This file compares backend options for Field Shift: the web framework, data fetching, caching and task queues, storage, raster handling, tile serving, STAC search, and Google Earth Engine. We checked versions, release dates, and licences on 14 November 2026 through the PyPI JSON API (`https://pypi.org/pypi/<name>/json`) and the GitHub API. Dataset access details live in `research/01_datasets/` and are not repeated here.

## Summary

| Layer | Recommendation | Why |
| --- | --- | --- |
| Web framework | FastAPI | Async, typed with Pydantic, auto OpenAPI docs, fits a JSON API behind a separate frontend |
| HTTP client | httpx | Async and sync in one library, HTTP/2, timeouts and retries through transports |
| Cache (demo) | diskcache | One file on disk, no server, Apache 2.0 |
| Task queue (long term) | arq on Valkey | Async-native, small, MIT; Valkey avoids the Redis licence question |
| Database (demo) | DuckDB with the spatial extension, plus GeoParquet files | No server, reads Parquet and GeoParquet directly, MIT |
| Database (long term) | Postgres with PostGIS | Multi-user writes, spatial indexes, mature |
| Raster cache | xarray with Zarr v3, COG files for map layers | Chunked time series for analysis, COGs for tiles |
| Tile serving | rio-tiler inside FastAPI, or TiTiler | Serve cached COGs as XYZ tiles |
| STAC search | pystac-client against NASA CMR-STAC and Microsoft Planetary Computer | Both search without an account |
| Earth Engine | Do not depend on it | Licence and quota terms add risk for a public tool |

## Web framework

| Framework | Version (date) | Licence | Maturity | Source |
| --- | --- | --- | --- | --- |
| FastAPI | 0.162.7 (2026-11-13) | MIT | Mature, still 0.x versioning | https://pypi.org/pypi/fastapi/json |
| Starlette (FastAPI base) | 1.10.0 (2026-10-24) | BSD-3-Clause | Mature | https://pypi.org/pypi/starlette/json |
| Uvicorn (ASGI server) | 0.54.0 (2026-09-25) | BSD-3-Clause | Mature | https://pypi.org/pypi/uvicorn/json |
| Pydantic | 2.14.3 (2026-11-05) | MIT | Mature | https://pypi.org/pypi/pydantic/json |
| Django | 6.1.3 (2026-11-03) | BSD-3-Clause | Mature | https://pypi.org/pypi/django/json |
| Flask | 3.1.3 (2026-02-19) | BSD-3-Clause | Mature | https://pypi.org/pypi/flask/json |

FastAPI pros:

- Request and response models in Pydantic give one typed contract for the frontend and for the LLM layer. The same Pydantic models can define the JSON schema for Claude structured outputs (see `llm_layer.md`).
- Native async lets one request fan out to NASA POWER, SDA, CMR, and Open-Meteo in parallel.
- It generates an OpenAPI document, so the TypeScript frontend can generate a typed client.
- TiTiler is built on FastAPI, so tile routes can mount into the same app.

FastAPI cons:

- It still uses 0.x version numbers and ships often, so pin the version.
- It has no built-in admin, auth, or ORM. We would add SQLAlchemy or plain SQL.

Django suits a content site with users, an admin panel, and forms. GeoDjango adds PostGIS support. It is heavier than we need for a computation API, and its async support is partial. Flask is simple and stable, but it is sync-first, so parallel data fetches need extra work.

Recommendation: FastAPI for both the demo and the long-term app. Keep the science code in a separate pure-Python package (for example `fieldshift_core`) so FastAPI, a notebook, a Streamlit prototype, or a batch job can all call it.

## Async data fetching

httpx 0.28.1 (2024-12-06, BSD-3-Clause, https://pypi.org/pypi/httpx/json) gives the same API for sync and async code, connection pooling, and timeouts. The last release is almost two years old. It is stable and widely used, but slow-moving. Use `httpx.AsyncClient` with `asyncio.gather` to fetch POWER, SDA, Open-Meteo, and CMR in parallel, and wrap calls in retries with backoff, because NASA and USDA endpoints return intermittent 5xx errors (not confirmed for each endpoint; the probe agent covers this).

## Caching and task queues

| Tool | Version (date) | Licence | Role | Source |
| --- | --- | --- | --- | --- |
| diskcache | 5.6.3 (2023-08-31) | Apache-2.0 | On-disk key-value cache, no server | https://pypi.org/pypi/diskcache/json |
| redis-py client | 8.1.0 (2026-07-30) | MIT | Client for Redis or Valkey | https://pypi.org/pypi/redis/json |
| valkey-py client | 6.2.0 (2026-10-12) | MIT | Client for Valkey | https://pypi.org/pypi/valkey/json |
| Celery | 5.7.0 (2026-11-05) | BSD-3-Clause | Full task queue with many brokers | https://pypi.org/pypi/celery/json |
| RQ | 3.0.0 (2026-10-28) | BSD-2-Clause | Simple Redis queue, sync workers | https://pypi.org/pypi/rq/json |
| arq | 0.28.0 (2026-04-16) | MIT | Async Redis queue | https://pypi.org/pypi/arq/json |

Redis server licence. Redis 8 and later is offered under a choice of RSALv2, SSPLv1, or AGPLv3 (https://redis.io/legal/licenses/). RSALv2 and SSPLv1 are not open source, and AGPLv3 is a strong copyleft licence. Running an unmodified Redis server as a separate process does not make our Apache 2.0 code a derivative work, but it is worth avoiding the question. Valkey is the BSD-3-Clause fork (https://github.com/valkey-io/valkey, 27,711 stars on 14 November 2026) and speaks the same protocol, so the client libraries above work against it. Flag: do not vendor or modify Redis source.

Comparison:

- diskcache needs no extra service. It suits one server process and the demo. It does not share state across machines. Its last release is from 2023, so treat it as stable but unmaintained (not confirmed whether maintainers still review issues).
- Celery has the most features (retries, schedules, chords) and the most configuration. It is more than a small team needs.
- RQ is simple, but its workers are synchronous.
- arq runs async jobs, which matches httpx and FastAPI. It has a smaller community.

Recommendation: diskcache for the hackathon, keyed by a hash of (dataset, version, geometry, date range). For the long-term app, add arq on Valkey for slow jobs such as AppEEARS tasks, HLS time-series builds, and nightly refreshes.

## Storage: PostGIS vs DuckDB spatial vs SQLite and GeoPackage

| Option | Version (date) | Licence | Source |
| --- | --- | --- | --- |
| DuckDB (Python) | 2.0.0 (2026-10-21) | MIT | https://pypi.org/pypi/duckdb/json |
| psycopg 3 (Postgres driver) | 3.3.9 (2026-11-12) | LGPL-3.0-only | https://pypi.org/pypi/psycopg/json |
| SQLAlchemy | 2.1.8 (2026-11-04) | MIT | https://pypi.org/pypi/sqlalchemy/json |
| GeoAlchemy2 | 0.21.0 (2026-11-04) | MIT | https://pypi.org/pypi/geoalchemy2/json |
| geopandas | 1.2.0 (2026-09-28) | BSD-3-Clause | https://pypi.org/pypi/geopandas/json |
| pyogrio | 0.13.0 (2026-06-26) | MIT | https://pypi.org/pypi/pyogrio/json |

PostGIS is licensed GPL-2.0 or later (not confirmed on the PostGIS site in this session; widely documented). We run it as a separate database server and talk to it over the network, so it does not affect our code's licence. psycopg 3 is LGPL-3.0, which allows use from Apache 2.0 code as an unmodified library.

- DuckDB with the spatial extension reads GeoParquet, Parquet, CSV, and many GDAL formats, and runs spatial joins in-process. It is ideal for read-heavy analysis and for shipping a demo dataset as files. It allows one writer process at a time.
- SQLite or GeoPackage is simple and portable. GeoPackage is a good exchange format for field boundaries, but spatial SQL in SQLite needs SpatiaLite, which is harder to install on Windows (not confirmed).
- Postgres with PostGIS handles many users, saved farms, and concurrent writes. It needs a hosted database. Render's free Postgres expires 30 days after creation (https://render.com/docs/free), so a free long-term Postgres needs another host (see `deployment.md`).

Recommendation: DuckDB plus GeoParquet files for the hackathon and for read-only reference layers (CSB polygons, SSURGO map units, county stats) in the long term. Add Postgres with PostGIS when the app stores user farms and scenarios.

## Cached rasters: xarray, Zarr, kerchunk, VirtualiZarr

| Library | Version (date) | Licence | Source |
| --- | --- | --- | --- |
| xarray | 2026.9.0 (2026-09-29) | Apache-2.0 | https://pypi.org/pypi/xarray/json |
| zarr | 3.4.2 (2026-10-27) | MIT | https://pypi.org/pypi/zarr/json |
| kerchunk | 0.2.10 (2026-03-30) | MIT | https://pypi.org/pypi/kerchunk/json |
| VirtualiZarr | 2.8.0 (2026-10-14) | Apache-2.0 | https://pypi.org/pypi/virtualizarr/json |
| rasterio | 1.5.2 (2026-09-30) | BSD-3-Clause | https://pypi.org/pypi/rasterio/json |

- Zarr v3 stores per-farm time series (for example daily SMAP, IMERG, and NDVI clipped to a buffer around the field) as chunked arrays. Writes are cheap, and xarray reads them lazily.
- kerchunk and VirtualiZarr build a virtual Zarr index over existing NetCDF or HDF5 files without copying them. That helps when we read many IMERG or SMAP granules repeatedly over HTTPS. VirtualiZarr is the newer, more active project. Both are worth trying only after the basic pipeline works, because they add indirection and need Earthdata auth to pass through to fsspec (not confirmed for every DAAC).
- COG (Cloud Optimized GeoTIFF) is the right format for any layer we show as map tiles.

Recommendation: per-farm Zarr stores for time series and COGs for map layers, written to a cache directory outside the repo. Try VirtualiZarr in the long-term phase for IMERG and SMAP archives.

## Serving COG tiles: TiTiler and rio-tiler

| Library | Version (date) | Licence | Source |
| --- | --- | --- | --- |
| titiler.core / titiler.application | 2.4.0 (2026-09-21) | MIT | https://pypi.org/pypi/titiler.core/json |
| rio-tiler | 9.4.13 (2026-11-02) | BSD-3-Clause | https://pypi.org/pypi/rio-tiler/json |

TiTiler (https://github.com/developmentseed/titiler, MIT, 1,208 stars) is a FastAPI app that serves XYZ tiles, previews, and point values from COGs and STAC items. rio-tiler is the library under it.

- For the demo, we do not need a tile server. Pre-render small PNG overlays or ship COGs that the browser reads directly (for example with a COG layer in deck.gl or OpenLayers; not tested).
- In the long term, mount `titiler.core` routers inside our FastAPI app to serve NDVI, ESI, and slope layers for any farm.

## STAC search: NASA CMR-STAC and Microsoft Planetary Computer

pystac-client 0.9.1 (2026-10-20, Apache-2.0, https://pypi.org/pypi/pystac-client/json) searches both catalogs.

NASA CMR-STAC. A search against `https://cmr.earthdata.nasa.gov/stac/LPCLOUD/search?collections=HLSL30_2.0&bbox=...` returned HLS items with no login on 14 November 2026 (our test). Searching is open, but downloading assets from LP DAAC needs Earthdata Login (see `research/01_datasets/nasa/access_tooling.md`).

Microsoft Planetary Computer (MPC). We listed the MPC STAC collections at `https://planetarycomputer.microsoft.com/api/stac/v1/collections` on 14 November 2026. It returned 139 collections. Those relevant to Field Shift, with temporal extent from the same response:

| MPC collection | Extent | Notes |
| --- | --- | --- |
| `hls2-l30`, `hls2-s30` | 2020-01-01 to open-ended | HLS v2, Landsat and Sentinel-2 |
| `landsat-c2-l2` | 1982-08-22 to open-ended | Landsat Collection 2 Level 2 |
| `modis-13Q1-061` and 21 other `modis-*-061` collections | 2000 to open-ended | NDVI and EVI, LST, ET (16A3GF), GPP, land cover |
| `nasadem` | 2000 (static) | NASA DEM from SRTM |
| `gpm-imerg-hhr` | 2000-06-01 to 2021-05-31 | Stops in 2021, so it is not usable for recent seasons |
| `usda-cdl` | 2008 to 2021 | Stops in 2021; use NASS directly for recent years |
| `gnatsgo-rasters`, `gnatsgo-tables` | 2020 snapshot | CC0-1.0 gridded soils |
| `sentinel-2-l2a`, `esa-worldcover`, `cop-dem-glo-30`, `era5-pds`, `terraclimate`, `daymet-*` | various | Non-NASA support layers |

MPC has no SMAP, ECOSTRESS, or GRACE collections in this list. Most collections list their licence as "proprietary" in STAC, which means "see the provider's terms", so cite the original NASA or USDA licence.

Auth. The MPC docs say the STAC API needs no account or token, and the data assets need a SAS token. Anyone can get one anonymously: "Datasets in the Planetary Computer are anonymously accessible: you don't need to supply a subscription key to get a SAS token" (https://planetarycomputer.microsoft.com/docs/concepts/sas/). The `planetary-computer` Python package signs items for you; version 1.0.0 dates from 2023-07-05 (MIT, https://pypi.org/pypi/planetary-computer/json). Rate limits and token expiry are more generous inside the Azure West Europe region. The MPC JupyterHub was retired, and a GitHub issue from December 2025 calls it "now-deprecated" (https://github.com/microsoft/PlanetaryComputer/issues/464), but the STAC API and data still worked in our test.

Recommendation: use MPC for HLS, Landsat, MODIS, and NASADEM in the demo, because it needs no login and serves COGs from Azure Blob storage. Use CMR-STAC plus `earthaccess` for SMAP, ECOSTRESS, GRACE, and recent IMERG. Record the STAC item ID and collection for every value, because both count as NASA data in the submission.

## Google Earth Engine

The Python package `earthengine-api` is 1.7.52 (2026-11-09, Apache-2.0, https://pypi.org/pypi/earthengine-api/json).

Terms. Earth Engine is free only for listed noncommercial uses, including "Individual using Earth Engine for noncommercial purposes". Individuals may not "Receive compensation for applications or data created by the use of Earth Engine" (https://earthengine.google.com/noncommercial/). Since 27 April 2026, noncommercial projects get a monthly compute quota: the default Community Tier gives 150 EECU-hours, and the Contributor Tier gives 1,000 EECU-hours but needs an active billing account (https://developers.google.com/earth-engine/guides/noncommercial_tiers).

Assessment:

- Allowed: a student or hobby team using Earth Engine for a hackathon fits the noncommercial individual or academic case.
- Not wise as a core dependency: every server call needs a registered Cloud project and a service account, quota is shared across all users of the deployed app, and any future funding or commercial use would require a licence. Earth Engine code also does not run offline or self-hosted.
- Useful as a side tool: prototyping an index in the Code Editor, or checking OpenET values, before porting the logic to xarray.

Recommendation: do not put Earth Engine in the request path. If a team member uses it for exploration, list it in the References and keep the production pipeline on open STAC and NASA endpoints.

## Sources

- PyPI JSON API, queried 14 November 2026: https://pypi.org/pypi/{package}/json
- Redis licences: https://redis.io/legal/licenses/
- Valkey: https://github.com/valkey-io/valkey
- TiTiler: https://github.com/developmentseed/titiler
- Render free tier: https://render.com/docs/free
- MPC STAC collections: https://planetarycomputer.microsoft.com/api/stac/v1/collections
- MPC SAS tokens: https://planetarycomputer.microsoft.com/docs/concepts/sas/
- MPC Hub deprecation mention: https://github.com/microsoft/PlanetaryComputer/issues/464
- NASA CMR-STAC LPCLOUD: https://cmr.earthdata.nasa.gov/stac/LPCLOUD
- Earth Engine noncommercial terms: https://earthengine.google.com/noncommercial/
- Earth Engine noncommercial tiers: https://developers.google.com/earth-engine/guides/noncommercial_tiers
