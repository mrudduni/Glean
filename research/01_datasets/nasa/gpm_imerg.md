# GPM IMERG (Integrated Multi-satellitE Retrievals for GPM)

## What it measures

IMERG estimates surface precipitation (rain and snow, as liquid-water equivalent) over most of the globe. It merges passive microwave estimates from the GPM satellite constellation, calibrated to the GPM Core Observatory radar-radiometer product (CORRA), with infrared estimates from geostationary satellites. The record joins the TRMM era (1998 to 2015) with the GPM era (2014 onward). The GPM Core Observatory launched on February 27, 2014.

Key fields in the files:

| Field | Meaning |
| --- | --- |
| `precipitation` | Multi-satellite estimate with gauge calibration. The GPM team recommends this field for most users. In Final it uses monthly GPCC gauge data. In Early and Late V07 it uses a climatological gauge adjustment |
| `precipitationUncal` | Estimate with no gauge calibration |
| `MWprecipitation` | Microwave-only estimate |
| `randomError` | Estimate of the non-systematic error |
| `probabilityLiquidPrecipitation` | Probability that precipitation is liquid (includes mixed). It is computed from surface wet-bulb temperature, not from the satellite data |
| `precipitation_cnt`, `precipitation_cnt_cond` | In daily files, counts of valid half-hours and of half-hours with at least 0.01 mm/hr |

Dew and frost are not counted as precipitation.

## Spatial resolution

0.1 x 0.1 degree, roughly 10 x 10 km. V07 added coverage poleward of 60 degrees for the precipitation fields. The infrared input covers only 60 N to 60 S, so estimates at higher latitudes rely on microwave data alone and are less complete.

## Temporal resolution and revisit

- Native output is every 30 minutes.
- GES DISC also distributes daily and monthly products. The GIS (GeoTIFF) files from PPS come in 30-minute, 3-hour, 1-day, 3-day, 7-day and 1-month accumulations, depending on the run.

## The three runs

| Run | Latency | How it differs |
| --- | --- | --- |
| Early | About 4 hours | Forward propagation only (extrapolation in time). Lowest latency |
| Late | Nominally 14 hours, closer to 12 hours in recent data | Forward and backward propagation (interpolation). PPS waits about 11 hours to catch the next microwave overpass. Uses a climatological gauge adjustment in V07 |
| Final | About 3.5 months per the IMERG FAQ, "roughly 2.5 months" per the download notes on the same page, and "the usual 4-month latency" in the V08 schedule note. The figures disagree; treat Final latency as about 3 to 4 months | Uses MERRA-2, GPCC monthly gauge analysis and revised retrievals that depend on ERA5. The GPM team advises Final for research |

The GPM team recommends Early or Late for low-latency uses such as crop forecasting, and Final when latency does not matter.

## Record length and version status (important)

- V07 is the current version. GES DISC labels it Version 07B for the half-hourly Early product.
- GPM_3IMERGHHE (Early, half-hourly): 1998-01-01 to 2026-11-12 at the time of fetching.
- GPM_3IMERGDF (Final, daily): 1998-01-01 to 2025-09-30. The V07 Final record stops in September 2025 because its parent products (CORRA and GPROF) are moving to V08.
- The GPM V08 schedule note (April 28, 2026) planned a V08 Final release in summer 2026, reprocessed from January 1998. An update on August 6, 2026 said the team was still waiting for one parent product, so V08 Final was not yet released. Its current release date is not confirmed.
- Early and Late V07 continue, but since 2026 they run in a "hybrid" mode that ingests GPROF V08. From March 1, 2026 the calibration to CORRA uses climatological values. The GPM team warns that the record may have discontinuities. The switch of near-real-time runs to V08 is expected no sooner than fall 2026.
- The DMSP SSMIS sensor feeds IMERG. The Department of Defense agreed to keep sharing SSMIS data until the sensor fails or the program ends (planned September 2026).

For the tool, this means a gap exists today between the end of V07 Final (September 2025) and the present that can only be filled with Late or Early data, which have a different calibration.

## File formats

- GES DISC: HDF5 for half-hourly products (about 2.8 MB per file for Early), NetCDF for daily Final (about 12 MB per file).
- PPS GIS files: GeoTIFF with world files. Values in 30-minute, 3-hour and 1-day files are scaled by 10 (units of 0.1 mm). Monthly files use 1 mm units.
- Giovanni returns maps, time series and subsets in several formats.
- Units differ between files. Some fields are rates (mm/hr), others are accumulations (mm) or daily mean rates (mm/day).

## Product IDs (V07)

| Short name | Description | DOI |
| --- | --- | --- |
| GPM_3IMERGHHE | Early, half-hourly | 10.5067/GPM/IMERG/3B-HH-E/07 |
| GPM_3IMERGHHL | Late, half-hourly | not confirmed |
| GPM_3IMERGHH | Final, half-hourly | not confirmed |
| GPM_3IMERGDE / GPM_3IMERGDL | Early and Late daily | not confirmed |
| GPM_3IMERGDF | Final, daily | 10.5067/GPM/IMERGDF/DAY/07 |
| GPM_3IMERGM | Final, monthly | not confirmed |

