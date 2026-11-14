# CGWB groundwater levels

The Central Ground Water Board (CGWB) measures water levels in a national network of monitoring wells. For Haryana these measurements are the most direct evidence of the groundwater decline that drives the whole rotation question.

## Key facts

| Item | Value |
|---|---|
| What | Depth to water below ground level, in metres, at each monitoring well |
| Haryana file | `GWL_Manual_Quarterly_CGWB_HR_1991_2020.csv`, 4.2 MB, 33,341 rows, 1,307 stations |
| Actual years in the file | 1996 to 2020, although the file name says 1991 |
| Months | Mainly January, May, August and November (quarterly manual readings) |
| Fields | station, district, tehsil, block, village, latitude, longitude, date and time, water level |
| Portal | National Water Data Portal (NWDP), a CKAN site at https://nwdp.nwic.gov.in. India-WRIS (https://indiawris.gov.in/wris) shows the same data in a viewer. |
| Access | CKAN API `resource_show`, then a direct CSV download |
| Auth | None. The download worked without a login. |
| Licence | Listed as "Other (Open)". The exact terms are not confirmed. |
| Updates | File last updated 2025-03-05. NWDP also lists hourly and six-hourly telemetry datasets from CGWB. |

Source: https://nwdp.nwic.gov.in/en/dataset/gwl-manual-quarterly-central-ground-water-board-department/resource/1386c95c-14e4-4dae-9697-bc738d23a30e

## What the probe found for the pilot districts

We used readings from April to June, before the monsoon recharge. For each year we took the median depth over all wells in the district. We fitted a straight line for each well with at least 10 pre-monsoon years.

| District | Wells | Median depth 2000 (m) | Median depth 2010 (m) | Median depth 2019 (m) | Wells with 10+ years | Median fall (m per year) | Middle half of wells |
|---|---|---|---|---|---|---|---|
| Karnal | 135 | 7.8 | 16.5 | 18.9 | 16 | 0.66 | 0.44 to 0.87 |
| Kurukshetra | 111 | 10.2 | 28.9 | 37.9 | 10 | 1.15 | 1.06 to 1.28 |
| Kaithal | 67 | 5.5 | 15.7 | 27.9 | 15 | 0.53 | 0.32 to 0.75 |

Caveat: the set of wells read changes from year to year, so the yearly medians partly reflect which wells were read. The per-well slopes avoid that problem and still show a fall at almost every long-record well.

These are our own numbers from the CGWB file. Before the tool shows them, a hydrologist should check them against CGWB's district reports.

## Role in the tool

- The local, ground-truth groundwater trend next to GRACE, which sees only a regional signal at about 300 km.
- The "why this matters" panel can show the nearest wells and their trend, with distance from the field.
- Rotation water savings can be expressed as "metres of water table per decade" only with care. That conversion needs specific yield, which varies by aquifer, so treat it as a stretch feature with a clear caveat.

## Gaps

- 2021 onward is not in this file. The telemetry datasets may fill that gap, and we have not probed them.
- Specific yield values for the Karnal aquifers, from CGWB aquifer mapping reports.

## Sources

- https://nwdp.nwic.gov.in/en/dataset/gwl-manual-quarterly-central-ground-water-board-department/resource/1386c95c-14e4-4dae-9697-bc738d23a30e
- https://indiawris.gov.in/wris
- https://un-igrac.org/data/country-profiles/india/
- The analysis script ran from the session scratchpad. It is a 15-line pandas summary and is easy to redo in the region-pack pipeline.
