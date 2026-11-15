# Data sources

Produced by `data-pipeline/process/build_sources.py` (D). The machine-readable version is
`data-pipeline/out/web/sources.json`, which lists only the sources that reached the app.

## Used

| Tag | Dataset | Provider | Resolution | Period | Used for |
|---|---|---|---|---|---|
| `POWER` | [NASA POWER daily (AG community)](https://power.larc.nasa.gov/) | NASA Langley Research Center | 0.5° × 0.625° grid, daily | 1981–2025 (solar from 1984) | Rotation Replay weather, reference ET, heat, frost and wind days |
| `GRACE` | [JPL GRACE/GRACE-FO Mascon RL06.3 (CRI filtered)](https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4) | NASA JPL / PO.DAAC | 0.5° grid; ~300 km true resolution | 2002-04 → latest (gap 2017-07 → 2018-05) | Regional aquifer / water-storage trend in the water outlook |
| `SRTM` | [SRTM Global 1 arc second DEM (SRTMGL1 v3)](https://lpdaac.usgs.gov/products/srtmgl1v003/) | NASA LP DAAC, via AppEEARS | 30 m | February 2000 | Field slope and cold-air low-spot flag |
| `SSURGO` | [SSURGO via Soil Data Access](https://sdmdataaccess.sc.egov.usda.gov/) | USDA NRCS | Map units at 1:12,000–1:24,000 | Current release | Soil water holding, erodibility, soil-health inputs and neighbour matching |
| `CSB` | [Crop Sequence Boundaries 2018–2025 (rev23)](https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/) | USDA NASS | Field polygons from 30 m CDL | 2018–2025 | Demo field outlines, crop history, detected rotation, neighbour pool |
| `NASS` | [Quick Stats](https://quickstats.nass.usda.gov/) | USDA NASS | Finney County, SW Kansas district, Kansas | 2000–2025 (prices 2015–2024) | Yields, prices and the local-market check |
| `OpenET` | [OpenET Ensemble](https://etdata.org/) | OpenET (NASA, USGS, DRI, EDF, Google and partners) | 30 m, monthly | 2016 → latest | Replay validation and neighbours' real water use |
| `PRISM` | [PRISM daily (4 km)](https://prism.oregonstate.edu/) | PRISM Climate Group, Oregon State University | 4 km, daily | 1991–2025 | 1991–2020 climate normals vs 2016–2025, ground-based check of POWER |
| `USGS` | [USGS Water Data APIs — groundwater field measurements](https://api.waterdata.usgs.gov/) | U.S. Geological Survey | Individual wells | 2000–2025 | Local aquifer trend near each field |
| `FAO56` | [FAO Irrigation and Drainage Paper 56 (Penman-Monteith, crop coefficients)](https://www.fao.org/4/x0490e/x0490e00.htm) | FAO | Method, not a dataset | 1998 | Reference ET and crop water demand in the Replay |
| `MODEL` | [Field Shift Rotation Replay model](https://github.com/mrudduni/Team-Brackets) | Team Brackets (M) | Field, daily/annual | 2016–2025 | Rotation Replay results and the calendar |

## Planned, not delivered yet

| Tag | Dataset | Why it's missing |
|---|---|---|
| `IMERG` | [GPM IMERG Final Run daily (GPM_3IMERGDF v07)](https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDF_07/summary) | needs an Earthdata login (or Giovanni CSVs in raw/imerg/) |
| `SMAP` | [SMAP L4 Global 3-hourly 9 km Surface and Root Zone Soil Moisture (SPL4SMGP v8)](https://nsidc.org/data/spl4smgp) | AppEEARS task needs an Earthdata login |
| `MODIS` | [MODIS Terra Vegetation Indices 16-day (MOD13Q1 v6.1)](https://lpdaac.usgs.gov/products/mod13q1v061/) | AppEEARS needs an Earthdata login; ORNL subset fallback still downloading |
| `ECOSTRESS` | [ECOSTRESS L3 ET (ECO_L3T_JET v2) and L4 ESI (ECO_L4T_ESI v2)](https://lpdaac.usgs.gov/products/eco_l3t_jetv002/) | AppEEARS task needs an Earthdata login |

## Access notes

- MODIS NDVI comes from AppEEARS when available, otherwise from the ORNL DAAC MODIS/VIIRS
  Land Product Subsets service (https://modis.ornl.gov/data/modis_webservice.html), which needs no login.
- Terrain uses SRTM from AppEEARS when available, otherwise USGS 3DEP 1/3 arc-second elevation
  (https://www.usgs.gov/3d-elevation-program) through the National Map ImageServer.
- Groundwater uses the new USGS Water Data APIs; the legacy `waterservices.usgs.gov/nwis/gwlevels`
  service was decommissioned in fall 2025.
- PRISM series use the same time-series endpoint as the PRISM Data Explorer.

## Skipped on purpose

| Dataset | Why |
|---|---|
| GEDI | Lidar canopy height/structure; Kansas cropland has no canopy structure that matters for rotation choice and footprints are sparse. |
| LANDFIRE | Wildland fuel and vegetation types; built for fire management, not cropland rotations. |
| NLCD | Land cover every 2–3 years at 30 m; CDL / Crop Sequence Boundaries already give the crop each year. |
| ERA5 | Global reanalysis at ~31 km; NASA POWER covers the same need here. ERA5 is the path to taking the tool global. |
| GLDAS | Global land model at 0.25°; SMAP L4 gives assimilated soil moisture at 9 km. Also a path to going global. |
| NLDAS | North American land model at 1/8°; overlaps POWER + SMAP and adds a third weather source without a clear gain. |
| STATSGO2 | Generalised 1:250,000 soils; SSURGO is far more detailed for field-scale decisions. |
| Ag Data Commons | A catalogue, not a dataset; the specific USDA datasets we need (CSB, NASS, SSURGO) are used directly. |

## COULD tier, not done

| Dataset | Status |
|---|---|
| HLS | Harmonized Landsat Sentinel-2 30 m NDVI — COULD tier, not done; MODIS covers the season curves. |
| CoCoRaHS | Volunteer rain gauges — COULD tier, not done; precip_check.cocorahs_mm is null. |
| GAEZ | FAO future crop suitability — COULD tier, not done. |
| AMS | USDA AMS local cash prices — COULD tier, not done; NASS Kansas prices are used. |
