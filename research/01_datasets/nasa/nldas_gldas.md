# NLDAS and GLDAS (North American and Global Land Data Assimilation Systems)

## What it measures

NLDAS and GLDAS are not satellite sensors. They are land surface models run by NASA Goddard and partners. Each model takes weather inputs ("forcing": rain, temperature, humidity, wind, radiation, pressure) built from observations and reanalysis, and simulates what happens at the land surface: soil moisture by layer, soil temperature, evapotranspiration, runoff, snow and energy fluxes. The output is a gap-free, gridded record that fills in what satellites cannot see, such as soil moisture below the top few centimetres.

### NLDAS-2

NLDAS-2 covers the continental United States plus parts of Canada and Mexico (product bounding box 25 N to 53 N, 125 W to 67 W).

The forcing files have two parts. File A is the main input. It holds 10 m wind (U and V), 2 m air temperature and specific humidity, surface pressure, downward longwave and shortwave radiation, hourly precipitation, convective fraction, CAPE and potential evaporation. Most fields come from the NCEP North American Regional Reanalysis (NARR, 32 km, 3-hourly), interpolated to the NLDAS grid and adjusted for terrain height. Shortwave radiation is bias-corrected against GOES satellite estimates. Precipitation comes from the CPC daily gauge analysis with a PRISM terrain adjustment, split into hours using Stage II radar, then CMORPH, then CPC hourly gauges, then NARR. Daily sums of NLDAS-2 precipitation match the CPC daily gauge analysis exactly. File B holds the same weather fields at the lowest NARR model level for modelling studies.

Four land models run on this forcing: Noah-2.8, Mosaic, VIC-4.0.3 and SAC. GES DISC distributes Noah, Mosaic and VIC output. The Noah product has 53 fields (the catalog variable table lists 57). Noah uses four soil layers of 10, 30, 60 and 100 cm. The first three form the root zone in non-forest areas.

### NLDAS-3 status

NLDAS-3 is in development. Its goals are coverage of all of North and Central America, 1 km resolution, lower latency, Noah-MP as the land model and assimilation of remote sensing data. The NLDAS-3 forcing data are now public, as hourly, daily and monthly collections, with access instructions on the NLDAS-3 GitHub README. The daily collection adds daily minimum and maximum air temperature. Planned Noah-MP outputs include four soil moisture layers (0 to 10, 10 to 40, 40 to 100 and 100 to 200 cm), water table depth, groundwater storage, vapour pressure deficit, transpiration, bare soil evaporation, GPP and LAI, with HyMAP streamflow. A drought monitoring workshop with NOAA NIDIS and the National Drought Mitigation Center was held on April 10, 2025. The release date of the NLDAS-3 model outputs is not confirmed.

### GLDAS-2

GLDAS-2 has three parts:

- GLDAS-2.0 is forced only with the Princeton meteorological data and gives a consistent series from 1948 to 2014.
- GLDAS-2.1 is forced with NOAA GDAS analysis fields, GPCP V1.3 daily precipitation and AGRMET radiation from 2000 to the present. It runs Noah 3.6 in the Land Information System (LIS) version 7 and has 36 land surface fields. It is "open loop", with no data assimilation.
- GLDAS-2.2 adds data assimilation. Its main product at GES DISC runs the Catchment model (CLSM-F2.5), not Noah, and assimilates GRACE total water storage from February 2003. It has 24 fields, including groundwater. It does not carry the forcing fields because of an ECMWF data agreement.

| Product | Short name | Model | What it gives |
| --- | --- | --- | --- |
| NLDAS-2 forcing, hourly | NLDAS_FORA0125_H (version 2.0; name follows GES DISC pattern, not confirmed on a product page) | none | Hourly weather inputs (File A) |
| NLDAS-2 Noah, hourly | NLDAS_NOAH0125_H (V2.0) | Noah | Soil moisture by layer, ET, runoff, soil temperature, snow |
| NLDAS-2 Mosaic and VIC, hourly | NLDAS_MOS0125_H, NLDAS_VIC0125_H (not confirmed) | Mosaic, VIC | Same family of outputs from other models |
| GLDAS-2.1 Noah, 3-hourly | GLDAS_NOAH025_3H (V2.1) | Noah 3.6 | 36 fields including soil moisture, ET, runoff and forcing |
| GLDAS-2.2 Catchment with GRACE-DA, daily | GLDAS_CLSM025_DA1_D (V2.2) | Catchment-F2.5 | 24 fields including groundwater storage |

## Spatial resolution

| Product | Grid |
| --- | --- |
| NLDAS-2 forcing and models | 0.125 degree (about 12 km) |
| NLDAS-3 | 1 km (target, per the NLDAS-3 page) |
| GLDAS-2.1 and 2.2 | 0.25 degree (about 25 to 28 km), 60 S to 90 N |

## Temporal resolution and revisit

- NLDAS-2 forcing and model output: hourly. Monthly averages and a monthly climatology are also offered for forcing.
- NLDAS-3 forcing: hourly, daily and monthly.
- GLDAS-2.1 Noah: 3-hourly (a monthly product also exists).
- GLDAS-2.2 Catchment GRACE-DA: daily.

Models have no revisit gaps. They produce a value for every time step.

## Record length

| Product | Start | End |
| --- | --- | --- |
| NLDAS-2 forcing | January 1, 1979 | Present |
| NLDAS-2 Noah | January 2, 1979 | Present |
| GLDAS-2.0 | 1948 | 2014 |
| GLDAS-2.1 Noah | January 1, 2000 | Present |
| GLDAS-2.2 Catchment GRACE-DA | February 1, 2003 | Present |

