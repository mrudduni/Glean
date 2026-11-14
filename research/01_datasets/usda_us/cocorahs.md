# CoCoRaHS (Community Collaborative Rain, Hail and Snow Network)

## What it is

CoCoRaHS is a volunteer network that measures precipitation with standard 4-inch manual rain gauges and reports it online. The Colorado Climate Center at Colorado State University houses the network. It began in 1998 after the July 1997 Fort Collins flood (per the METplus dataset description) and now has tens of thousands of observers. CoCoRaHS records also feed NOAA NCEI's GHCN-Daily.

## Report types

The View Data menu lists daily precipitation, daily comments, significant weather, multiple-day accumulation, condition monitoring (with summary charts), evapotranspiration, soil moisture, hail, frost, optics, snowflake and thunder reports. Summary reports include water year summaries, station precipitation, snow and water balance summaries, total precipitation summaries and a rainy days report.

## Spatial and temporal resolution

- Point observations at volunteer locations. Density follows population, so rural farm areas can be sparse.
- One daily report per station for the 24 hours ending at the observer's morning reading time (7:00 AM local preferred, so windows differ between stations).
- Precipitation to the nearest 0.01 inch, new snowfall to 0.1 inch, snow depth to 0.5 inch, snow water equivalent optional.

## Coverage

United States, Canada, Puerto Rico, US Virgin Islands, Guam and the Bahamas (METplus description). Records start in 1998 in Colorado and expand over later years.

## Formats

The Export Manager offers XML, XML Compact, CSV, SHEF and SHEF Snow. Report types available for export are Daily, Multi-Day, Hail and Significant Weather. Users can filter by state and by report date or timestamp.

## Access methods

- Interactive maps: https://www.cocorahs.org/Maps and https://data.cocorahs.org/cocorahs/maps/
- View Data lists and station reports: https://www.cocorahs.org/ViewData/
- Data Explorer for station histories: https://dex.cocorahs.org
- Export Manager form: https://data.cocorahs.org/cocorahs/Export/ExportManager.aspx
- GHCN-Daily at NCEI for CoCoRaHS stations merged with other networks.

Bulk CSV export URL (documented by the NCAR METplus project, not by CoCoRaHS itself; it returned 15,749 records for one day in their test):

```
curl -o cocorahs_20220914.csv \
 "https://data.cocorahs.org/cocorahs/export/exportreports.aspx?ReportType=Daily&Format=CSV&StartDate=2022-09-14&EndDate=2022-09-14"
```

Adding `&Units=Metric` returns millimeters. Omitting the state parameter returns all stations. The exact state parameter name was not confirmed. A formal, documented CoCoRaHS REST API was not found.

## Authentication

None to view or export. An account is only needed to submit observations.

## License and terms

Unless otherwise noted, CoCoRaHS content and data are released under the Creative Commons Attribution 4.0 license. CoCoRaHS asks users to acknowledge the source when displaying data. Data come "as is" with no liability for missing data or misinterpretation.

## Limitations

- Station locations follow volunteers, so a given farm may have no nearby gauge.
- Observation windows vary by station.
- Daily totals only; no sub-daily timing.
- Quality control is partly retrospective (coordinator review and the CoCoRaHS Error Check Assistant), so recent reports may still hold errors such as false zeros or wrong dates.
- Snow water equivalent is reported less consistently than rain.

## How it plugs into the rotation tool

- CoCoRaHS gives ground-truth rainfall near the farm. The tool can compare it with PRISM grid values and with NASA precipitation products (for example IMERG) to show how well the gridded data match local gauges.
- Condition monitoring, soil moisture and evapotranspiration reports give qualitative drought or wetness evidence for recent seasons, which helps explain risk.
- Gauge density near the farm is a data-quality indicator the tool can report.

## Sources

- https://www.cocorahs.org/Maps
- https://www.cocorahs.org/ViewData/
- https://www.cocorahs.org/Content.aspx?page=datausagepolicy
- https://data.cocorahs.org/cocorahs/Export/ExportManager.aspx
- https://data.cocorahs.org/cocorahs/maps/
- https://metplus.readthedocs.io/en/develop/Verification_Datasets/datasets/cocorahs.html
- https://dex.cocorahs.org