Only GPM_3IMERGHHE and GPM_3IMERGDF pages were read in full. The other short names follow the same pattern and appear in the GPM IMERG Giovanni table, but their DOIs were not checked.

## Access methods

- GES DISC (https://disc.gsfc.nasa.gov) distributes HDF5 and NetCDF products. A free Earthdata Login account is required.
- Giovanni lists IMERG variables at https://giovanni.gsfc.nasa.gov/giovanni/#dataKeyword=IMERG. It can make area-averaged time series for a country, U.S. state or watershed using the "Show Shapes" option.
- PPS servers host the GIS GeoTIFF files. These need a separate free PPS registration. Early GIS files are at https://jsimpsonhttps.pps.eosdis.nasa.gov/imerg/gis/. Late files sit in `./[yyyy]/[mm]` and Final files in `./[yyyy]/[mm]/[dd]/gis/` on the PPS archive. An example file name from the docs is `3B-HHR-E.MS.MRG.3IMERG.20200207-S053000-E055959.0330.V06B.1day.zip` (this example is from V06B).
- AWS: the daily Final product sits in the Earthdata Cloud bucket `arn:aws:s3:::gesdisc-cumulus-prod-protected/GPM_L3/GPM_3IMERGDF.07/` in us-west-2. This is a protected bucket, so it needs Earthdata Login based S3 credentials.
- `earthaccess` can search and download with short names such as `GPM_3IMERGDF`.
- NASA POWER serves IMERG daily totals as `IMERG_PRECTOT` (mm/day), plus `IMERG_PRECLIQUID_PROB` and `IMERG_PRECTOT_COUNT`, at 0.1 degree from June 1, 1998 to near real time, with no login. See nasa_power.md.

Example `earthaccess` search:

```python
import earthaccess
earthaccess.login()
granules = earthaccess.search_data(
    short_name="GPM_3IMERGDF",
    temporal=("2015-01-01", "2025-09-30"),
    bounding_box=(-94.0, 41.0, -93.0, 42.0),
)
ds_files = earthaccess.open(granules)  # stream instead of download
```

## Worldview layers

Worldview shows IMERG as images from 1998 to the present at 30-minute steps. To display it, open Add Layers, search "imerg" and tick "Precipitation Rate (30-min) IMERG". A daily layer is also available from the same search. Images appear a few hours after real time, so users must move the time slider back. Rates are shown in mm/hr of liquid-equivalent depth, with green to red for rain and cyan to purple for snow. Hovering over a pixel shows the rate range for that colour. The GIBS layer identifier is reported as `IMERG_Precipitation_Rate` in a third-party catalogue; it was not checked against GIBS capabilities.

## Known limitations

- A 10 km pixel covers many fields. Convective summer storms can be much smaller than one pixel.
- Early and Late runs use only climatological gauge calibration. Final is better calibrated but arrives months later.
- V07 Final stops at 2025-09-30, and Early and Late are in a hybrid state with possible jumps.
- Extreme values are more sensitive to input changes than medians or means. The GPM team suggests using metrics such as medians, means and root-mean-square differences.
- Coverage above 60 degrees latitude is less complete.
- Snow is reported as liquid-water equivalent, not as snow depth.

## How it maps to this challenge

- Rainfall reliability. IMERG Final daily data from 1998 give about 27 years to compute, for each farm, how often the planting window or flowering month got enough rain. This lets the tool compare rotations whose critical months differ.
- Water stress. Rainfall deficits during sensitive crop stages, together with SMAP and ECOSTRESS, show which crop in a rotation is most exposed.
- Erosion. Counts of intense rain days (for example days above a threshold in mm/day) during bare-field periods show when bare soil is most at risk. Half-hourly rates help detect intense bursts.
- Frost and snow context. `probabilityLiquidPrecipitation` separates rain from snow in shoulder seasons.
- Data gap to report. The tool should label which run it uses for each date and warn that the Late run after September 2025 is not directly comparable with the Final record.

## Sources

- https://gpm.nasa.gov/data
- https://gpm.nasa.gov/data/imerg
- https://gpm.nasa.gov/data/news/imerg-v08-transition-schedule
- https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDF_07/summary
- https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGHHE_07/summary
- https://registry.opendata.aws/nasa-gpm3imergdf/
- https://www.earthdata.nasa.gov/learn/tutorials/view-imerg-precipitation-imagery-worldview
- https://geodiscovery.uwm.edu/catalog/nasa-gibs-imerg_precipitation_rate (search snippet only, for the layer identifier)
- https://power.larc.nasa.gov/docs/methodology/
- https://power.larc.nasa.gov/api/system/manager/parameters?community=AG&temporal=daily
- https://earthaccess.readthedocs.io/en/latest/user/quick-start/
