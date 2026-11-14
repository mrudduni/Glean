# Field Shift resources tab (official list)

Source: https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/?tab=resources
Scraped on 2026-11-13. Each dataset has a deeper write-up in `../01_datasets/`.

## NASA data and resources

| # | Resource | Official link | Use stated on the challenge page |
|---|----------|---------------|-------------------------|
| 1 | SMAP (Soil Moisture Active Passive) | https://www.earthdata.nasa.gov/data/platforms/space-based-platforms/smap | Global surface soil moisture + freeze/thaw, every 2–3 days. Drought stress, infiltration, early crop stress. |
| 2 | GPM & IMERG | https://gpm.nasa.gov/data | Global precip rate/accumulation. Rainfall reliability, extreme storms, erosion risk. Worldview IMERG layers downloadable as images. |
| 3 | Landsat (30 m) | https://earthexplorer.usgs.gov/ | Reflectance, NDVI, plant stress, bare ground, seasonal change. |
| 4 | MODIS/VIIRS (250–1000 m) | https://lpdaac.usgs.gov/products/ , https://search.earthdata.nasa.gov/search?q=VIIRS | Vegetation indices, crop vigor, seasonal transitions. |
| 5 | NASA POWER | https://power.larc.nasa.gov/ | Agroclimatology: temp, humidity, radiation; crop water use, frost risk, climate suitability. |
| 6 | SRTM | https://www.earthdata.nasa.gov/data/instruments/srtm | Elevation: slope, runoff, erosion risk, water flow. |
| 7 | ECOSTRESS | https://ecostress.jpl.nasa.gov/data | High-res LST + evapotranspiration. Heat/water stress hotspots, field microclimate. |
| 8 | USDA Ag Data Commons | https://www.nal.usda.gov/services/agdatacommons | Open ag datasets: soils, crops, management, phenology. |
| 9 | Web Soil Survey (NRCS) | https://websoilsurvey.nrcs.usda.gov/app/ | Official US soil maps: OM, texture, drainage, erosion, hydrologic ratings. |
| 10 | Cropland Data Layer / CropScape | https://nassgeodata.gmu.edu/CropScape/ | Annual 30 m crop-type map (US). Existing rotations, bare fields, SI labels. |
| 11 | PRISM (Oregon State) | https://prism.oregonstate.edu | US daily/monthly/30-yr normals; precip, temp, dewpoint, frost dates; topography-aware. |
| 12 | SSURGO / STATSGO2 | https://www.nrcs.usda.gov/resources/data-and-reports/soils | Soil attributes: texture, OM, drainage, HSG, erosion factors, AWC. |
| 13 | NAIP | https://naip-usdaonline.hub.arcgis.com/ | ~1 m US aerial imagery; field boundaries, bare soil, validation. |
| 14 | NLCD (USGS) | https://www.usgs.gov/centers/eros/science/national-land-cover-database | 30 m land cover over decades; landscape context. |
| 15 | NLDAS / GLDAS | https://www.earthdata.nasa.gov/ (search "NLDAS"/"GLDAS" in Earthdata Search) | Gridded sub-daily temp, precip, soil moisture, ET, radiation. Drought onset. |
| 16 | FAO GAEZ | https://gaez.fao.org | Global crop suitability, soil constraints, yield potential. |
| 17 | CoCoRaHS | https://www.cocorahs.org/Maps | Crowd-sourced daily precip (N. America). Validate IMERG. |
| 18 | USGS NWIS | https://waterdata.usgs.gov/nwis | Groundwater levels, streamflow, water quality. Irrigation availability. |
| 19 | USDA AMS Market News | https://www.ams.usda.gov/market-news | Commodity prices + demand. Market viability of rotation crops. |
| 20 | USDA NASS QuickStats | https://quickstats.nass.usda.gov | County/state yields, acreage, production history. Calibration. |
| 21 | OpenET | https://openetdata.org | Field-scale ET, western US. Crop water demand, irrigation. |
| 22 | USFS LANDFIRE | https://www.landfire.gov | Vegetation type/condition, fuels, landscape characteristics. |
| 23 | GEDI | https://gedi.umd.edu/data | Lidar canopy height, LAI, L4 biomass. Surrounding land-cover structure. |

The Details tab also names GRACE and GRACE-FO (groundwater and water-storage trends), but the Resources tab does not link them.

## Space agency partner resources (ESA)

| # | Resource | Link | Use |
|---|----------|------|-----|
| 24 | Copernicus Sentinel-2 | https://dataspace.copernicus.eu | 10–20 m multispectral, red-edge/NIR/SWIR. NDVI/EVI, bare soil, crop stress. |
| 25 | ERA5 (ECMWF) | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview | Hourly global reanalysis: temp, precip, wind, humidity, soil temp, radiation. |

## Disclaimers on the page
- NASA does not endorse non-US-government entities. Each third-party site sets its own data-use terms, and teams must follow them.
- The page says NASA may add more resources before the hackathon begins.
