# PRISM climate data

## What it is

PRISM, run by the PRISM Group at Oregon State University (NACSE), produces gridded weather and climate datasets for the United States. It combines station observations from many networks with quality control and a terrain-aware interpolation method. The USDA Risk Management Agency supports the website.

## Variables

| Code | Meaning |
| --- | --- |
| ppt | Total precipitation (rain plus melted snow) |
| tmin, tmax | Daily minimum and maximum temperature |
| tmean | Mean temperature, computed as (tmax + tmin) / 2 |
| tdmean | Mean dew point |
| vpdmin, vpdmax | Minimum and maximum vapor pressure deficit |
| soltotal, solslope | Global shortwave solar irradiance on a horizontal and on a sloped surface (time series added February 2026) |
| solclear, soltrans | Clear-sky irradiance and cloud transmittance (normals only) |

## Spatial and temporal resolution

- 800 m (30 arc-second) and 4 km (2.5 arc-minute). The web service lists 400 m as a future resolution that is not yet implemented.
- Daily grids from 1 January 1981 to present.
- Monthly and annual grids from 1895 to present.
- 30-year normals for 1991-2020 (monthly, annual and daily normals). Normals are recomputed at the end of each decade.

## Dataset types

- AN ("all networks") gives the best estimate each day, using all available stations, at some cost to long-term consistency. The web service returns AN by default.
- LT ("long term") favors temporal consistency. The web service can return LT 800 m monthly data by adding `/lt` to the URL.
- Recent grids are revised. Daily grids go through 8 versions and monthly grids 7 versions over six months, after which PRISM treats them as stable.

## Coverage

Conterminous US through the web service. The file naming scheme also lists Alaska, Hawaii and Puerto Rico, but the web service documentation says only CONUS is currently available.

## Formats

Each grid comes as a zip "grid package" with a Cloud Optimized GeoTIFF (default), auxiliary statistics files, a projection file, an FGDC metadata XML, an info text file, and a CSV listing the stations used. The web service can also return netCDF (`?format=nc`), ASCII grid (`asc`) or BIL (`bil`). PRISM announced netCDF availability on 8 September 2026.

## Access methods

### Web service (current version, document updated 26 March 2025)

The old web service was scheduled to be disabled on 30 September 2025.

Pattern:

```
https://services.nacse.org/prism/data/get/<region>/<res>/<element>/<date>[?format=nc|asc|bil]
```

Examples from the official documentation:

```
https://services.nacse.org/prism/data/get/us/800m/tmin/20090405      # 800 m daily
https://services.nacse.org/prism/data/get/us/4km/ppt/199504          # 4 km monthly
https://services.nacse.org/prism/data/get/us/4km/tmin/202204?format=nc
https://services.nacse.org/prism/data/get/us/800m/tmax/200506/lt     # LT dataset
wget --content-disposition https://services.nacse.org/prism/data/get/us/4km/tmin/20191121
```

Release date service (tells whether a grid changed since last download):

```
https://services.nacse.org/prism/data/get/releaseDate/us/800m/ppt/20090405?json=true
https://services.nacse.org/prism/data/get/releaseDate/us/800m/ppt/19990101/19991231
```

Grid count service (returns the version number 1 to 8):

```
https://services.nacse.org/prism/data/get/gridCount/us/tmax/20150819
```

The 30-year normals are not available through the web service. They are on FTP and the website.

### FTP and data directory

Anonymous FTP at prism.oregonstate.edu, mirrored over HTTPS at https://data.prism.oregonstate.edu. It holds all time series and normals plus earlier versions.

### Data Explorer

The PRISM Data Explorer returns 4 km and 800 m time series for point locations. Its bulk option accepts up to 500 points in one request. This is the easiest way to get a daily series for a farm point without handling whole grids.

## Authentication and limits

No key or account. PRISM monitors downloads. If the same file is downloaded twice in 24 hours, further downloads of that file are blocked for that period, and repeated excessive activity can lead to IP blocking. The sample script waits 2 seconds between requests.

## Terms of use

Data may be freely reproduced and distributed. Users must state the PRISM Group name, URL and date of access, for example "PRISM Group, Oregon State University, https://prism.oregonstate.edu, accessed 16 Dec 2025." Map graphics must carry the PRISM copyright notice. Oregon State University keeps ownership and copyright. PRISM advises against using its data to calculate very long-term trends. Data come with no warranty.

## Limitations

- Grids for the last six months change as stations report and QC runs.
- AN data mix station networks over time, so trend analysis should use LT data, and even then PRISM discourages very long-term trends.
- 800 m cells are larger than many fields, so within-field variation is lost.
- Only one grid per request through the web service, so a multi-year daily series for a whole grid means thousands of requests.

## How it plugs into the rotation tool

- Daily tmin and tmax give growing degree days, frost dates and heat stress counts for each candidate crop.
- Daily ppt and vpd give water stress indicators and planting window checks, and they can drive a simple water balance with SSURGO available water capacity.
- 1991-2020 normals give the baseline climate. Recent years compared with normals show how conditions are shifting, which supports the "field shift" framing of the challenge.
- The station CSV in each grid package lets the tool report how many stations support the estimate near the farm, a useful data-quality flag.

## Sources

- https://prism.oregonstate.edu
- https://prism.oregonstate.edu/terms
- https://prism.oregonstate.edu/downloads
- https://prism.oregonstate.edu/documents/PRISM_downloads_web_service.pdf
- https://prism.oregonstate.edu/documents/PRISM_datasets.pdf
- https://prism.oregonstate.edu/documents/PRISM_update_schedule.pdf
- https://prism.oregonstate.edu/documents/PRISM_downloads_FTP.pdf
- https://data.prism.oregonstate.edu
