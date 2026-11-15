# Handover 1 · Data engineer (D)

You are building the **data pipeline** for Team Brackets' crop-rotation decision tool (NASA Space Apps 2026, "Adapting Farms with NASA Data"). Read the team contract [docs/CONTRACT.md](../docs/CONTRACT.md) first (it was the root README.md; "README §N" below means its sections). It is the shared contract. Its §7 (IDs and conventions) and §8 (data contract) define exactly what you must produce. If this file and the README disagree, the README wins.

## 1. Your mission

Download, clean and package every dataset the project needs for **3 demo fields in Finney County, Kansas (FIPS 20055)** and a pool of ~100–150 neighbouring fields. You hand two kinds of output to others:

- **To M (modeller):** per-field daily and monthly tables in `data-pipeline/out/processed/` (README §8.2).
- **To the web app:** display-ready JSON in `data-pipeline/out/web/` (README §8.3): `fields.json`, `sources.json`, and per field `water.json`, `observed.json`, `neighbors.json`.

You also own **Farms Like Yours** (the neighbour matching and grouping) and `docs/DATA_SOURCES.md`.

## 2. What you own and must not touch

- **You own:** `data-pipeline/**`, `docs/DATA_SOURCES.md`.
- **Don't edit:** `model/`, `scripts/`, `web/`, `content/`, `design/`, `README.md`. If the contract needs to change, tell the team. Don't change it on your own.

## 3. Folder layout to create

```text
data-pipeline/
├─ README.md                  # how to run, env vars, what each script does
├─ requirements.txt
├─ .env.example               # EARTHDATA_USERNAME, EARTHDATA_PASSWORD, NASS_API_KEY, OPENET_API_KEY
├─ config.py                  # field ids, county FIPS, bbox, years, paths, CDL code map
├─ run_all.py                 # runs every step in order; each step skips if its output exists (--force to redo)
├─ fetch/
│  ├─ county.py               # TIGER county boundary for 20055
│  ├─ csb.py                  # Crop Sequence Boundaries → candidate fields
│  ├─ power.py                # NASA POWER daily
│  ├─ ssurgo.py               # Soil Data Access queries
│  ├─ nass.py                 # QuickStats
│  ├─ appeears.py             # submit / poll / download (MODIS, SMAP L4, ECOSTRESS, SRTM, HLS)
│  ├─ imerg.py                # parse Giovanni CSV exports (or OPeNDAP if you automate it)
│  ├─ prism.py                # parse PRISM Explorer CSVs
│  ├─ openet.py               # OpenET API or CSV exports
│  ├─ grace.py                # JPL mascon netCDF → cell series
│  └─ wells.py                # USGS groundwater levels (fallback: KGS WIZARD)
├─ process/
│  ├─ select_fields.py        # picks f1/f2/f3, writes fields.geojson draft
│  ├─ harmonize.py            # → out/processed/{fid}/*.csv
│  ├─ rotation_class.py       # crop sequence → RotationClass (shared rules, §7 below)
│  ├─ build_fields.py         # → out/web/fields.json
│  ├─ build_water.py          # → out/web/field/{fid}/water.json
│  ├─ build_observed.py       # → out/web/field/{fid}/observed.json
│  └─ build_sources.py        # → out/web/sources.json
├─ neighbors/
│  ├─ pool.py                 # neighbour pool + features
│  └─ match.py                # similarity + groups → out/web/field/{fid}/neighbors.json
├─ raw/                       # gitignored downloads
└─ out/
   ├─ processed/              # committed
   └─ web/                    # committed
```

`requirements.txt`: `requests pandas numpy geopandas shapely pyproj xarray netCDF4 rasterio python-dotenv earthaccess tqdm`.

Python 3.11. Put a `_meta` block (README §7.3) on every JSON file you write, with `"mock": false` and `"generator": "data-pipeline/<script>.py"`.

## 4. Accounts (do these first)

