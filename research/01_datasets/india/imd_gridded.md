# IMD gridded rainfall and temperature

The India Meteorological Department (IMD) in Pune publishes daily gridded rainfall and temperature for India, built from its rain gauge and weather station network. It is the official reference for Indian rainfall, and Indian agronomists will expect to see it.

## Key facts

| Item | Rainfall | Max and min temperature |
|---|---|---|
| Resolution | 0.25 degree | 1 degree |
| Grid | 135 x 129 points, from 6.5 N, 66.5 E to 38.5 N, 100.0 E | 31 x 31 points, from 7.5 N, 67.5 E to 37.5 N, 97.5 E |
| Archive record | 1901 to 2024 | 1951 to 2024 |
| Unit | mm per day | degrees C |
| Missing value | -999.0 | 99.9 |
| Format | Raw little-endian float32 binary (`.grd`), one record per day, 365 or 366 per year | Same |
| Citation | Pai et al. 2014, MAUSAM 65(1): 1-18 | Srivastava et al. 2009, Atmospheric Science Letters, DOI 10.1002/asl.232 |

From 2008 on, the temperature grid uses only about 180 stations that report in real time, so recent years are less dense than older ones.

Sources: https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_Bin.html and https://imdpune.gov.in/cmpg/Griddata/Max_1_Bin.html

## Access

There is no API. Each file comes from an HTML form that sends a POST request. The probe script reproduces these:

| Data | POST URL | Form field | Size |
|---|---|---|---|
| Archive daily rainfall for one year | `https://imdpune.gov.in/cmpg/Griddata/rainfall.php` | `rain=2023` | About 25 MB, returned as `ind2023_rfp25.grd` |
| Archive daily Tmax for one year | `https://imdpune.gov.in/cmpg/Griddata/maxtemp.php` | `maxtemp=2023` | 1.4 MB |
| Real-time daily rainfall for one day | `https://imdpune.gov.in/cmpg/Realtimedata/Rainfall/rain.php` | `rain=15072025` (DDMMYYYY) | 69,660 bytes |

No login is needed. IMD's pages state a disclaimer of liability but no explicit licence. Licence status is not confirmed, so the project page should name IMD and cite the papers above.

## What the probe found

| Check | Karnal cropland | Ludhiana cropland | Nashik cropland |
|---|---|---|---|
| Real-time rain, 15 July 2025 (mm) | 0.0 | 12.1 | 17.3 |
| Real-time rain, 1 August 2025 (mm) | 18.2 | 1.1 | 2.6 |
| Highest Tmax in 2023 (C) | 43.7 | 43.0 | 39.4 |
| Mean Tmax in 2023 (C) | 30.8 | 30.4 | 32.8 |
| Days over 40 C in 2023 | 16 | 11 | 0 |

The binary layouts match IMD's documentation exactly: 135 x 129 x 4 bytes per rainfall day, and 31 x 31 x 365 x 4 bytes for a temperature year.

## Role in the tool

- The Indian ground-truth rainfall next to IMERG and CHIRPS. Showing all three tells the farmer how much the sources agree.
- Days over 40 C and terminal heat in March feed the wheat heat-risk flag. The 1 degree grid is coarse, so use POWER or ERA5 for field detail and IMD as the check.
- The archive back to 1901 gives a long drought climatology.

## Gaps

- We have not read the real-time Tmax and Tmin files.
- The licence is not confirmed.

## Sources

- https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_Bin.html
- https://imdpune.gov.in/cmpg/Griddata/Max_1_Bin.html
- Probe output: `research/04_data_probes/samples/global_probe_results.json`, key `india`
