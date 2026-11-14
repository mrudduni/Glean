# ERA5 and ERA5-Land

ERA5 is the fifth-generation ECMWF global reanalysis, published by the Copernicus Climate Change Service (C3S) on the Climate Data Store (CDS). ERA5-Land re-runs the land part of ERA5 at a finer grid. The Field Shift Resources tab lists ERA5 single levels as a space agency partner (ESA) resource.

## What it measures

A reanalysis merges a weather model with past observations to give a complete, consistent gridded record. ERA5 gives hourly atmosphere, ocean-wave and land-surface fields. ERA5-Land is driven by ERA5 weather (with a lapse-rate correction for elevation) and does not assimilate observations directly.

### Farm-relevant variables (ERA5-Land names, CDS request names in brackets)

| Group | Variables |
|---|---|
| Temperature | 2 m temperature (`2m_temperature`), 2 m dewpoint (`2m_dewpoint_temperature`), skin temperature (`skin_temperature`) |
| Soil temperature | Soil temperature levels 1 to 4 (`soil_temperature_level_1` to `_4`) |
| Soil water | Volumetric soil water layers 1 to 4 (`volumetric_soil_water_layer_1` to `_4`, m³/m³) |
| Water balance | Total precipitation (`total_precipitation`), total evaporation, meaning actual ET (`total_evaporation`), potential evaporation (`potential_evaporation`), evaporation from bare soil, from vegetation transpiration and from top of canopy, surface and sub-surface runoff, runoff |
| Energy | Surface solar radiation downwards (`surface_solar_radiation_downwards`), surface net solar and thermal radiation |
| Snow | Snowfall, snowmelt, snow evaporation |
| Vegetation | Leaf area index for low and high vegetation (monthly climatology only, no year-to-year change) |
| Static | Soil type, land-sea mask, low and high vegetation cover and type, geopotential |

Soil layers in ERA5-Land: 0 to 7 cm, 7 to 28 cm, 28 to 100 cm and 100 to 289 cm.

ERA5 single levels carries the same core weather fields plus wind and many more atmospheric fields. I did not pull its full variable table.

## Resolution

| | ERA5 single levels | ERA5-Land |
|---|---|---|
| Grid on CDS | 0.25° x 0.25° (atmosphere). Ensemble spread at 0.5° | 0.1° x 0.1° (native about 9 km) |
| Time step | Hourly. Monthly means also offered | Hourly. Monthly means in a separate dataset |
| Uncertainty | 10-member ensemble every 3 hours | None of its own. Use the ERA5 ensemble |

## Record length

- ERA5: 1940 to present.
- ERA5-Land: January 1950 to present.

## Latency

- ERA5 updates daily with a lag of about 5 days. This early release is called ERA5T. If flaws are found, ERA5T values can differ from the final release, which comes 2 to 3 months later, and users are notified.
- ERA5-Land-T follows ERA5T. Daily updates arrive about 5 days behind real time, and monthly means about 5 days after the month ends. The consolidated ERA5-Land runs to 2 to 3 months before the present.

## Formats

GRIB is the native format. NetCDF can be requested on the CDS (`'data_format': 'netcdf'`). Accumulated variables in ERA5-Land (precipitation, evaporation, radiation, runoff) are summed from 00 UTC to the forecast step. The value at 00 UTC holds the total for the previous day. ERA5 uses a different accumulation convention, so mixing the two needs care.

## Access

CDS dataset pages:
- ERA5: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels
- ERA5-Land: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land

Steps from the CDS "How to API" page:

1. Register and log in on the CDS.
2. Put your key in `$HOME/.cdsapirc` (on Windows, `%USERPROFILE%\.cdsapirc`):

```
url: https://cds.climate.copernicus.eu/api
key: <PERSONAL-ACCESS-TOKEN>
```

3. Install the client: `pip install "cdsapi>=0.7.7"`.
4. Accept the dataset's Terms of Use by hand at the bottom of the dataset's download form. The API refuses requests until this is done.
5. Build the request on the web form and press "Show API request code" to get the exact Python.

Request pattern from the CDS docs:

```python
import cdsapi

client = cdsapi.Client()
dataset = "<DATASET-SHORT-NAME>"
request = {<SELECTION-REQUEST>}
client.retrieve(dataset, request, "<TARGET-FILE>")
```

A rotation-tool request for one farm area, built on that pattern (variable names from the ERA5-Land parameter table; check the keys against "Show API request code" before use):

```python
import cdsapi

client = cdsapi.Client()
client.retrieve(
    "reanalysis-era5-land",
    {
        "variable": [
            "2m_temperature",
            "total_precipitation",
            "volumetric_soil_water_layer_1",
            "potential_evaporation",
            "total_evaporation",
        ],
        "year": ["2024"],
        "month": [f"{m:02d}" for m in range(1, 13)],
        "day": [f"{d:02d}" for d in range(1, 32)],
        "time": ["00:00"],
        "area": [31.0, 30.5, 30.0, 31.5],   # North, West, South, East
        "data_format": "netcdf",
    },
    "farm_2024.nc",
)
```

ECMWF also offers a newer client, `ecmwf-datastores-client`, which is still "incubating". The CDS says users do not need to migrate yet.

## Auth

A free CDS account and a personal access token are required. The licence must be accepted once per dataset on the website.

## Licence

The CDS licence page says these datasets are released under the CC-BY licence. An ECMWF forum post says CC-BY replaced the "Licence to use Copernicus products" on 2 July 2025 (title seen in search results only). CC-BY needs attribution to C3S and ECMWF. I did not open the full licence text.

## Limitations

- At 0.1° (about 9 to 11 km), ERA5-Land describes a district, not a field. Hilly or coastal farms can differ a lot from the grid cell.
- ERA5-Land is a model run without direct observation input, so precipitation and soil moisture can be biased. Validate against station data or NASA IMERG and SMAP.
- Leaf area index is a fixed monthly climatology and does not show real crop growth.
- ERA5T values can be revised 2 to 3 months later.
- CDS requests queue, and large hourly requests can be slow. Ask for small areas, few variables and daily times during the hackathon.
- ERA5 is not NASA data. Space Apps requires at least one NASA dataset, so ERA5 should sit beside NASA POWER, IMERG or SMAP rather than replace them.

## How it serves the rotation tool

- A 70-year climate baseline (1950 onward) at each farm gives growing degree days, frost dates, heat-stress days and rainfall reliability for each candidate crop.
- Trend analysis over 1950 to the present shows how the farm's season has already shifted, which supports the "adapt to changing conditions" story.
- Soil water layers and potential versus actual evaporation give a simple water-balance check for whether a rotation's crops fit available water.
- Soil temperature at 0 to 7 cm helps set sowing windows.
- Near-real-time ERA5-Land-T (about 5 days behind) can update the current-season view.
- GAEZ v5 uses AgERA5, an agriculture-oriented ERA5 product, as its historical climate input. AgERA5 was not researched here.

## Sources

- https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview
- https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=overview
- https://cds.climate.copernicus.eu/how-to-api
- https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation
- https://cds.climate.copernicus.eu/licences/cc-by (search snippet)
- https://forum.ecmwf.int/t/cc-by-licence-to-replace-licence-to-use-copernicus-products-on-02-july-2025/13464 (search snippet)