| Account | Why | Notes |
|---|---|---|
| NASA Earthdata Login (urs.earthdata.nasa.gov) | AppEEARS, Giovanni, GRACE (PO.DAAC), IMERG | Also approve the "NASA GESDISC DATA ARCHIVE" application in your Earthdata profile for Giovanni/GES DISC access. Put credentials in `~/.netrc` for `earthaccess`. |
| USDA NASS QuickStats API key | Yields, prices, acres | Instant, by email |
| OpenET account + API key | Field-level ET | Free tier |
| (none) | POWER, SSURGO SDA, CSB, CropScape, PRISM, USGS | Public |

Never commit keys. Use `.env` (gitignored) and `python-dotenv`.

## 5. Delivery order (what others are waiting for)

1. **Submit the AppEEARS jobs first.** They can queue for hours. Submit as soon as you have candidate points; resubmit later if fields change.
2. **Pick f1, f2, f3** and write `out/web/fields.json` (crop history and soil may be partial at first). This unblocks M and F.
3. **`out/processed/f1/weather_daily.csv` + f1 soil in `fields.json`.** This unblocks M's Replay engine.
4. Same for f2, f3; then `nass.json`.
5. `observed.json`, `water.json`, `sources.json`.
6. Neighbour pool → `neighbors.json` (M needs it for evidence on the cards).
7. `precip_imerg_daily.csv`, `prism_daily.csv`, `openet_monthly.csv`, `smap_l4_daily.csv`, `ecostress.csv`, `grace_monthly.csv` as they arrive.

Tell M and F each time a file goes from partial to complete.

## 6. Step-by-step

### 6.1 County and candidate fields (`fetch/county.py`, `fetch/csb.py`, `process/select_fields.py`)

1. **County outline:** download the US Census TIGER/Line or cartographic boundary county file and select `STATEFP=20`, `COUNTYFP=055` (Finney). Save `raw/county_20055.geojson`. Use it for clipping and as the AppEEARS area for SRTM.
2. **Crop Sequence Boundaries (CSB):** download USDA NASS's CSB for Kansas (latest release covering ~8 years, e.g. 2016–2023). It gives field polygons with one CDL crop code per year. Filter to Finney County with its county attribute if present, otherwise clip with the county outline.
3. **Map CDL codes → `CropId`** in `config.py` (check against the CDL legend):

   | CDL code | CDL name | CropId |
   |---|---|---|
   | 1 | Corn | `corn` |
   | 2 | Cotton | `cotton` |
   | 4 | Sorghum | `sorghum` |
   | 5 | Soybeans | `soybean` |
   | 24 | Winter Wheat | `wheat` |
   | 26 | Dbl Crop WinWht/Soybeans | `wheat` (note double crop) |
   | 236 | Dbl Crop WinWht/Sorghum | `wheat` (note double crop) |
   | 27 | Rye | `rye_cover` |
   | 36 | Alfalfa | `alfalfa` |
   | 61 | Fallow/Idle Cropland | `fallow` |
   | 205 | Triticale | `triticale` |
   | anything else | | `"other"` |

4. **Pick 3 demo fields:**
   - **f1 · irrigated pivot:** a centre-pivot circle (visible on imagery) mostly in corn; `irrigated: true`.
   - **f2 · dryland:** a field whose sequence looks like wheat–sorghum–fallow; `irrigated: false`.
   - **f3 · sandy / wind-erodible:** a field on sandy soil with SSURGO wind erodibility group (WEG) 1–3, typically south of the Arkansas River.
   - Prefer fields of 50–65 ha (a quarter section is ~65 ha) with clean 8-year histories. Simplify polygons to ≤ 200 vertices.
   - Fallback if CSB is unusable: look up CDL per year at chosen points with the CropScape web service, and draw the 3 outlines by hand from imagery.
5. Write `raw/fields_draft.geojson` and immediately a first `out/web/fields.json` (soil and detection can be filled in later; keep the schema shape).

### 6.2 AppEEARS (`fetch/appeears.py`) — submit early

API base: `https://appeears.earthdatacloud.nasa.gov/api/`

