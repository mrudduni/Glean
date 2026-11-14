# Field boundaries

Field Shift needs a polygon for each field so it can clip soil, weather, and satellite data and read the crop history. This file covers open datasets and models that supply field polygons, their licences, and how to access them. CDL and CSB data content is covered in `research/01_datasets/usda_us/cropland_data_layer.md`; this file covers their role as boundaries.

## Summary

| Region | First choice | Fallback |
| --- | --- | --- |
| United States | USDA Crop Sequence Boundaries (CSB), which also carry 8 years of crop history | FTW global predictions, then user drawing |
| Outside the US (including India) | Fields of The World (FTW) global predictions for 2024 and 2025 | User drawing; run the FTW model on a fresh Sentinel-2 pair |
| Anywhere, for editing | Terra Draw in the browser (see `frontend.md`) | n/a |

Always let the farmer correct the polygon. Every model makes errors at field edges, and small fields are the hardest case.

## USDA Crop Sequence Boundaries (CSB)

- What: field polygons derived from the CDL pixel history, with the crop sequence attached. NASS says the data come from "satellite imagery and publicly available data" and not from producers or the Farm Service Agency (https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php).
- Coverage and dates: the current release covers 2018 to 2025, released 27 March 2026. Datasets span 8-year windows for all years from 2008 (same page). The page also says "Current version is v2024", which conflicts with the 2018 to 2025 release date (not confirmed which label is current).
- Licence: NASS calls the CDL public domain (see the CDL file). The CSB page says the data are "open source"; a formal licence statement for CSB was not found (not confirmed). Treat it as US Government public data and cite NASS and ERS.
- Access: national and state zip downloads (file geodatabase). Convert once to GeoParquet with `pyogrio` and query by bounding box with DuckDB (`backend.md`). Do not commit the files to the repo.
- Fit: very good. A click on the map can return the field and its rotation history, which seeds the farmer's "current rotation" strategy.

## Fields of The World (FTW)

FTW is a benchmark, a set of models, and now a global prediction dataset.

| Item | Details | Licence | Source |
| --- | --- | --- | --- |
| Global predictions | 10 m field polygons for 2024 (1.62 billion) and 2025 (1.55 billion), 3.17 billion across 241 countries and territories, from the FTW PRUE model | CC-BY-4.0 | https://fieldsofthe.world/ and https://source.coop/ftw/global-data |
| Data catalog | STAC catalog with predictions, confidence, and prediction Zarr | CC-BY-4.0 ("Catalog metadata and data are published under CC-BY-4.0 by Taylor Geospatial and collaborators") | https://github.com/fieldsoftheworld/ftw-data-catalog |
| Harmonized field data | About 2.94 million open field boundaries collected from other sources, 2024 and 2025 | CC-BY-4.0 (per search snippet) | https://source.coop/ftw/harmonized-field-data |
| Benchmark | Labelled chips from 24 countries on 4 continents; licence differs per country (for example CC-BY-4.0, CC-BY-2.0, CC0-1.0) | Per country | https://source.coop/kerner-lab/fields-of-the-world |
| India subset | Field boundaries for India from Wang, Waldner, and Lobell's smallholder delineation work | Not confirmed | https://source.coop/kerner-lab/fields-of-the-world-india |
| Baseline code | Training and inference code | MIT | https://github.com/fieldsoftheworld/ftw-baselines |
| `ftw-tools` CLI | Runs FTW models and downloads imagery | MIT, version 1.4.3 (2025-08-19) | https://pypi.org/pypi/ftw-tools/json |

Notes:

- The PRUE model was trained on the CC-BY subset of the benchmark (https://source.coop/ftw/global-data, search snippet).
- CC-BY-4.0 needs attribution. List FTW and Taylor Geospatial Institute in the app footer and the submission References.
- Predictions at 10 m will merge or split small fields. Show the FTW confidence value when it is available.
- The FTW site says the predictions are also listed on the Earthmover marketplace (https://fieldsofthe.world/). We have not checked those terms.

## fiboa (field boundary schema)

fiboa is a GeoParquet schema for field boundaries used by FTW and others. The `fiboa-cli` package is 0.30.0 (2026-10-30, Apache-2.0, https://pypi.org/pypi/fiboa-cli/json). Using the fiboa core fields (`id`, `geometry`, `area`, `determination_method`) for our own stored fields makes import and export simple.

## SAM-based delineation

| Tool | Version | Licence | Source |
| --- | --- | --- | --- |
| segment-geospatial (samgeo) | 1.4.2 (2026-08-22) | MIT | https://pypi.org/pypi/segment-geospatial/json and https://github.com/opengeos/segment-geospatial |
| SAM 2 (Meta) | 1.1.0 (2024-12-21) | Apache-2.0 | https://github.com/facebookresearch/sam2 |

Segment Anything models can outline a field from one click on a high-resolution image. They work best on sub-metre imagery such as NAIP (US only) and less well on 10 to 30 m Sentinel-2 or HLS. They need a GPU for comfortable speed (not confirmed for SAM 2 small variants on CPU). Use this as a stretch feature: "click your field on the NAIP image".

## Google Agricultural Landscape Understanding (ALU)

Google's ALU segments fields, trees, and water bodies at national scale for smallholder regions, including India, with history from 2011 (https://deepmind.google/science/agricultural-understanding/). It is offered through the Agricultural Understanding API (https://developers.google.com/agricultural-understanding/api). Terms, cost, and redistribution rights were not checked (not confirmed). It is a strong option for India if the terms allow an open-source app, but do not depend on it until the terms are read.

## Other national sources (not checked in this session)

- Many EU countries publish farmer parcel data (LPIS or IACS), and several appear in the FTW benchmark with their own licences.
- India: state land-record cadastral maps (Bhulekh portals) differ by state and often restrict reuse (not confirmed).

## Recommendation

1. US demo: click a field to fetch its CSB polygon and crop history from a GeoParquet extract for the demo county.
2. Non-US demo, if any: fetch the FTW 2025 polygon for the clicked point from Source Cooperative.
3. Always allow drawing or editing with Terra Draw.
4. Store fields in fiboa-compatible GeoParquet (demo) or PostGIS (long term), with a `source` field (`csb`, `ftw`, `drawn`) and licence.

## Sources

- CSB: https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php
- FTW: https://fieldsofthe.world/
- FTW global data: https://source.coop/ftw/global-data
- FTW data catalog: https://github.com/fieldsoftheworld/ftw-data-catalog
- FTW harmonized data: https://source.coop/ftw/harmonized-field-data
- FTW benchmark: https://source.coop/kerner-lab/fields-of-the-world
- FTW India: https://source.coop/kerner-lab/fields-of-the-world-india
- FTW baselines: https://github.com/fieldsoftheworld/ftw-baselines
- segment-geospatial: https://github.com/opengeos/segment-geospatial
- SAM 2: https://github.com/facebookresearch/sam2
- Google ALU: https://deepmind.google/science/agricultural-understanding/ and https://developers.google.com/agricultural-understanding/api
- PyPI JSON API, queried 14 November 2026: https://pypi.org/pypi/{package}/json
