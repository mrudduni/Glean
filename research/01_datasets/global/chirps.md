# CHIRPS rainfall (v2 and v3)

CHIRPS is the Climate Hazards Center's rainfall dataset. It blends infrared satellite rainfall estimates with rain gauge data. FEWS NET uses it for drought early warning. Version 3 is the current release.

## Key facts

| Item | v2.0 | v3.0 |
|---|---|---|
| Resolution | 0.05 degree (about 5.5 km) | 0.05 degree |
| Coverage | 50 S to 50 N | 60 S to 60 N |
| Record | 1981 onward | 1981 onward |
| Steps | daily, pentad, dekad, monthly | daily, pentad, dekad, monthly |
| Monthly COG path | `https://data.chc.ucsb.edu/products/CHIRPS/v2.0/global_monthly/cogs/chirps-v2.0.{y}.{mm}.cog` | `https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/cogs/chirps-v3.0.{y}.{mm}.cog` |
| Auth | None | None |
| Licence | Public domain (CC0 waiver by the producer) | Public domain (CC0 waiver by the producer) |

v3 has two daily versions in Google Earth Engine: one built on ERA5 and one built on IMERG. The IMERG version uses NASA's GPM data inside it.

Source for coverage, paths and licence: probe output, https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHC_CHIRPS_V3_DAILY_SAT and https://fews.net/new-version-fews-nets-chirps-rainfall-dataset-enhances-global-monitoring-extreme-weather-events

## What the probe found

We read single pixels from the monthly COGs with HTTP range requests. One read took 14 to 72 seconds. CHC's server is slow, so the region pack should cache the needed tiles.

Kharif 2024 rainfall at the Karnal cropland point (29.69 N, 76.90 E), in mm:

| Month | v2.0 | v3.0 |
|---|---|---|
| June | 37.6 | 22.6 |
| July | 242.7 | 228.1 |
| August | 291.1 | 249.8 |
| September | 147.3 | 92.9 |
| Total | 718.7 | 593.4 |

The two versions differ by 125 mm, or about 17 percent of the v2 total, for the same season and pixel. That gap is a direct, measurable sign of input uncertainty. The tool should show it as a rainfall range, for example by drawing v2, v3, IMERG and IMD side by side.

## Role in the tool

- A second rainfall source next to GPM IMERG, and the long record (1981 onward) for climatology and drought percentiles.
- Its spread against IMERG and IMD feeds the rainfall uncertainty band.
- The NASA source stays primary for the Global Award rule. CHIRPS is a cross-check.

## Gaps

- We have not checked the v3 latency for the final monthly product.
- We have not compared CHIRPS with IMD gridded rainfall at Karnal for a full season.

## Sources

- https://www.chc.ucsb.edu/data/chirps3
- https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHC_CHIRPS_V3_DAILY_SAT
- https://docs.digitalearthafrica.org/en/latest/data_specs/CHIRPS_specs.html (licence text)
- Probe output: `research/04_data_probes/samples/global_probe_results.json`, key `chirps`
