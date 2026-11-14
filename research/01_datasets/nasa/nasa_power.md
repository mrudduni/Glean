# NASA POWER (Prediction Of Worldwide Energy Resources)

## What it measures

POWER is a NASA Langley service that repackages NASA solar and meteorological data as analysis-ready time series. It serves three user communities: Renewable Energy (RE), Sustainable Buildings (SB) and Agroclimatology (AG). All three draw on the same archive and differ in parameter names, units and formats.

- Solar parameters come from the GEWEX SRB Release 4.0-IP archive (1984 to 2000) and from CERES SYN1deg and FLASHFlux (2001 onward). They are model estimates inferred from satellite observations through radiative transfer.
- Meteorological parameters come from the GMAO MERRA-2 reanalysis and GEOS-IT (the methodology page also mentions GEOS FP-IT).
- POWER Release 10 moved processing to a cloud pipeline.
- POWER also offers higher-resolution sources through a "High-Resolution" toggle in the Data Access Viewer and through parameter aliases in the API.

| High-resolution source | Domain | Resolution | Start | End |
| --- | --- | --- | --- | --- |
| IMERG | Precipitation | 0.1 degree (about 10 km), daily UTC | June 1, 1998 | near real time |
| SMAP L4 | Soil moisture | about 0.09 degree (about 9 km), daily UTC | 31 March 2015 | near real time |
| NEX-GDDP-CMIP6 | Future climate | about 0.25 degree (about 25 km), daily | 2015 | 2100 |

## The Agroclimatology community

The AG community provides daily time series aimed at agricultural decision support tools such as DSSAT. The AG daily parameter dictionary returned 152 parameters when queried. The ones most useful here:

| Parameter | Units | Definition (summarised from the POWER parameter dictionary) |
| --- | --- | --- |
| T2M | C | Mean air temperature at 2 m |
| T2M_MAX, T2M_MIN | C | Maximum and minimum hourly air temperature at 2 m in the period |
| T2M_RANGE | C | Daily temperature range at 2 m |
| T2MDEW | C | Dew or frost point at 2 m |
| T2MWET | C | Wet bulb temperature at 2 m |
| RH2M | % | Relative humidity at 2 m |
| PRECTOTCORR | mm/day | MERRA-2 bias-corrected total precipitation |
| IMERG_PRECTOT | mm/day | IMERG total precipitation |
| GWETTOP | 0 to 1 | Surface soil wetness, upper 5 cm (0 dry, 1 saturated) |
| GWETROOT | 0 to 1 | Root zone soil wetness, "generally considered to be the upper 1 m" |
| GWETPROF | 0 to 1 | Profile soil moisture |
| SFMC, RZMC | m3/m3 | Surface and root zone (0 to 100 cm) soil moisture |
| RZMC_PRCNTL | % | Root zone soil moisture as a percentile |
| ALLSKY_SFC_SW_DWN | MJ/m2/day | All-sky surface shortwave downward irradiance (global horizontal irradiance) |
| ALLSKY_SFC_PAR_TOT | MJ/m2/day | All-sky total photosynthetically active radiation |
| FROST_DAYS | days | A frost day occurs when 2 m temperature cools to the dew point and both are below 0 C |
| GDD4_4, GDD7_2, GDD10, GDD13_3, GDD15_6 | degree-days C | Growing degree days above the stated base temperature (GDD10 is noted for corn, sorghum, rice and soybeans) |
| EVLAND | mm/day | Evaporation over land |
| EVPTRNS | MJ/m2/day | Evapotranspiration energy flux |
| WS2M, WS10M | m/s | Wind speed at 2 m and 10 m |
| TSOIL1 to TSOIL6 | C | Soil temperature layers |
| SNODP | cm | Snow depth |
| GWM_HEIGHT_ANOMALY | m | Height anomaly from the "GWM" hydrology source (not explained further on the pages read) |

The full list comes from the API endpoint shown below.

## Spatial resolution

- POWER serves each parameter at its source resolution.
- MERRA-2 meteorology is on a 1/2 x 5/8 degree grid (about 50 x 60 km at mid latitudes).
- Release 9 notes give 1 x 1 degree for radiation and 1/2 x 5/8 degree for meteorology. Release 10 says it keeps source resolution; whether solar is still 1 degree is not confirmed.
- The Daily API docs describe a 0.5 x 0.5 degree global grid for regional requests.
- IMERG and SMAP aliases run at 0.1 degree and about 9 km.

## Temporal resolution

Hourly, daily, monthly and annual, and climatology (long-term monthly averages). Daily data are available in UTC or Local Solar Time; the Daily API defaults to Local Solar Time (`time-standard=LST` or `time-standard=UTC`).

## Record length

- Daily meteorology: 1981-01-01 to near real time.
- Solar: from 1984 (per the AWS registry entry and the communities page).
- Hourly source data: from 1984 for CERES-based fields per the AWS registry entry (the hourly meteorology start was cut off in the text read and is not confirmed).

## Latency