1. `POST /login` with HTTP basic auth (Earthdata username and password) → bearer token.
2. Look up exact product and layer names: `GET /product` and `GET /product/{ProductAndVersion}`. Versions change; don't hard-code without checking.
3. **Point task** (all demo-field centres, plus 4 extra points inside each demo field, plus every neighbour centre):

```json
{
  "task_type": "point",
  "task_name": "brackets_points",
  "params": {
    "dates": [{ "startDate": "01-01-2000", "endDate": "12-31-2025" }],
    "layers": [
      { "product": "MOD13Q1.061", "layer": "_250m_16_days_NDVI" },
      { "product": "MOD13Q1.061", "layer": "_250m_16_days_pixel_reliability" },
      { "product": "SPL4SMGP.<version>", "layer": "<root-zone soil moisture layer>" },
      { "product": "SPL4SMGP.<version>", "layer": "<surface soil moisture layer>" },
      { "product": "<ECOSTRESS L3 ET product>", "layer": "<ET layer>" },
      { "product": "<ECOSTRESS L4 ESI product>", "layer": "<ESI layer>" }
    ],
    "coordinates": [
      { "id": "f1_c", "category": "demo", "latitude": 37.97, "longitude": -100.87 }
    ]
  }
}
```

   Coordinates above are placeholders. `POST /task` → `task_id`. Poll `GET /task/{task_id}` (every few minutes, not faster). When done: `GET /bundle/{task_id}` lists files; download each with `GET /bundle/{task_id}/{file_id}`. Results are CSVs, one per product.

   If the request is too big or slow, split it: MODIS + SMAP for all points first; ECOSTRESS only for the 3 demo fields.

4. **Area task** for SRTM (`SRTMGL1_NC.003`, layer `SRTMGL1_DEM`) with the county GeoJSON, output GeoTIFF. Compute slope (%) with numpy gradients in a projected CRS (UTM 14N, EPSG:32614).
5. *(COULD)* HLS points (`HLSL30`, `HLSS30`, 2019–2025) for the 3 demo fields only.

**Cleaning:**
- NDVI: keep pixel reliability 0–1 (`qa_ok = 1`), otherwise `qa_ok = 0`. Check the scale: final NDVI must be between −0.2 and 1.0 (apply ×0.0001 if values are in the thousands).
- SMAP L4 is 3-hourly. Average to daily. Units m³/m³.
- ECOSTRESS is sparse with varying overpass times. Keep only passes with valid quality flags.

**Fallback if AppEEARS hasn't delivered:** the ORNL DAAC MODIS/VIIRS Land Product Subsets web service gives MOD13Q1 time series for a point with no login. Use it for the 3 demo fields and as many neighbours as time allows.

### 6.3 NASA POWER (`fetch/power.py`)

```text
GET https://power.larc.nasa.gov/api/temporal/daily/point
    ?parameters=T2M_MAX,T2M_MIN,T2M,RH2M,WS2M,WS10M,WS10M_MAX,ALLSKY_SFC_SW_DWN,PRECTOTCORR
    &community=AG&longitude={lon}&latitude={lat}
    &start=19810101&end=20251231&format=JSON
```

- One request per demo field. If a full-range request is refused, split by decade.
- Fill value is `-999` → empty cell.
- Check the units block in the response. Radiation must end up as **MJ/m²/day** (`rs_mj_m2`). Convert from kWh/m²/day with ×3.6 if needed.
- Solar may only start in 1984. That's fine; the Replay uses 2000 onward.
- Output `out/processed/{fid}/weather_daily.csv` with columns exactly as README §8.2.

### 6.4 SSURGO via Soil Data Access (`fetch/ssurgo.py`)

`POST https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest` with JSON `{"query": "<SQL>", "format": "JSON+COLUMNNAME"}`.

1. Map unit at a point:
   ```sql
   SELECT mukey FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('POINT(-100.87 37.97)')
   ```
