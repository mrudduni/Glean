# US agriculture API probe

Run on 2026-11-14 with `scripts/probe_us.py`. Raw results are in `samples/us_probe_results.json`. No API keys were used or stored. Probes that need a key record the no-key reply, so we know how each one fails.

Two test points:

- `iowa_s1`: 42.03, -93.75, central Iowa near the Marsden Farm rotation trial.
- `kansas_sd6`: 39.40, -100.40, cropland inside the Sheridan 6 (SD-6) groundwater management area in Sheridan County, Kansas.

## Summary

| Source | Result | Key needed | Use in the tool |
|---|---|---|---|
| SSURGO through Soil Data Access | Works. Map unit, aggregate and horizon tables return in about 2 s each. | No | Soil water holding, texture, Ksat and pH for the US water balance |
| CropScape CDL point history | Works. 17 years (2008 to 2024) of crop at a point in about 1 s a year. | No | Infers the current rotation for a US field, which India cannot do |
| NASS Quick Stats | `401 {"error":["unauthorized"]}` | Yes (free) | County yields and prices for the US region |
| USGS Water Data OGC API | Works. 20 groundwater sites in a 0.5 degree box around SD-6, with field measurements. | No (rate limited without one) | Well trends next to GRACE for the Kansas region |
| PRISM web service | Works. Monthly 4 km precipitation comes back as a zip. | No | US weather check against IMERG and POWER |
| AMS MyMarketNews | `403`, "Attempt to access the protected resource" | Yes (free) | US cash prices |
| GAEZ v5 | Licence confirmed as CC-BY-4.0 on the FAO data catalogue | No | Suitability layers, global |
| OpenET | Not probed | Yes | Field ET for the US region; needs a team key |

## SSURGO through Soil Data Access

Endpoint: `https://SDMDataAccess.sc.egov.usda.gov/Tabular/post.rest`, POST with `query` and `format=JSON+COLUMNNAME`. The map unit lookup uses `SDA_Get_Mukey_from_intersection_with_WktWgs84('point(lon lat)')`.

| Field | Iowa S1 | Kansas SD-6 |
|---|---|---|
| mukey | 2765522 | 2759231 |
| Map unit | Clarion loam, Bemis moraine, 2 to 6 percent slopes | Keith silt loam, 1 to 3 percent slopes |
| Main component (share) | Clarion (85 percent) | Keith (98 percent) |
| `aws0100wta` (available water, 0 to 100 cm) | 18.64 cm | 20.92 cm |
| `aws0150wta` (0 to 150 cm) | 27.64 cm | 31.42 cm |
| Slope (`slopegradwta`) | 3.5 percent | 2 percent |
| Hydrologic group | B | C |
| Drainage | Well drained | Well drained |
| Topsoil clay, OM, pH (Ap horizon) | 21 percent, 3.5 percent, 6.2 | 22 percent, 2.6 percent, 6.9 |
| Topsoil Ksat | 9.17 micrometres per second | 6 micrometres per second |
| Topsoil AWC (`awc_r`) | 0.21 cm/cm | 0.21 cm/cm |

Points for the engine:

- `aws0100wta` gives total available water for a 1 m root zone directly. For a crop with a different root depth, sum `awc_r` times horizon thickness from the horizon table.
- Field capacity and wilting point come back as `wthirdbar_r` and `wfifteenbar_r` (percent by volume). Iowa Ap: 28.6 and 14.5. Kansas Ap: 29 and 14.
- These are survey estimates (`_r` is the "representative" value), not measurements. The `_l` and `_h` columns give low and high values and can feed the uncertainty bands, as SoilGrids quantiles do for India.
- SSURGO has no gap at either point. Compare SoilGrids at Karnal, where the clay range ran from 3 to 86 percent.

## CropScape CDL point history

Endpoint: `https://nassgeodata.gmu.edu/axis2/services/CDLService/GetCDLValue?year=&x=&y=`. The x and y must be in Albers equal area (EPSG:5070). We convert with pyproj. The reply is XML holding a JSON-like string, for example `{x: 185002.3, y: 2116458.4, value: 1, category: "Corn", color: "#FFD400"}`. It is not valid JSON, so the script parses it with a regular expression.

