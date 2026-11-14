# FAO WaPOR v3

WaPOR is FAO's portal for water productivity from remote sensing. It maps actual evapotranspiration and interception (AETI), reference ET, net primary production, and relative soil moisture. It covers the globe at 300 m and some regions at finer levels.

## Key facts

| Item | Value |
|---|---|
| Global level (L1) resolution | 300 m (the probe read a pixel size of 0.0029 degree) |
| Finer levels | 100 m (L2) for Africa, the Near East, Sri Lanka, Pakistan and Colombia; 20 m (L3) for selected areas in partner countries |
| Steps | dekadal (about 10 days), monthly, annual |
| Record | 2018 onward for v3 |
| Catalogue | `https://data.apps.fao.org/gismgr/api/v2/catalog/workspaces/WAPOR-3/mapsets` |
| Files | Cloud-Optimised GeoTIFFs on Google Cloud Storage, for example `https://storage.googleapis.com/fao-gismgr-wapor-3-data/DATA/WAPOR-3/MAPSET/L1-AETI-A/WAPOR-3.L1-AETI-A.2024.tif` |
| Auth | None |
| Licence | CC BY 4.0 for the global layers. Some 20 m local layers use CC BY-SA 4.0 or CC BY-NC-SA 4.0, so check each mapset. |

Sources: https://data.fao.org/catalog/dataset/b860007a-6c03-4210-b16b-3b2ecba5f029 and https://www.fao.org/land-water/news/detail/WaPOR-v3-data-now-available-in-the-new-portal/en

## What the probe found

| Point | AETI 2024 (mm per year) | Relative soil moisture, August 2024 dekad 1 |
|---|---|---|
| Karnal cropland | 751.5 | 0.711 |
| Ludhiana cropland | 783.1 | 0.612 |
| Nashik cropland | 784.7 | 0.579 |
| Iowa | 569.1 | 0.692 |

Each pixel read took about 25 to 30 seconds.

## Role in the tool

- An independent estimate of actual ET for the field's history. We can compare it with ECOSTRESS and with our modelled crop ET, which is a validation step the judges will value.
- WaPOR is not NASA data. It supports the NASA sources and does not replace them.

## Gaps

- We have not checked how WaPOR splits AETI between seasons at Karnal. The annual total mixes rice and wheat.
- India has no L2 or L3 coverage, so Karnal is limited to 300 m. Pakistan's Punjab has L2 at 100 m, which could serve as a nearby comparison.

## Sources

- https://data.fao.org/catalog/dataset/b860007a-6c03-4210-b16b-3b2ecba5f029
- https://www.fao.org/land-water/news/detail/WaPOR-v3-data-now-available-in-the-new-portal/en
- Probe output: `research/04_data_probes/samples/global_probe_results.json`, key `wapor`