2. Attributes for that `mukey` (dominant component, `majcompflag = 'Yes'`, highest `comppct_r`):
   - `mapunit.muname`
   - `muaggatt.aws0100wta` (available water storage 0–100 cm, cm → ×10 for mm), `muaggatt.drclassdcd`, `muaggatt.hydgrpdcd`
   - `component.compname, comppct_r, slope_r, weg, wei`
   - top `chorizon` of that component: `om_r, kwfact, awc_r`, and texture from `chtexturegrp.texdesc`
   - `corestrictions.resdept_r` (shallowest restriction, if any)
3. Derive `awc_mm_per_m`: depth-weighted `awc_r` (cm/cm) over 0–100 cm × 1000. Cross-check with `aws0100wta × 10`; they should be in the same range.
4. Field soil = the dominant map unit at the centre. Also query the polygon (`SDA_Get_Mukey_from_intersection_with_WktWgs84('POLYGON((...))')`) and log if another map unit covers more than 40% (mention it in `fields.json` `soil.map_unit_name`, e.g. "… (mixed)").
5. The same function runs for every neighbour centre (§6.10). Cache responses in `raw/ssurgo/{mukey}.json`.

### 6.5 USDA NASS QuickStats (`fetch/nass.py`)

`GET https://quickstats.nass.usda.gov/api/api_GET/?key={KEY}&format=JSON&...`

- **County yields:** `source_desc=SURVEY&sector_desc=CROPS&agg_level_desc=COUNTY&state_alpha=KS&county_name=FINNEY&statisticcat_desc=YIELD&commodity_desc={CORN|SORGHUM|WHEAT|SOYBEANS|HAY|COTTON}`. Use `prodn_practice_desc` for `IRRIGATED` / `NON-IRRIGATED`. Corn and sorghum: grain only (`util_practice_desc=GRAIN`). Wheat: winter wheat (`class_desc=WINTER`). Hay: alfalfa (`class_desc=ALFALFA`).
- **NASS has dropped many county estimates in recent years.** When a crop/year is missing at county level, fill from the agricultural district (`agg_level_desc=AGRICULTURAL DISTRICT&asd_desc=SOUTHWEST`), then the state, and record `level`.
- **Prices:** `agg_level_desc=STATE&state_alpha=KS&statisticcat_desc=PRICE RECEIVED&freq_desc=ANNUAL`, 2015–2024. Units: corn, sorghum, wheat, soybeans in $/bu (sorghum is sometimes $/cwt; convert: $/bu = $/cwt × 0.56); hay $/ton; cotton lint $/lb.
- **Acres planted** by county for each crop (local-market check).
- No county data for triticale, rye or cover crops is expected. Leave them out; M uses the defaults in `crops.yaml`.
- Output `out/processed/nass.json` (README §8.2).

### 6.6 GPM IMERG (`fetch/imerg.py`)

Easiest route: NASA Giovanni (giovanni.gsfc.nasa.gov) → "Time Series, Area-Averaged" → variable from **GPM_3IMERGDF** (daily, Final run) → a small box around each field (about 0.1° × 0.1°) → 2000-06-01 to the latest available date → download CSV. Do one per demo field (or one county box if the three are within ~10 km of each other, and say so in `sources.json`).

Parse to `out/processed/{fid}/precip_imerg_daily.csv` (`date, precip_mm`).

### 6.7 PRISM (`fetch/prism.py`)

Use the PRISM Explorer (prism.oregonstate.edu, "Data Explorer: time series values for individual locations") for each demo field centre: daily tmin, tmax, ppt, 1991-01-01 → 2025-12-31, 4 km. Download CSVs, parse to `out/processed/{fid}/prism_daily.csv` (`date, tmin_c, tmax_c, precip_mm`). M computes the 1991–2020 normals and 2016–2025 recent stats from it.

### 6.8 OpenET (`fetch/openet.py`)

- Check that Finney County is covered (OpenET covers the western US; Kansas should be included).
- Use the OpenET API (docs at openet-api.org) time-series endpoint for a point or polygon: model `Ensemble`, variable `ET`, interval `monthly`, units mm, 2016 → latest. Or export the same from the OpenET Data Explorer as CSV.
- Demo fields → `out/processed/{fid}/openet_monthly.csv` (`month, et_mm`).
- Neighbours → annual ET for `neighbors.json` (sum of months per full year, median across years).
- Free tier has request limits. Cache everything in `raw/openet/`.

