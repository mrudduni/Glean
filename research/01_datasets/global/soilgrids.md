# SoilGrids 2.0

SoilGrids is ISRIC's global map of soil properties. Machine-learning models (quantile random forests) predict each property from the WoSIS soil profile database and global environmental covariates (Poggio et al. 2021, https://doi.org/10.5194/soil-7-217-2021). It is the main global fallback where no national soil survey is open, which includes our Haryana pilot area.

## Key facts

| Item | Value |
|---|---|
| Resolution | 250 m |
| Depths | 0-5, 5-15, 15-30, 30-60, 60-100, 100-200 cm |
| Values per pixel | mean, median (Q0.5), Q0.05, Q0.95, and an uncertainty layer |
| Properties | clay, sand, silt, soil organic carbon (soc), pH in water (phh2o), bulk density (bdod), CEC, total nitrogen, water content at 33 kPa and 1500 kPa (wv0033, wv1500), coarse fragments, organic carbon density and stock |
| Record | A single static map. No time series. |
| Access | REST point API at `https://rest.isric.org/soilgrids/v2.0/properties/query`, WCS at `https://maps.isric.org/mapserv`, and Cloud-Optimised GeoTIFFs at `https://files.isric.org/soilgrids/latest/data/` |
| Auth | None |
| Limits | ISRIC labels the REST API beta. A fair-use limit of 5 calls per minute is noted in our probe script; we did not find it on an ISRIC page, so it is not confirmed. The script waits 12 seconds between calls. |
| Licence | CC BY 4.0 according to ISRIC's data policy. The FAQ page we read does not state it, so confirm on the download page before submission. |

Source for the facts above: https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs.html (250 m, six depths, machine learning) and the probe output (properties, quantiles, units).

## Units need scaling

The API returns integers. Divide by `d_factor` (10 for the properties below) to get the target unit. The response includes the factor, so the code should read it rather than hard-code it.

| Property | Raw unit | Divide by | Target unit |
|---|---|---|---|
| clay, sand, silt | g/kg | 10 | percent |
| soc | dg/kg | 10 | g/kg |
| phh2o | pH times 10 | 10 | pH |

## What the probe found at Karnal

We queried the Karnal cropland point (29.69 N, 76.90 E) on 2026-11-14. The REST call took 15.9 seconds. The same call for Ludhiana and Nashik timed out with HTTP 504 after 181 seconds. Iowa took 70 seconds.

| Property, 0-5 cm | Mean | 90 percent range (Q0.05 to Q0.95) |
|---|---|---|
| Clay | 27.9 percent | 2.9 to 86.1 percent |
| Sand | 35.3 percent | 5.2 to 63.1 percent |
| Soil organic carbon | 14.3 g/kg | 2.0 to 40.5 g/kg |
| pH | 8.1 | 5.8 to 10.3 |

The mean pH of 8.1 fits the alkaline soils known in this belt. The 90 percent ranges are very wide, though. At this point SoilGrids cannot tell a sandy loam from a heavy clay. That gap matters, because texture sets water-holding capacity, and water-holding capacity drives the water balance.

## Check against measured soil at Karnal

Two Karnal station trials report measured topsoil. These are field plots at CSSRI, not our probe point, so they show the order of error rather than an exact test.

| Property | SoilGrids at our point (0-5 cm) | CSSRI measured |
|---|---|---|
| Texture | 27.9 percent clay, 35.3 percent sand | Loam with 19.9 percent clay (Jat et al. 2019); silty loam (Jat et al. 2020) |
| pH | 8.1 | 8.00 and 8.13 |
| Organic carbon | 14.3 g/kg | 7.6 g/kg and 4.8 g/kg |

pH agrees. SoilGrids puts organic carbon about two to three times higher than the measured plots, though both CSSRI values fall inside its 90 percent range. A Soil Health Card value should replace the SoilGrids mean whenever the farmer has one.

Sources: https://doi.org/10.1038/s41598-019-54086-1 and https://doi.org/10.1038/s41598-020-76035-z (both read in full).

## Role in the tool

- Default soil input for any field outside the US, always shown with its Q0.05 to Q0.95 range.
- The interval goes into the Monte Carlo runs, so soil uncertainty shows up in the final ranges.
- The interface asks the farmer for a soil test or a texture class ("sandy", "loam", "clay") and says how much this narrows the result. The Soil Health Card that Indian farmers already hold is the natural source.
- Do not use the REST API live in the app. Its latency and 504 errors make it unfit for a user request. Pre-cut the COGs for each region pack instead.

## Gaps

- We have not tested the COG route yet. It should be faster and needs no rate limit.
- We have not compared SoilGrids with Soil Health Card values for Karnal.

## Sources

- https://www.isric.org/explore/soilgrids/faq-soilgrids
- https://docs.isric.org/globaldata/soilgrids/
- Probe output: `research/04_data_probes/samples/global_probe_results.json`, key `soilgrids_rest`