| Year | Iowa S1 | Kansas SD-6 |
|---|---|---|
| 2008 | Corn | Fallow/Idle |
| 2009 | Soybeans | Winter wheat |
| 2010 | Corn | Winter wheat |
| 2011 | Soybeans | Corn |
| 2012 | Corn | Fallow/Idle |
| 2013 | Soybeans | Winter wheat |
| 2014 | Corn | Corn |
| 2015 | Soybeans | Fallow/Idle |
| 2016 | Corn | Winter wheat |
| 2017 | Soybeans | Corn |
| 2018 | Corn | Fallow/Idle |
| 2019 | Soybeans | Winter wheat |
| 2020 | Corn | Corn |
| 2021 | Soybeans | Fallow/Idle |
| 2022 | Corn | Winter wheat |
| 2023 | Soybeans | Corn |
| 2024 | Corn | Fallow/Idle |

Iowa S1 is a clean corn-soybean rotation for all 17 years. Kansas SD-6 runs a wheat, corn, fallow cycle from 2012 on, which is the classic dryland rotation of the western High Plains. The tool can read the current rotation from CDL in the US instead of asking the farmer. One pixel is 30 m, so a point can fall on a field edge or road; sample the field polygon and take the majority class before trusting it.

The earlier run (`samples/probe_cdl_result.json`) used other points and got Grass/Pasture in Kansas and Developed in California. That shows the edge problem: always check that the point is cropland.

## NASS Quick Stats

`https://quickstats.nass.usda.gov/api/api_GET/` returns HTTP 401 with `{"error":["unauthorized"]}` without a key. Keys are free at https://quickstats.nass.usda.gov/api. Add one as `NASS_API_KEY` in `.env` if we build the US region.

## USGS Water Data OGC API

Endpoint base: `https://api.waterdata.usgs.gov/ogcapi/v0/collections`.

- `monitoring-locations/items?bbox=...&site_type_code=GW` returned 20 groundwater sites (the page limit) in a 0.5 degree box around the SD-6 point. IDs look like `KS014-391512100245301`.
- `field-measurements/items?monitoring_location_id=...` returned 51 records for the first site, 17 visits each with three parameters:
  - `72019` depth to water below land surface: 140.00 ft on 1989-04-07, 146.53 ft on 2013-12-18.
  - `62610` and `62611` water level above NGVD29 and NAVD88.
- That is a drop of 6.5 ft (2.0 m) in 24.7 years, about 0.08 m a year at this well. This is one well with a record that ends in 2013. It is not a regional trend. The Kansas Geological Survey WIZARD database has denser SD-6 wells and should be checked before we show a Kansas trend.

The API returns no rate-limit header without a key. USGS documents a lower limit for anonymous use, so cache the data pack instead of calling live during the demo.

## PRISM

`https://services.nacse.org/prism/data/get/us/4km/ppt/202407` returns `application/zip` with filename `prism_ppt_us_25m_202407.zip`. The filename says 25m, which suggests PRISM now serves its newer grid under the old 4km path. Check the file's grid before use. The old `/data/public/` path returns an HTML page, not data. PRISM asks users to download each file at most twice a day.

## AMS MyMarketNews

`https://marsapi.ams.usda.gov/services/v1.2/reports` returns HTTP 403 without a key. Keys are free after sign-up at https://mymarketnews.ams.usda.gov/mymarketnews-api/. US prices matter only if we build the Kansas region.

## GAEZ licence

The FAO data catalogue records for GAEZ v5 layers state: "This work is made available under the Creative Commons Attribution 4.0 International licence (CC-BY-4.0)". Example record: https://data.fao.org/catalog/iso/e7c45e67-b5b3-48de-b8e5-4e2f62f63d01. The v4 data licence is still not confirmed, so the tool should use v5 layers.

## What this means for the build

- The hackathon demo stays on Karnal. The US probe supports L7 (Kansas SD-6 as a second region) in `../07_plan/feature_ideas.md`.
- A US region would be stronger on data than India: survey soil with no gap, 17 years of observed crops per field, and public well records. That contrast is worth one line in the presentation: the method is the same, and the bands shrink where better local data exists.
- Keys to request before building the US region: NASS, AMS, OpenET.

## Sources

- Soil Data Access: https://sdmdataaccess.sc.egov.usda.gov/
- CropScape web service: https://nassgeodata.gmu.edu/CropScape/
- NASS Quick Stats API: https://quickstats.nass.usda.gov/api
- USGS Water Data APIs: https://api.waterdata.usgs.gov/
- PRISM web service: https://prism.oregonstate.edu/documents/PRISM_downloads_web_service.pdf
- AMS MyMarketNews API: https://mymarketnews.ams.usda.gov/mymarketnews-api/
- GAEZ v5 catalogue record: https://data.fao.org/catalog/iso/e7c45e67-b5b3-48de-b8e5-4e2f62f63d01
