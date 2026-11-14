# FAO GAEZ (Global Agro-Ecological Zones)

GAEZ is a joint FAO and IIASA modelling framework that rates how suitable land is for specific crops under given climate, soil, terrain and management conditions. The Field Shift Resources tab links the v4 portal at https://gaez.fao.org. FAO released GAEZ v5 in 2025, and the v4 portal home page now points users to v5.

## What it measures

GAEZ v4 combines climate, soil and terrain data with crop eco-physiology to estimate where each crop can grow and how much it can yield. The v4 portal holds more than 150 variables in six themes and 25 sub-themes.

| Theme | Contents |
|---|---|
| 1. Land and water resources | Soil, water, terrain, land cover, protected areas, some socio-economic and demographic layers |
| 2. Agro-climatic resources | Climate class, temperature, evapotranspiration, length of growing period, frost days, dry days, rain days, net primary production, Fournier index, soil moisture, evapotranspiration deficit |
| 3. Agro-climatic potential yield | Yield limited by climate only, yield constraint factors, crop cycle attributes, land utilization types (LUTs) |
| 4. Suitability and attainable yield | Suitability class, suitability index, attainable yield after soil and terrain limits, crop water indicators |
| 5. Actual yields and production | Production, value, yield and harvested area, split into rainfed and irrigated |
| 6. Yield and production gaps | Yield gap ratio, production gap, yield achievement ratio |

Theme 3 ignores soil and slope. Theme 4 applies soil and slope reduction factors on top of theme 3, so theme 4 is the layer to use for "can this crop grow well here".

Crop coverage in v4 is about 53 crops built from more than 300 crop and LUT combinations. The list is strong for cereals (11 crops, 108 LUTs), roots and tubers (5 crops), sugar crops (2), pulses (6 crops, 35 LUTs) and oil crops (6 crops, 28 LUTs). Fruit and vegetable coverage is thin. Every crop is run separately for rainfed and irrigated supply and for several input levels.

GAEZ v5 adds crops such as avocado, cashew, mango, watermelon, sesame, finger millet, fonio and tef, and models 33 crop groups for 2020 actual production.

## Resolution

| Version | Main grid | Finer layers |
|---|---|---|
| v4 | 5 arc-minutes (about 9 x 9 km at the equator) | AEZ classes, soil suitability, slopes and land cover at 30 arc-seconds (about 0.9 x 0.9 km) |
| v5 | 5 arc-minutes for most outputs | Attainable yield and crop suitability at 30 arc-seconds (about 1 km) |

## Record length and scenarios

| Version | Baseline | Historical climate | Future climate |
|---|---|---|---|
| v4 | 2010 (statistics for 2009 to 2011) | 1961 to 2010 time series, with averages for 1961-1990, 1971-2000 and 1981-2010 | IPCC AR5, 5 climate models (GFDL-ESM2M, HadGEM2-ES, IPSL-CM5A-LR, MIROC-ESM-CHEM, NorESM1-M) x 4 RCPs (2.6, 4.5, 6.0, 8.5) for the 2020s (2011-2040), 2050s (2041-2070) and 2080s (2070-2099) |
| v5 | 2020 (statistics for 2019 to 2021) | AgERA5 daily data, with baselines 1981-2000 and 2001-2020 | CMIP6 (ISIMIP3b), 5 models x 3 SSPs (SSP1-2.6, SSP3-7.0, SSP5-8.5) for 2021-2040, 2041-2060, 2061-2080 and 2081-2100 |

v5 soil data comes from HWSD v2.2. v4 soil data comes from HWSD v1.21.

## Latency

GAEZ is a static model release, not a live feed. v4 came out in 2021 and v5 in 2025. There are no in-season updates.

## Formats

The v4 rasters are GeoTIFF files. FAO publishes them as ArcGIS Image Services, and each image record carries a URL to its original .tif file. Crop summary tables cover 53 crops by country and, for 12 large countries, by first-level sub-national unit.

