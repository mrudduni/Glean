# OpenET

## What it is

OpenET delivers satellite-based actual evapotranspiration (ET) at field scale. It is a consortium led by NASA, the Desert Research Institute (DRI) and Environmental Defense Fund, with USGS, California State University Monterey Bay, Google Earth Engine, HabitatSeven and several universities. The website now lives at etdata.org (openetdata.org redirects there). Tools are the Data Explorer, the FARMS tool for individual farmers and ranchers, and the OpenET API.

## Models in the ensemble

OpenET runs six models on Google Earth Engine and reports each model plus an ensemble value.

| Model | Version listed | Approach |
| --- | --- | --- |
| ALEXI/DisALEXI | 0.0.32 | Full surface energy balance using thermal data |
| eeMETRIC | 0.20.26 | Full surface energy balance with internal calibration |
| geeSEBAL | 0.2.2 | Full surface energy balance |
| PT-JPL | 0.2.1 | Priestley-Taylor, simplified |
| SIMS | 0.1.0 | Crop coefficient from reflectance and crop type (agricultural lands) |
| SSEBop | 0.2.6 | Operational simplified surface energy balance |

The methods page has a section on how the ensemble value is computed. That section was not read, so the averaging and outlier rule is not confirmed here.

## Inputs

Landsat is the primary satellite input, with GOES, Sentinel-2, Suomi NPP, Terra and Aqua as supplements. Gridded weather comes from gridMET, Spatial CIMIS, DAYMET, PRISM and NLDAS. Reference ET uses the ASCE Standardized Penman-Monteith grass reference (ETo), computed from gridMET and bias-corrected with nearly 800 quality-controlled agricultural weather stations. Daily ET between clear Landsat overpasses is filled by interpolating the fraction of reference ET and multiplying by daily ETo. Ancillary inputs include USDA crop type maps, USDA soils, USGS elevation and land use, irrigated lands maps, and digitized field boundaries.

## Spatial and temporal resolution

- 30 m by 30 m (0.22 acre).
- Daily, monthly and annual totals. The API docs state monthly ET from 2000 to present and a rolling archive of daily ET from 2016 to present. Recent data can change for up to six months.
- The Data Explorer shows a rolling 5 to 6 year archive. The API reaches further back (the site says 25 or more years in select regions).

## Coverage

Sources disagree, so the tool should check coverage for the farm at run time.

- OpenET launched in 2021 for 17 western states (Arizona, California, Colorado, Idaho, Kansas, Montana, Nebraska, Nevada, New Mexico, North Dakota, Oklahoma, Oregon, South Dakota, Texas, Utah, Washington, Wyoming). The 2020 OpenET FAQ snippet confirmed the first twelve names; the last five come from background knowledge.
- It expanded to 23 western states in 2023. The OpenET FAQ page still says it "covers 23 western U.S. states" plus raster layers for the Mississippi Alluvial Plain.
- A NASA press release republished by DRI states that on 15 December (2025, per a news report dated 17 December 2025) data became available for all 48 contiguous states across all tools. The API docs now describe data "across the United States".

## Access methods

### Data Explorer and FARMS

- Data Explorer: https://explore.etdata.org/ (view field-scale monthly ET; download limited amounts free).
- FARMS tool: https://farms.etdata.org

### OpenET API (version 3.2, OpenAPI 3.1)

Base server: https://openet-api.org, with the OpenAPI document at https://openet-api.org/openapi.json. Endpoints listed on the public server:

| Group | Endpoints |
| --- | --- |
| Account | GET /account/status (current quota), GET /account/storage, POST /account/upload, POST /account/decrypt |
| Raster data | POST /raster/timeseries/point, /raster/timeseries/polygon, /raster/timeseries/multipolygon, /raster/geotiff/composite, /raster/geotiff/stack, /raster/export/composite, /raster/export/stack, /raster/export/multipolygon, GET /raster/export/track, POST /raster/metadata, /raster/visual/tile_cache, /raster/visual/animate |
| Pre-computed field data | POST /geodatabase/metadata/ids, /geodatabase/metadata/properties, /geodatabase/metadata/boundaries, /geodatabase/timeseries |

