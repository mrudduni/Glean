# Open-Meteo historical weather API

Open-Meteo serves ERA5 and ERA5-Land reanalysis, plus forecasts, through a simple JSON API. It needs no key. It is the fastest way to get daily weather and FAO-56 reference ET for any point. See `era5.md` for the underlying reanalysis.

## Key facts

| Item | Value |
|---|---|
| Endpoint | `https://archive-api.open-meteo.com/v1/archive` |
| Source models | ERA5 (0.25 degree), ERA5-Land (0.1 degree) and others, picked by "best match" by default |
| Record | Follows ERA5 (see `era5.md`) |
| Variables we used | daily `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `et0_fao_evapotranspiration`, `shortwave_radiation_sum`; hourly `soil_moisture_0_to_7cm`, `soil_moisture_28_to_100cm` |
| Auth | None |
| Limits | The response headers showed a limit of 600 cost units per 60 seconds. One year of daily and hourly data at one point cost 18.3 units. The terms set the free tier at under 600 calls per minute, 5,000 per hour, 10,000 per day and 300,000 per month, for non-commercial use only. Public research and educational use count as non-commercial. |
| Licence | Data under CC BY 4.0, with attribution |

Sources: https://open-meteo.com/en/docs/historical-weather-api and https://open-meteo.com/en/terms

## What the probe found

All calls returned in 1.3 to 2.0 seconds. Results for 2024:

| Point | Grid cell used | Rain (mm) | FAO-56 ET0 (mm) | Highest Tmax (C) | Lowest Tmin (C) |
|---|---|---|---|---|---|
| Karnal cropland (29.69 N, 76.90 E) | 29.70 N, 76.95 E | 773.2 | 1,585.2 | 45.8 | 2.9 |
| Ludhiana cropland (30.90 N, 75.77 E) | 30.90 N, 75.73 E | 570.6 | 1,510.7 | 45.4 | 2.7 |
| Nashik cropland (20.05 N, 73.75 E) | 20.07 N, 73.78 E | 1,313.7 | 1,680.5 | 40.3 | 10.8 |

At Karnal, reference ET was about twice the rainfall in 2024. That gap is the irrigation demand the rotations compete on.

## Role in the tool

- A fast fallback and cross-check for NASA POWER, which stays primary for the NASA data rule.
- Its precomputed FAO-56 ET0 lets us check our own ET0 code against an outside value.
- Its forecast API can feed the in-season check mode.

## Gaps

- We have not compared Open-Meteo ET0 with POWER-derived ET0 at Karnal.
- The commercial terms matter only if the tool ever charges money.

## Sources

- https://open-meteo.com/en/docs/historical-weather-api
- https://open-meteo.com/en/terms
- Probe output: `research/04_data_probes/samples/global_probe_results.json`, key `open_meteo`, and `open_meteo_ludhiana_2024-05-31_10days.json`
