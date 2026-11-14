# GRACE and GRACE-FO (Gravity Recovery and Climate Experiment and Follow-On)

## What it measures

GRACE and GRACE-FO are pairs of twin satellites that measure month-to-month changes in Earth's gravity field. The two satellites fly about 220 km apart. A microwave ranging system (and on GRACE-FO, a test laser ranging interferometer) measures tiny changes in the distance between them as they pass over areas of more or less mass. Accelerometers remove non-gravity forces such as drag, and GPS fixes each satellite's position. Over land, most monthly mass change comes from water, so the missions track changes in total water storage: groundwater, soil moisture, snow, lakes and rivers combined.

GRACE ran from 2002 to 2017. GRACE-FO, a NASA and German Research Centre for Geosciences (GFZ) partnership, launched on May 22, 2018.

The main product for land hydrology is the JPL mascon solution, release RL06.3 version 04. JPL fits the ranging data to 4,551 equal-area spherical cap "mascons" (mass concentration blocks), each 3 degrees across, with geophysical constraints in space and time. This removes the north-south striping seen in older spherical harmonic solutions without extra smoothing. A Coastline Resolution Improvement (CRI) filter separates land and ocean mass in coastal mascons. Values are anomalies in centimetres of equivalent water thickness, relative to a 2004.0 to 2009.999 mean.

GRACE measures total water storage. It does not split that total into groundwater and soil moisture by itself. Two derived products do the split.

| Product | Short name or location | What it gives |
| --- | --- | --- |
| JPL mascons, CRI filtered, RL06.3 v04 | TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4 | Monthly total water storage anomaly (cm), uncertainty, land mask, gain factors, mascon ID |
| JPL mascons, not CRI filtered | Offered on the same JPL page for expert users (short name not confirmed) | Same, without the land and ocean separation |
| GRACE-based drought indicators (NASA GSFC) | https://nasagrace.unl.edu | Weekly groundwater, root-zone soil moisture and surface soil moisture percentiles, plus 1 to 3 month forecasts |

The drought indicators come from scientists at NASA Goddard. They assimilate GRACE-FO water storage into a land surface model with other observations and express each week's groundwater and soil moisture as a percentile for that place and time of year. Low percentiles mean drier than normal. The forecasts drive the model forward with downscaled GEOS-5 seasonal forecasts and give percentiles relative to 1948 to 2014. These indicators are widely described as an input the U.S. Drought Monitor authors consult. That role is not confirmed in the pages fetched for this note.

## Spatial resolution

| Product | Grid | Real resolution |
| --- | --- | --- |
| JPL mascons | 0.5 degree (720 by 360 cells) | 3 degree mascons (about 300 km). Neighbouring 0.5 degree cells are not independent |
| GSFC drought indicators, CONUS | 0.125 degree | Model grid. The GRACE signal behind it is still coarse |
| GSFC drought indicators, global | 0.25 degree | Same |

JPL supplies 0.5 degree gain factors, derived from the CLM land model, to rescale land signals below mascon size. JPL notes the gain factors are mostly driven by the annual cycle and may not suit trend analysis. Uncertainty grids hold one value per mascon, not per 0.5 degree cell. A single cell's error would be much larger.

## Temporal resolution and revisit

- Mascons are monthly.
- GSFC drought indicators are weekly.
- Each new month slightly changes all earlier months, because the solution links months with a Kalman filter. The last four or so months change most. JPL reissues the whole series in one NetCDF file with each update and recommends using the latest file.

## Record length

- Mascons start on April 4, 2002, and run to the present.
- GRACE data end in mid-2017 and GRACE-FO data begin in mid-2018. NASA papers describe the gap as July 2017 to May 2018 (11 months) or June 2017 to June 2018. Treat these months as missing.
- The GRACE record also has scattered missing months, mainly late in the mission when battery limits forced the satellites into reduced operations. A NASA paper by Rodell and Li counts 18 missing months besides the gap.

## Latency

The GES DISC page for GLDAS-2.2, which assimilates GRACE, states that "GRACE data have a 2-6 month latency". JPL's own mascon latency is not stated on the pages fetched. The GSFC drought indicators are produced weekly, which suggests they bridge recent weeks with the model until new GRACE-FO months arrive (the method is not detailed on the page fetched).

## Formats

Mascons are a single NetCDF-4 file holding all months. The GSFC drought indicators come as images and binary data files (format details not confirmed).

## Product IDs and DOIs

| Product | DOI |
| --- | --- |
| TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4 | 10.5067/TEMSC-3JC634 |
| Previous release RL06.1Mv03 | 10.5067/TEMSC-3JC63 |

## Access methods

- JPL GRACE Tellus portal: https://grace.jpl.nasa.gov/data/get-data/jpl_global_mascons/
- PO.DAAC dataset page: https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4
- NASA Earthdata Search and the `earthaccess` library, using the short name:

```python
import earthaccess
earthaccess.login()
results = earthaccess.search_data(
    short_name="TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4",
)
files = earthaccess.download(results, "./grace")
```

- GSFC drought indicator maps and files: https://nasagrace.unl.edu (University of Nebraska-Lincoln host).

To apply the gain factors, multiply each month's grid by the scaling grid: corrected(x, y, t) = g(x, y, t) times s(x, y), as the JPL user guide states.

## Auth needed

A free NASA Earthdata Login account is required to download from PO.DAAC. The nasagrace.unl.edu maps appear open (login need not confirmed).

## Known limitations

- The real resolution is about 300 km. A single farm sits inside one mascon. GRACE describes the regional aquifer and basin, not the farm.
- Total water storage mixes groundwater, soil moisture, snow and surface water. Separating groundwater needs a model or other data.
- The 2017 to 2018 gap breaks trend fitting across the two missions.
- Recent months get revised.
- Anomalies use a 2004 to 2009 baseline. Other anomaly data must use the same baseline before comparison.
- Gain factors suit seasonal hydrology but may bias trends.

## How it maps to this challenge

- Groundwater decline. A long downward trend in the mascon covering the farm, together with GSFC groundwater percentiles, shows whether the regional aquifer is falling. A rotation that relies on irrigated, water-hungry crops carries more long-term risk where that is true.
- Drought onset. Weekly GSFC root-zone soil moisture and groundwater percentiles show when a region slips into deficit, and the 1 to 3 month forecasts give an early warning before planting.
- Rotation framing. Where groundwater is in steep decline, the tool can favour rotations with lower seasonal water demand or more dryland crops, and state that the evidence is regional.
- Data gap to report. GRACE cannot see a single farm or well. The tool should pair it with local well records (for example USGS) where available.

## Sources

- https://grace.jpl.nasa.gov/data/get-data/jpl_global_mascons/
- https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4
- https://gracefo.jpl.nasa.gov/mission/overview/
- https://nasagrace.unl.edu/
- https://ntrs.nasa.gov/api/citations/20230003509/downloads/Rodell-Li_grace_extreme_final3_all.pdf (search snippet only, for the gap and missing months)
- https://grace.jpl.nasa.gov/publications/1206/ (search snippet only, for the June 2017 to June 2018 gap wording)
- https://www.earthdata.nasa.gov/data/catalog/ges-disc-gldas-clsm025-da1-d-2.2 (for the 2 to 6 month GRACE latency)
- Not fetched: a page confirming U.S. Drought Monitor use of the GSFC indicators, and an official JPL mascon latency figure.