## Access

v4 Data Viewer: https://gaez.fao.org/pages/data-viewer. The FAQ (November 2022) gives three download routes.

1. Filter the Data Viewer down to one image, click a pixel, and use the .tif link in the popup.
2. Open the viewer full screen, filter, and use "Export all as CSV" in the Attribute Table widget. The CSV lists every matching raster with its download URL. The FAQ suggests a batch file with `curl -k [URL of the GAEZ raster layer] -o [output directory]`.
3. For some themes, use the bulk links on the Data Access page (https://gaez.fao.org/pages/data-access-download).

A third-party R package, GAEZr (MIT licence), wraps the v4 downloads:

```r
remotes::install_github(repo = "floswald/GAEZr")
library(GAEZr)
gaez_download("whe")   # wheat potential yield, 1981-2010 climate
```

v5 portal: https://data.apps.fao.org/gaez/. The FAO GitHub repo https://github.com/un-fao/gaezv5 holds the v5 user guide and Jupyter notebooks that select and download v5 datasets "through the API". I did not open the notebooks, so the exact API calls are not confirmed. The same repo links PyAEZ, a Python package that runs parts of the AEZ model.

## Auth

The v4 Data Viewer and the .tif links did not ask for a login in the FAQ steps. Whether the v5 API needs a key is not confirmed.

## Licence

Not confirmed for the v4 rasters. The v4 terms-of-use page returned empty content. FAO publications about GAEZ v4 use CC BY-NC-SA 3.0 IGO, but that applies to the report, and it is not confirmed for the data. FAO's own 2025 reference list cites the GAEZ v5 data catalogue entry with "Licence: CC-BY-4.0". Before shipping, check the licence on the dataset page.

Suggested v4 citation from the FAQ: FAO and IIASA. Global Agro Ecological Zones version 4 (GAEZ v4). Accessed DATE. URL: http://www.fao.org/gaez/

## Limitations

- The 9 km grid is far coarser than a single field. The FAQ says results should be read at national, regional and first sub-national level, and it advises against statistics at finer administrative levels.
- The FAQ names soil map quality as a concern. Input data quality is uneven across regions.
- Land degradation (erosion, compaction, nutrient loss) is not, or only partly, modelled.
- Socio-economic factors and markets enter only through input levels and prices.
- Vegetable and fruit coverage is incomplete in v4.
- v4 uses AR5 scenarios. v5 uses CMIP6, so the two versions are not directly comparable.

## How it serves the rotation tool

- Theme 4 suitability index and attainable yield give a prior score for each candidate crop at the farm's location, separately for rainfed and irrigated cases.
- Future-period layers let the tool show how a crop's suitability shifts by the 2050s under different scenarios, which fits the challenge's "adapt to changing conditions" goal.
- Theme 3 crop-cycle attributes (start of cycle, cycle length, water deficit) help sequence crops in a rotation calendar.
- Theme 6 yield gaps help explain where better management could pay off.
- The tool should present GAEZ as a regional baseline and then refine it with field-scale data such as Sentinel-2, HLS, SMAP and local soil maps.

## Sources

- https://gaez.fao.org/
- https://www.fao.org/gaez/en
- https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/documentation/GAEZ4_FAQ.pdf (GAEZ v4 FAQ, version 2.0, November 2022)
- https://github.com/un-fao/gaezv5
- https://github.com/un-fao/gaezv5/wiki
- https://floswald.github.io/GAEZr/
- https://www.fao.org/3/cd7488en/online/state-of-the-worlds-land-and-water-resources-for-food-and-agriculture-2025-2025/notes.html (v5 CC-BY-4.0 citation, search snippet only)
- Pages that failed to load: https://gaez.fao.org/pages/data-access-download, https://gaez.fao.org/pages/theme-details, https://gaez.fao.org/pages/terms-of-use, https://gaez.fao.org/pages/disclaimer (empty content)
