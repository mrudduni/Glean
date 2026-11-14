# Research index

Phase 1 research for Field Shift, gathered on 2026-11-13. There are 39 files and about 400 KB of notes. Every file lists its source URLs at the bottom. Facts the agents could not verify carry the label "not confirmed". We downloaded no data files.

## 00_challenge, the official problem

| File | Contents |
|---|---|
| [details.md](00_challenge/details.md) | Verbatim Details tab: background, objectives, and the five groups of considerations. |
| [resources.md](00_challenge/resources.md) | All 25 linked resources (23 NASA and US, 2 ESA) with links and stated uses. |

## 01_datasets/nasa

| File | Key facts |
|---|---|
| [smap.md](01_datasets/nasa/smap.md) | Surface soil moisture (top 5 cm) every 2 to 3 days. The L4 product adds root-zone moisture. |
| [gpm_imerg.md](01_datasets/nasa/gpm_imerg.md) | Precipitation at 0.1 degree and 30 minutes. Early, Late, and Final runs trade latency for accuracy. |
| [landsat_hls.md](01_datasets/nasa/landsat_hls.md) | Landsat Collection 2 surface reflectance at 30 m. HLS merges Landsat and Sentinel-2. |
| [modis_viirs.md](01_datasets/nasa/modis_viirs.md) | NDVI and EVI at 250 m, plus ET, LST, and land cover. VIIRS continues MODIS. |
| [nasa_power.md](01_datasets/nasa/nasa_power.md) | Daily point weather from a REST API with no key. Agroclimatology parameters. |
| [srtm.md](01_datasets/nasa/srtm.md) | 30 m elevation (SRTMGL1, NASADEM). We derive slope for erosion. |
| [ecostress.md](01_datasets/nasa/ecostress.md) | 70 m LST, ET, and the evaporative stress index. Overpass time drifts and the record has gaps. |
| [gedi.md](01_datasets/nasa/gedi.md) | Lidar canopy height and biomass from 25 m footprints. L4B grid at 1 km. |
| [grace.md](01_datasets/nasa/grace.md) | Monthly water storage since 2002, at 3 degree native resolution on a 0.5 degree grid. GSFC drought indicators are weekly at 0.125 degree. |
| [nldas_gldas.md](01_datasets/nasa/nldas_gldas.md) | NLDAS-2 is hourly at 0.125 degree from 1979. GLDAS-2.1 is 3-hourly at 0.25 degree. |
| [access_tooling.md](01_datasets/nasa/access_tooling.md) | Earthdata Login, CMR, AppEEARS, `earthaccess`, GIBS, Giovanni, and S3 access, which works only from us-west-2. |

## 01_datasets/usda_us

| File | Key facts |
|---|---|
| [cropland_data_layer.md](01_datasets/usda_us/cropland_data_layer.md) | Annual crop map (30 m, 10 m from 2024). Crop Sequence Boundaries gives 8-year rotations per field. No key needed. |
| [ssurgo_statsgo.md](01_datasets/usda_us/ssurgo_statsgo.md) | Soil properties through the Soil Data Access SQL API. No key needed. Column names still need a check before coding. |
| [web_soil_survey.md](01_datasets/usda_us/web_soil_survey.md) | Interactive soil maps. Scripts should use SDA instead. |
| [prism.md](01_datasets/usda_us/prism.md) | 800 m and 4 km daily climate from 1981. Normals cover 1991 to 2020. |
| [nass_quickstats.md](01_datasets/usda_us/nass_quickstats.md) | County yields and acreage. Needs a free key and returns at most 50,000 rows per call. |
| [ams_market_news.md](01_datasets/usda_us/ams_market_news.md) | Crop prices. The MARS API needs an eAuthentication key. |
| [openet.md](01_datasets/usda_us/openet.md) | Field-scale ET from a six-model ensemble. Needs a key. Coverage claims conflict between sources. |
| [usgs_nwis.md](01_datasets/usda_us/usgs_nwis.md) | Groundwater and streamflow. The legacy service retires in early 2027, so we use the OGC APIs. |
| [naip.md](01_datasets/usda_us/naip.md) | 0.6 m aerial imagery. Each state is flown every 2 to 3 years. |
| [nlcd.md](01_datasets/usda_us/nlcd.md) | Annual NLCD at 30 m for 1985 to 2024. |
| [cocorahs.md](01_datasets/usda_us/cocorahs.md) | Volunteer rain gauges under CC BY 4.0, for checking IMERG. |
| [landfire.md](01_datasets/usda_us/landfire.md) | Vegetation and fuel layers. A minor input for rotations. |
| [ag_data_commons.md](01_datasets/usda_us/ag_data_commons.md) | Rotation and soil-health trial datasets (DRIVES, NAPESHM, SoilHealthDB). |

## 01_datasets/global

| File | Key facts |
|---|---|
| [gaez.md](01_datasets/global/gaez.md) | Crop suitability for about 53 crops. v5 (2025) adds 1 km layers and an API. |
| [sentinel2.md](01_datasets/global/sentinel2.md) | 10 m imagery with red-edge bands and a 5-day revisit. Covers the CDSE APIs. |
| [era5.md](01_datasets/global/era5.md) | Reanalysis at 0.25 degree from 1940. ERA5-Land is 0.1 degree from 1950. |

## 02_hackathon

| File | Key facts |
|---|---|
| [event.md](02_hackathon/event.md) | The hackathon runs 14 to 15 November 2026. Global winners are announced 26 January 2027. |
| [rules_judging.md](02_hackathon/rules_judging.md) | Judges score Impact, Creativity, Validity, Relevance, and Presentation from 1 to 5. The demo is a video of 30 seconds or less, or at most 7 slides. A Global Award requires NASA data. The project needs an open-source licence. |
| [teams_tab.md](02_hackathon/teams_tab.md) | 1,605 teams have joined this challenge. The file samples 876 of them. |
| [past_winners.md](02_hackathon/past_winners.md) | Farm winners from 2023 to 2025 and the patterns they share. |
| [space_agency_partners.md](02_hackathon/space_agency_partners.md) | 17 partners. Only ESA has data on this challenge's resource list. |

## 03_domain

| File | Key facts |
|---|---|
| [existing_tools.md](03_domain/existing_tools.md) | 17 tools reviewed. None compares three or more whole rotations for one field with explanations. |
| [agronomy_rotations.md](03_domain/agronomy_rotations.md) | Nitrogen credits, pest breaks, FAO-56 crop coefficients, RUSLE factors, GDD, and frost thresholds, all with sources. |
| [science_methods.md](03_domain/science_methods.md) | Indices, drought metrics, ETo, phenology, regridding, and TOPSIS ranking, each rated core, stretch, or later. |
| [papers.md](03_domain/papers.md) | 17 papers, each checked against Crossref or Europe PMC. |
| [open_source.md](03_domain/open_source.md) | 30 Python libraries with licences and versions. |

## Open questions from the research

- OpenET coverage: the FAQ says 23 western states, while a 2025 NASA/DRI release says all 48 states.
- FAO-56 gives alfalfa a mid-season Kc of 0.95 in Table 12 and 1.05 in the chapter text.
- The SSURGO column names and the SDA spatial query need a live test before we write code.
- The GAEZ v4 licence is unconfirmed, while v5 is CC-BY-4.0.