The "pre-computed field data" group serves OpenET's own field boundary geodatabase. The tool can look up field IDs, fetch boundaries and pull field-average ET time series without uploading a polygon.

Request body fields and the exact header name for the key were not read in this research. The documented pattern in the OpenET GitBook quick start (not fetched) should be checked before coding. A likely request shape is:

```python
import requests
r = requests.post(
    "https://openet-api.org/raster/timeseries/point",
    headers={"Authorization": API_KEY},          # header name not confirmed
    json={"date_range": ["2023-01-01", "2023-12-31"],
          "interval": "monthly", "geometry": [-120.3, 36.8],
          "model": "Ensemble", "variable": "ET",
          "reference_et": "gridMET", "units": "mm",
          "file_format": "JSON"},               # field names not confirmed
    timeout=120,
)
```

### Google Earth Engine

OpenET data are in the Earth Engine public data catalog (tag "openet"). OpenET recommends this route for large volumes. Earth Engine access needs a Google account and a registered Cloud project.

## Authentication and quotas

- An OpenET account and API key are required for the API. Register at https://account.etdata.org/register.
- The API is free but has quotas. Each request can cover up to 50,000 acres. Raster queries with custom shapefiles accept up to 50 polygons. Geodatabase queries accept up to 100 field IDs.
- Users are subject to monthly request limits (the number was not stated). Linking a Google Cloud project ID to the OpenET profile raises quota limits.
- High load can cause timeouts while servers scale up.

## Terms of use

OpenET has terms of service at https://etdata.org/terms-of-service/ and https://openet.gitbook.io/docs/terms-of-service. These were not read. The FAQ states that data are for informational purposes, should not be taken as professional advice, and should not be relied on in legal or regulatory enforcement actions, and that uses outside the terms need written permission.

## Accuracy

OpenET says it completed a large ET accuracy assessment and intercomparison study and keeps an "accuracy and known issues" page (https://etdata.org/accuracy-known-issues/). Accuracy numbers were not extracted here.

## Limitations

- Coverage outside the original western states is new, and accuracy there may differ from the western validation.
- Clouds reduce Landsat overpasses, which lowers confidence in daily values in cloudy regions and seasons.
- Recent months are revised for up to six months.
- Quotas limit large-area pulls through the API.
- ET is consumptive use, not applied irrigation. Precipitation and soil storage must be accounted for to estimate irrigation.

## How it plugs into the rotation tool

- OpenET gives historical crop water use for the farm's fields by year. Joined with CDL crop labels, it shows how much water each crop in the current rotation used.
- The tool can compare ET of candidate crops in nearby fields (same soil and climate) to estimate the water demand of each rotation, a key risk for irrigated farms on declining aquifers (see USGS groundwater data).
- Net ET (ET minus effective precipitation from PRISM) approximates irrigation need.
- Spread among the six models gives a ready-made uncertainty band for the data gaps section.

## Sources

- https://openetdata.org (redirects to https://etdata.org/)
- https://etdata.org/api/
- https://etdata.org/methods/
- https://etdata.org/faqs/
- https://openet-api.org
- https://openet.gitbook.io/docs
- https://account.etdata.org/register
- https://developers.google.com/earth-engine/datasets/tags/openet
- https://www.dri.edu/nasa-partners-expand-crucial-water-tracking-program/
- https://mavensnotebook.com/2025/12/17/openet-expands-satellite-based-water-use-data-across-48-states-providing-critical-information-to-farmers-and-water-managers-across-the-nation/ (search snippet only)
- https://texasgroundwater.org/wp-content/uploads/2020/11/OpenET-FAQ-FINAL_Nov2020.pdf (search snippet only)
