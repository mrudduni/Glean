# Web Soil Survey (WSS)

## What it is

Web Soil Survey is the NRCS web application for viewing and downloading soil survey data from the National Cooperative Soil Survey. NRCS calls it the single authoritative source of soil survey information. It serves the SSURGO detailed soil database and the STATSGO2 general soil map. NRCS states that soil maps and data exist online for more than 95 percent of US counties.

WSS is an interactive front end. The data behind it are SSURGO and STATSGO2, described in `ssurgo_statsgo.md`. For scripted access, the tool should use Soil Data Access (SDA) instead of WSS.

## Spatial and temporal resolution

- SSURGO polygons are mapped at scales from 1:12,000 to 1:63,360.
- STATSGO2 is mapped at 1:250,000 (1:1,000,000 in Alaska).
- NRCS refreshes soil data once a year in the Annual Soils Refresh.

## Coverage

United States and territories. Coverage gaps are shown on the SSURGO availability map (https://websoilsurvey.nrcs.usda.gov/DataAvailability/SoilDataAvailabilityMap.pdf).

## How to use it

The workflow has four tabs.

1. Area of Interest. Draw a rectangle or polygon, pick a whole soil survey area, or import a shapefile or zipped shapefile. Rectangle and polygon AOIs are limited to 100,000 acres. Whole soil survey area AOIs have no acreage limit.
2. Soil Map. View the map units in the AOI with descriptions.
3. Soil Data Explorer. Run ratings and reports under "Suitabilities and Limitations for Use", "Soil Properties and Qualities", and "Soil Reports". Results appear as tables and colored maps.
4. Shopping Cart. Combine maps and reports into one PDF. NRCS suggests ten items or fewer.

The "Download Soils Data" tab gives SSURGO tabular and spatial data for the AOI or a full survey area, and STATSGO2 by state or for the whole US. Tabular data come as text files with a Microsoft Access template. Spatial data come as ESRI shapefiles.

## Ratings relevant to rotation planning

WSS ratings in Soil Data Explorer include land capability class, farmland classification, erosion factors (K factor, T factor), hydrologic soil group, drainage class, available water capacity, organic matter, pH, and crop yields by map unit. The exact list of ratings in the current version was not checked item by item. The NRCS "Guide to Maps, Reports, and Tables" PDFs list them.

## Access and authentication

- Web application: https://websoilsurvey.nrcs.usda.gov/app/
- No account or key is needed.
- WSS has published operation hours and a Known Problems document. Downtime windows were not confirmed.
- An active WSS AOI can be imported into SDA through the `WSSAOIID` parameter of the SDA post.rest AOI service.

## License and terms

Soil survey data are public USDA data. NRCS asks users to cite WSS in this form: Soil Survey Staff, Web Soil Survey, U.S. Department of Agriculture, Natural Resources Conservation Service, accessed [date], https://websoilsurvey.sc.egov.usda.gov. A formal license statement was not found on the fetched pages.

## Limitations

- WSS is built for people, not programs. It has no documented REST API of its own.
- AOIs drawn by hand cap at 100,000 acres.
- Map units can hold one to three major soil components plus minor ones, so a small field may not match the dominant soil of its map unit.
- NRCS notes that onsite investigation is needed for some uses, such as soil quality assessments.

## How it plugs into the rotation tool

- The team can use WSS by hand to check SDA query results for a test farm and to produce a printable soil report for the user.
- WSS ratings such as land capability class, K factor and hydrologic soil group give a quick check on erosion risk and drainage before the tool ranks rotations.
- For automated runs, the tool should call SDA (see `ssurgo_statsgo.md`).

## Sources

- https://websoilsurvey.nrcs.usda.gov/app/
- https://www.nrcs.usda.gov/resources/data-and-reports/web-soil-survey
- https://www.nrcs.usda.gov/conservation-basics/soil/getting-started-with-web-soil-survey
- https://websoilsurvey.nrcs.usda.gov/app/MainHelp.htm
- https://websoilsurvey.nrcs.usda.gov/DataAvailability/SoilDataAvailabilityMap.pdf
- https://www.nrcs.usda.gov/sites/default/files/2022-09/WSS-Frequently-Asked-Questions.pdf
- https://sdmdataaccess.nrcs.usda.gov/WebServiceHelp.aspx