### 6.9 GRACE/GRACE-FO (`fetch/grace.py`)

- Download the JPL GRACE/GRACE-FO **mascon** monthly product (RL06.x, CRI-filtered) from PO.DAAC with `earthaccess` (search "GRACE mascon JPL"). Variable `lwe_thickness` (cm), monthly, 2002 → latest.
- Take the cell containing each field (0.5° grid; all three fields probably share a cell). Remember the true resolution is ~300 km. This is a regional aquifer signal.
- There is a gap from 2017-07 to 2018-05 between missions. Leave those months out; don't interpolate.
- `trend_cm_per_yr`: ordinary least-squares slope over the full record.
- Output `out/processed/{fid}/grace_monthly.csv` and the `grace` block of `water.json`.

### 6.10 Groundwater wells (`fetch/wells.py`)

- Try the USGS groundwater levels service for Finney County first: legacy `https://waterservices.usgs.gov/nwis/gwlevels/?format=json&countyCd=20055&startDT=2000-01-01`. USGS is migrating to new Water Data APIs (api.waterdata.usgs.gov). If the legacy service is gone, use the new field-measurements endpoint.
- Fallback: Kansas Geological Survey's WIZARD water-level database (manual CSV export).
- Keep the 3 wells nearest each demo field with ≥ 10 years of winter measurements. Convert feet → metres (×0.3048). `depth_to_water_m` increases as the water table drops.
- `trend_m_per_yr`: OLS slope of depth to water. Positive = water table falling.

### 6.11 Harmonize (`process/harmonize.py`)

The common analysis unit is the **field**. Every series is sampled at the field centre (or averaged over the 5 points inside the field for MODIS and SMAP). Write every processed CSV with the exact column names in README §8.2, ISO dates, metric units, empty cells for missing values. No interpolation beyond filling single missing days in POWER.

### 6.12 Rotation class (`process/rotation_class.py`)

The same function classifies demo fields and neighbours. Input: the 8-year crop list (oldest → newest). Rules, applied in order:

| Rule | Class | Canonical `sequence` |
|---|---|---|
| alfalfa in ≥ 3 years | `alfalfa` | `["alfalfa","alfalfa","alfalfa","alfalfa","corn","wheat"]` |
| corn in ≥ 75% of years | `continuous_corn` | `["corn"]` |
| corn ≥ 2 and soybean ≥ 2 years | `corn_soy` | `["corn","soybean"]` or with wheat if present |
| wheat ≥ 2, sorghum ≥ 2, fallow ≥ 1, corn ≤ 1 | `wsf` | `["wheat","sorghum","fallow"]` |
| wheat ≥ 3 and fallow ≥ 3, sorghum ≤ 1 | `wheat_fallow` | `["wheat","fallow"]` |
| corn ≥ 2 and (wheat ≥ 1 or sorghum ≥ 1) | `corn_wheat_sorghum` | `["corn","wheat","sorghum"]` |
| otherwise | `mixed` | most common 3-year pattern |

`confidence`: `good` if the rule matched with ≥ 6 of 8 years consistent, `fair` if 4–5, else `limited`. Add `detected` to each `Field` and neighbour.

### 6.13 Build web JSON (`process/build_*.py`)

- **`fields.json`:** README §8.3 `FieldsFile`. `name` examples: f1 `{"en":"North pivot (irrigated)","es":"Pivote norte (riego)"}`, f2 `{"en":"Dryland wheat field","es":"Campo de trigo de secano"}`, f3 `{"en":"Sandy field","es":"Campo arenoso"}`. `area_ac = area_ha × 2.471`. `terrain.low_spot = true` if the field's mean elevation is ≥ 3 m below the mean of a 1 km ring around it.
- **`water.json`:** GRACE block, wells, and `smap_rootzone_anom` (monthly mean root-zone moisture, anomaly in % vs the 2015–2025 mean for that calendar month).
- **`observed.json`:**
  - `ndvi_modis`: QA-filtered series.
  - `ndvi_climatology`: the 23 composites per year averaged by day-of-year over 2000–2025 with p10/p90.
  - `drought_years`: Jun–Aug mean NDVI anomaly vs the 2016–2019 Jun–Aug mean, for 2002, 2011, 2012, 2018, 2020, 2022 and any other year below −10%.
  - `openet_monthly`, `ecostress`.
  - `precip_check`: monthly POWER vs IMERG (vs CoCoRaHS if done).
