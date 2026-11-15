# data-pipeline (D · Data engineer)

Downloads, cleans and packages every dataset for the 3 demo fields in Finney County, KS
(FIPS 20055) and a 150-field neighbour pool. Outputs follow the shared contract in the root
`README.md` §7–§8. Nothing here is fetched live during judging.

| Output | For | Contract |
|---|---|---|
| `out/processed/{fid}/*.csv`, `out/processed/nass.json` | M (model) | README §8.2 |
| `out/web/fields.json`, `sources.json`, `field/{fid}/water.json`, `observed.json`, `neighbors.json` | web app + M | README §8.3 |
| `../docs/DATA_SOURCES.md` | submission | used / pending / skipped datasets |

## Setup

```bash
cd data-pipeline
python -m venv .venv
.venv/Scripts/activate            # Windows;  source .venv/bin/activate elsewhere
pip install -r requirements.txt
cp .env.example .env              # then fill in your keys (never commit .env)
```

| Variable | Needed for | Get it |
|---|---|---|
| `EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD` | AppEEARS (MODIS, SMAP L4, ECOSTRESS, SRTM), GRACE, IMERG | https://urs.earthdata.nasa.gov — also approve **NASA GESDISC DATA ARCHIVE** under Applications → Authorized Apps |
| `NASS_API_KEY` | yields, prices, acres | https://quickstats.nass.usda.gov/api |
| `OPENET_API_KEY` | field + neighbour ET | https://etdata.org |

POWER, SSURGO, CSB, PRISM, USGS wells, 3DEP terrain and the ORNL MODIS fallback need no key.

## Run

```bash
python run_all.py                 # everything, in order; finished downloads are skipped
python run_all.py --skip modis_ornl   # leave out the slow no-login MODIS fallback
python run_all.py --only power,build_fields
python run_all.py --force         # redo everything
python validate.py                # handover §7 acceptance checks: PASS / FAIL / PENDING
```

A step that can't run yet (missing key, AppEEARS still queued) prints **SKIPPED** with the
reason and the rest continues. Rerun `run_all.py` after adding a key or when AppEEARS
finishes; build steps always rerun so new inputs flow into the web JSON.

## Steps

| # | Step | Script | Output | Needs |
|---|---|---|---|---|
| 1 | County outline | `fetch/county.py` | `raw/county_20055.geojson` (Census 2023 cartographic boundary) | — |
| 2 | Crop Sequence Boundaries | `fetch/csb.py` | `raw/csb_finney.gpkg` (15,926 fields, CDL 2018–2025) | 3.8 GB national zip, read in place |
| 3 | Pick f1/f2/f3 | `process/select_fields.py` | `raw/fields_draft.geojson` | — |
| 4 | Neighbour pool | `neighbors/pool.py select` | `raw/neighbors/pool.geojson` | — |
| 5 | AppEEARS submit/poll/download | `fetch/appeears.py` | `raw/appeears/<task>/` | Earthdata |
| 6 | NASA POWER | `fetch/power.py` | `{fid}/weather_daily.csv` | — |
| 7 | SSURGO | `fetch/ssurgo.py` | `raw/ssurgo/fields_soil.json` (+ cache per mukey) | — |
| 8 | Terrain | `process/terrain.py` | `raw/terrain.json` (SRTM, else USGS 3DEP) | — |
| 9 | MODIS fallback | `fetch/modis_ornl.py [demo\|area]` | `raw/modis_ornl/` | — (slow service) |
| 10 | NASS QuickStats | `fetch/nass.py` | `nass.json` | NASS key |
| 11 | PRISM | `fetch/prism.py` | `{fid}/prism_daily.csv` | — |
| 12 | GPM IMERG | `fetch/imerg.py` | `{fid}/precip_imerg_daily.csv` | Earthdata, or Giovanni CSVs |
| 13 | OpenET | `fetch/openet.py` | `{fid}/openet_monthly.csv`, `raw/openet/neighbors_annual.json` | OpenET key |
| 14 | GRACE/GRACE-FO | `fetch/grace.py` | `{fid}/grace_monthly.csv` | Earthdata |
| 15 | Wells | `fetch/wells.py` | `raw/wells/wells.json` | — |
| 16 | Harmonize | `process/harmonize.py` | `{fid}/ndvi_modis.csv`, `smap_l4_daily.csv`, `ecostress.csv` | step 5 or 9 |
| 17 | fields.json | `process/build_fields.py` | `out/web/fields.json` | 3, 7, 8 |
| 18 | Pool features | `neighbors/pool.py features` | `raw/neighbors/pool_features.csv` | 4 (+ MODIS, OpenET, ESI when available) |
| 19 | Matching | `neighbors/match.py` | `field/{fid}/neighbors.json` | 17, 18 |
| 20–22 | Web JSON | `process/build_water.py`, `build_observed.py`, `build_sources.py` | `water.json`, `observed.json`, `sources.json`, `docs/DATA_SOURCES.md` | — |