## Latency

- GLDAS-2.1 Early Products appear with about 1.5 month latency. The main stream waits for GPCP V1.3, which has 3 to 4 month latency, and then replaces the Early Products.
- GLDAS-2.2 Early Products (without GRACE) appear with about 1 month latency. The main GRACE-DA stream follows once GRACE data arrive, which takes 2 to 6 months.
- NLDAS-2 latency is not confirmed in the pages fetched.

## Formats

- NLDAS-2 forcing: WMO GRIB-1 per the LDAS page. GES DISC also serves NetCDF versions (confirmed for the Noah product, which states "netCDF (converted from the GRIB format)").
- GLDAS-2.1 and 2.2: NetCDF.

## Product IDs and DOIs

| Short name | CMR concept ID | DOI |
| --- | --- | --- |
| NLDAS_NOAH0125_H V2.0 | C2069246977-GES_DISC | 10.5067/T4OW83T8EXDO |
| GLDAS_NOAH025_3H V2.1 | C1342986035-GES_DISC | 10.5067/E7TYRXPJKWOQ |
| GLDAS_CLSM025_DA1_D V2.2 | C1700900796-GES_DISC | 10.5067/TXBMLX370XX8 |

## Access methods

- GES DISC dataset pages, for example https://disc.gsfc.nasa.gov/datasets/GLDAS_NOAH025_3H_2.1/summary (the page is a JavaScript app and did not render for this note). GES DISC offers subsetting and OPeNDAP.
- NASA Earthdata Search at https://search.earthdata.nasa.gov with the short names above.
- Giovanni, for quick area-average time series and maps of NLDAS and GLDAS variables without download. See access_tooling.md.
- NLDAS-3 forcing: access instructions on the NLDAS-3 GitHub README, linked from https://ldas.gsfc.nasa.gov/nldas/v3.
- `earthaccess` in Python:

```python
import earthaccess
earthaccess.login()
results = earthaccess.search_data(
    short_name="NLDAS_NOAH0125_H",
    version="2.0",
    bounding_box=(-94.0, 41.0, -93.0, 42.0),
    temporal=("2023-05-01", "2023-09-30"),
)
files = earthaccess.open(results)  # stream instead of download
```

Hourly files over long periods add up fast. For a single farm, a point time series through Giovanni or a GES DISC subsetting request is lighter than full files.

## Auth needed

A free NASA Earthdata Login account is required for GES DISC downloads, and the GES DISC application must be authorised in the Earthdata Login profile (standard GES DISC practice, not confirmed on the pages fetched).

## Known limitations

- These are model outputs. Soil texture, crop type and irrigation are not represented at the field level, so values describe a typical grid cell.
- NLDAS-2 Noah and GLDAS-2.1 Noah do not model irrigation (not stated on the pages fetched, but neither page lists irrigation), so irrigated areas look drier than they are.
- NLDAS-2 precipitation inputs changed over time. The CPC gauge analysis switched from inverse distance weighting (1979 to 2011) to optimal interpolation (2012 onward), which changed behaviour near the Mexican border, in western mountains and along coasts. Radar disaggregation starts in 1996 and CMORPH in 2002. Gauge networks also changed. Long trends need care.
- Over Canada, NLDAS-2 precipitation comes from NARR model output, not gauges.
- GLDAS-2.0 ends in 2014 and GLDAS-2.1 starts in 2000, with different forcing, so joining them makes a series that is not fully consistent.
- GLDAS-2.1 is open loop, so it does not correct its soil moisture with observations.
- Data downloaded before November 2020 lack the MOD44W inland water mask fix and should be downloaded again.

## How it maps to this challenge

- Heat stress. Hourly 2 m air temperature from NLDAS-2 forcing gives degree-days and hours above crop heat thresholds for each past season. The NLDAS-3 daily collection will add daily minimum and maximum temperature directly.
- Water stress. Noah root-zone soil moisture (0 to 100 cm) and ET show how dry the profile ran in each past season, and they cover 1979 onward, which is far longer than SMAP.
- Drought onset. Soil moisture percentiles from NLDAS-2 drive a drought monitor product (listed on the LDAS menu). A drop in root-zone percentiles in spring can flag years when a deep-rooted crop would struggle.
- Groundwater decline. GLDAS-2.2 groundwater storage, constrained by GRACE, adds a modelled groundwater trend at 0.25 degree. See grace.md.
- Rotation comparison. A 40-plus year NLDAS record lets the tool replay past weather against each rotation strategy and count how often each would have met heat or water stress.
- Data gap to report. Model grids of 12 to 25 km cannot see field-level soil or irrigation differences. Pair with ECOSTRESS, SMAP and local soil data.

## Sources

- https://ldas.gsfc.nasa.gov/nldas/v2/forcing
- https://ldas.gsfc.nasa.gov/nldas/v2/models
- https://ldas.gsfc.nasa.gov/nldas/v3
- https://www.earthdata.nasa.gov/data/catalog/ges-disc-nldas-noah0125-h-2.0
- https://www.earthdata.nasa.gov/data/catalog/ges-disc-gldas-noah025-3h-2.1
- https://www.earthdata.nasa.gov/data/catalog/ges-disc-gldas-clsm025-da1-d-2.2
- Failed to render: https://disc.gsfc.nasa.gov/datasets/GLDAS_NOAH025_3H_2.1/summary (JavaScript app returned only the site banner) and https://ldas.gsfc.nasa.gov/gldas/gldas-get-data (menu only).