- **`sources.json`:** one entry per `SourceTag` you actually used (README §7.2), with real URLs, resolution, period and a one-line "used for". Also write it as a readable table in `docs/DATA_SOURCES.md`, plus the "skipped on purpose" list from README §10.

### 6.14 Farms Like Yours (`neighbors/pool.py`, `neighbors/match.py`)

1. **Pool:** CSB fields in Finney County within ~25 km of the demo fields, 20–130 ha, with ≥ 6 years of known crops. Sample up to ~150 (stratify so every `RotationClass` has fields if possible).
2. **Features per field:**
   - SSURGO at the centre: `awc_mm_per_m`, `om_pct`, `hydgrp`, `weg`, `slope_pct`
   - `irrigated`: OpenET summer (Jun–Aug) ET above a threshold you calibrate on obvious pivots, or MODIS July–August NDVI peak ≥ 0.75 in at least half of the years. Record which method.
   - `rotation_class` (§6.12)
   - MODIS NDVI drought anomalies for 2012 and 2022; OpenET annual ET median; ECOSTRESS summer ESI mean (only if available)
3. **Similarity to each demo field:** z-score `awc_mm_per_m`, `om_pct`, `slope_pct`, `wei_t_ac_yr` across the pool; hydrologic group as ordinal A=1…D=4; **require the same `irrigated` value as the demo field**. Distance = Euclidean on these; `similarity = 1 / (1 + distance)`. Keep the 30 most similar.
4. **Groups:** group the 30 by `rotation_class`. Per group: `n`, median OpenET annual ET, median NDVI drop 2012 and 2022 (as % vs 2016–2019 normal), mean summer ESI. Set `matches_rotation` with the README §7.2 mapping and `is_current` if it equals the demo field's class. Drop groups with n < 3 into `mixed`.
5. Write `out/web/field/{fid}/neighbors.json` with simplified polygons (≤ 60 vertices each) so the file stays small.

## 7. Acceptance checks (run before telling the team a file is ready)

- [ ] Every JSON validates against README §8.3 (keys, types, IDs) and starts with `_meta`.
- [ ] `fields.json` has exactly `f1`, `f2`, `f3`, each with a real polygon and 8-year `crop_history`.
- [ ] `weather_daily.csv` covers 2000-01-01 → 2025-12-31 with no gaps longer than 1 day; annual precipitation in Finney is roughly 400–550 mm; summer Tmax often > 32 °C.
- [ ] `rs_mj_m2` values mostly 5–30 (MJ/m²/day). If they're 1–8, you left them in kWh.
- [ ] NDVI between −0.2 and 1.0; irrigated corn peaks ~0.8+ in July–August.
- [ ] SMAP root-zone between ~0.05 and 0.45 m³/m³.
- [ ] `aws_0_100_mm` in a plausible range (sandy soils ~60–120 mm, silt loams ~150–220 mm).
- [ ] NASS yields have units and `level` filled.
- [ ] `neighbors.json` groups have `n ≥ 3`, and at least one group matches R1, R2, R4 or R5 for each demo field (say so to M if not).
- [ ] No API keys in any committed file.

## 8. Handover checklist

- [ ] `data-pipeline/README.md` explains how to run each step and the env vars.
- [ ] `out/processed/` and `out/web/` committed on branch `role/data`.
- [ ] `docs/DATA_SOURCES.md` written (used + skipped datasets, with links).
- [ ] Told M and F which files are final and anything missing (e.g. "no ECOSTRESS for f3").