Each script also runs on its own, e.g. `python fetch/power.py --force`.

## Demo fields (auto-selected, deterministic)

| id | CSB id | Area | Crops 2018→2025 | Soil | Why |
|---|---|---|---|---|---|
| f1 | 201825007952467 | 52 ha | C C C C W C C C | Las clay loam | centre-pivot circle, 4 km from Garden City |
| f2 | 201825006143835 | 64 ha | F W S F W S F W | Richfield silt loam | rectangular dryland wheat–sorghum–fallow |
| f3 | 201825007467030 | 55 ha | A C C C C C S S | Valent fine sand, WEG 1, WEI 250 | pivot on Arkansas River sand hills |

Rules are in `process/select_fields.py`. To force a different field put its CSB id in
`raw/field_overrides.json` (e.g. `{"f3": "201825001234567"}`) and run
`python run_all.py --force --only select_fields` and then `python run_all.py`.

## Methods and choices worth knowing

- **Pivot detection:** CSB outlines are raster-derived and jagged, so perimeter circularity is
  unreliable. We use area ÷ minimum-bounding-circle area (`pivot_fill`; circle ≈ 1, square ≈ 0.64).
- **Rotation class:** `process/rotation_class.py`, rules from handover §6.12, shared by demo fields
  and neighbours. Confidence counts years whose crop is in the class's canonical sequence.
- **Irrigation (neighbours and f3):** MODIS Jul–Aug NDVI peak ≥ 0.75 in at least half of 2018–2025.
  Until MODIS arrives for the pool, a proxy is used (pivot shape, or corn/alfalfa in ≥ 3 of 8 years);
  `neighbors.json` `method.note` says which.
- **NDVI drop** in `neighbors.json` = % below the field's 2016–2019 Jun–Aug mean; **positive = less green**.
- **Soil:** dominant major component of the map unit at the field centre; a 6×6 point grid checks the
  polygon and appends "(mixed)" when another map unit covers > 40 %.
- **Terrain:** slope and the low-spot flag (field ≥ 3 m below a 1 km ring) in UTM 14N. SRTM is used
  once AppEEARS delivers it (`terrain` recomputes automatically); until then USGS 3DEP.
- **Wells:** the legacy NWIS gwlevels service is gone (fall 2025), so this uses the USGS Water Data
  OGC API. Trend = OLS of the per-winter median depth to water; positive = water table falling.
- **GRACE:** nearest 0.5° cell of the JPL CRI mascon; ~300 km true resolution; the 2017-07 → 2018-05
  gap is left empty. `water.json` `grace` is `null` until GRACE is downloaded.
- **ECOSTRESS ET:** AppEEARS reports `ETdaily` in W/m² (daily-mean latent heat), converted to mm/day (÷ 28.36).
- **Caching:** every HTTP response is cached under `raw/` (gitignored); writes are atomic.

## Free-tier limits

Every outside call goes through `common.request()` / `spend()`, which counts it in
`raw/usage.json` and refuses (step shows **SKIPPED**) before a budget is exceeded. `run_all.py`
prints the usage table at the end of each run.

| Service | Budget | Why |
|---|---|---|
| OpenET | 90 / month | the free key stops at about 100 requests a month (quota reached on 2026-11-15); a full run needs 3 + 150 |
| NASS | 300 / day | no published rate limit; a full run needs ~20 |
| AppEEARS | 200 / day, task status at most every 5 min | no published limit; politeness |
| GES DISC (IMERG) | 12,000 / day, ≤ 4 per second, 2 connections | no published limit, but it blocks IPs that send many failing requests; a full run needs ~9,500 |
| Earthdata CMR / GRACE | 60 / day | a full run needs ~3 |
| POWER, PRISM, SDA, USGS, ORNL | 100, 20, 500 / day; 200 / hour; 3,000 / day | none published (USGS returns `X-RateLimit-Remaining`, which is honoured) |

Also: HTTP 429 or a low `X-RateLimit-Remaining` stops that service for the rest of the period;
nothing retries on 429, and POSTs are never retried automatically; GES DISC stops at the first
401/403. To change a budget edit `BUDGETS` in `common.py`; to clear a block delete the service's
entry in `raw/usage.json`.

## Status

Run `python validate.py` for the live list. Missing pieces are marked PENDING with the reason
(e.g. "needs NASS_API_KEY"). `docs/DATA_SOURCES.md` lists the same under "Planned, not delivered yet".