POWER states a latency of 2 to 3 days for meteorological parameters and 5 to 7 days for solar parameters. The archive updates nightly. A POWER Services Status Dashboard shows current latency (not opened for this note).

## File formats

Daily API: CSV, JSON, ASCII, NetCDF (point and regional) and ICASA (point only, AG only). ICASA is the format used by crop models such as DSSAT. When ICASA is requested, the API fills in the required weather parameters and sets the community to AG.

## Access methods

No account or API key appears in any POWER API example, and the AWS registry entry says there are no restrictions on use, access or download (data are under Creative Commons BY 4.0, with a request to cite POWER). This makes POWER the only source in this set that needs no Earthdata Login.

API base: `https://power.larc.nasa.gov`

Example point request (from the Daily API docs, AG community):

```
https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PS,WS10M&community=AG&longitude=0&latitude=0&start=20170101&end=20170201&format=CSV
```

A farm request built on the same pattern:

```
https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,GWETROOT,ALLSKY_SFC_SW_DWN,FROST_DAYS&community=AG&longitude=-93.6&latitude=42.0&start=19810101&end=20251231&format=JSON
```

ICASA for crop models (from the docs):

```
https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M&community=AG&longitude=0&latitude=0&start=20170101&end=20170401&format=ICASA
```

Regional request (from the docs):

```
https://power.larc.nasa.gov/api/temporal/daily/regional?latitude-min=50&latitude-max=55&longitude-min=50&longitude-max=55&parameters=T2M&community=SB&start=20170101&end=20170201&format=CSV
```

Parameter dictionary for AG daily data (JSON):

```
https://power.larc.nasa.gov/api/system/manager/parameters?community=AG&temporal=daily
```

Point requests can include `site-elevation` (metres, returns pressure corrected to that elevation) and `wind-elevation` with `wind-surface` (10 to 300 m).

Cloud access: the archive is on AWS in us-west-2 as Zarr data stores. The registry gives `arn:aws:s3:::nasa-power` and `arn:aws:s3:::power-datastore`, and the public listing command `aws s3 ls --no-sign-request s3://nasa-power/`. The POWER FAQ warns that units in the raw Zarr stores may not match the community units served by the API.

## Rate limits and request limits

- A single point request can ask for up to 20 parameters. A regional request is limited to one parameter.
- The API returns HTTP 429 (Too Many Requests) when a client sends too many requests, and HTTP 422 for invalid parameters.
- The Daily API docs warn that a client that keeps requesting the same location may be blocked, and that bulk users only need one request per 0.5 degree grid cell.
- A numeric rate limit (requests per minute or per day) is not stated on the pages read. Not confirmed.
- Response times grow with the number of parameters and the temporal level. Application APIs usually finish in under a minute.

## Known limitations

- Coarse grid. One MERRA-2 cell covers thousands of hectares. In hilly or coastal areas the cell average can differ a lot from a farm, and the POWER FAQ notes the cell elevation can differ from a local station.
- Model data. Meteorology is reanalysis, and solar values are model estimates from satellite data. POWER documents validation against surface stations in its methodology pages.
- FROST_DAYS uses a dew point condition, so it may miss radiative frosts in dry air where air temperature falls below 0 C but stays above the dew point. Computing frost days from T2M_MIN gives a second view.
- GWETROOT and GWETTOP are model fields from MERRA-2, not satellite soil moisture. The SMAP-based aliases are a separate source.
- Near-real-time values may later be revised as source data are finalised (stated in general terms only).

## How it maps to this challenge

- Frost risk. FROST_DAYS and T2M_MIN from 1981 give last spring frost and first autumn frost dates per year, so the tool can test whether an earlier planting or a winter crop in a rotation is exposed.
- Heat stress. T2M_MAX gives counts of days above crop thresholds during flowering windows.
- Season length. GDD sums show whether a longer-season crop or a double crop fits the local thermal time.
- Rainfall reliability. PRECTOTCORR (1981 onward) and IMERG_PRECTOT (1998 onward) give two independent rainfall series.
- Water stress. GWETROOT and RZMC_PRCNTL track root-zone dryness. Combining rainfall with PET-type fields gives a simple water balance.
- Crop model inputs. ICASA output feeds DSSAT directly if the team wants to simulate yields for each rotation.
- POWER is the easiest first data source to wire up because it needs no login.

## Sources

- https://power.larc.nasa.gov/
- https://power.larc.nasa.gov/docs/services/api/
- https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- https://power.larc.nasa.gov/docs/services/api/system/
- https://power.larc.nasa.gov/docs/methodology/
- https://power.larc.nasa.gov/docs/methodology/communities/
- https://power.larc.nasa.gov/docs/methodology/meteorology/
- https://power.larc.nasa.gov/docs/faqs/
- https://power.larc.nasa.gov/docs/faqs/data/
- https://power.larc.nasa.gov/api/system/manager/parameters?community=AG&temporal=daily
- https://registry.opendata.aws/nasa-power/
