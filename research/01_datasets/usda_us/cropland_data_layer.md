# Cropland Data Layer (CDL), CropScape, CroplandCROS and Crop Sequence Boundaries

## What it is

The Cropland Data Layer is an annual crop-specific land cover raster for the contiguous United States, produced by USDA NASS. It classifies each pixel into one of more than 100 categories, including individual crops, double-crop combinations (for example code 26, "Dbl Crop WinWht/Soybeans"), fallow, pasture and non-agricultural classes. NASS trains the classifier on Farm Service Agency Common Land Unit (CLU) records for crops and on NLCD for non-crop land.

CropScape (nassgeodata.gmu.edu/CropScape) is the long-running web viewer and web service built with George Mason University. NASS now points users to CroplandCROS (https://croplandcros.scinet.usda.gov/) as the main viewer and download site. The CropScape home page returned a login-required error during this research, but its developer help and web service example pages loaded.

## Spatial and temporal resolution

- 30 m for 2008 to 2023.
- 10 m from 2024 onward. NASS also publishes a 30 m nearest-neighbor resampled version of the 10 m years for consistency with the historical series.
- One map per year, covering the growing season. A winter wheat field planted in fall 2009 is labeled in the 2010 CDL, since NASS uses harvest year.
- Raster size: 316,295 x 480,509 pixels at 10 m and 96,523 x 153,811 at 30 m.

## Coverage and years

- Contiguous US, bounding box roughly 129.3 W to 73.2 W and 21.8 N to 49.0 N.
- The metadata gives 1997 as the beginning date. Early years cover only some states. The full CONUS series runs from 2008 (the abstract describes 2008 to 2023 CDLs at 30 m). The exact state-by-year coverage before 2008 was not checked.
- The 2025 CDL was released on 27 February 2026.
- A separate Hawaii CDL exists at 10 m for 2023, 2024 and 2025 (released 12 June 2026).

## Formats and projection

- GeoTIFF or Cloud Optimized GeoTIFF.
- Projection: Albers Conical Equal Area, EPSG:5070 (same grid family as NLCD), NAD83, meters. The FAQ notes an offset from the standard North America Albers definition.
- NASS does not offer a vector (shapefile) version.

## Accuracy

The metadata states that producer's accuracy is generally 85 to 95 percent for the major crop categories. NASS publishes per-state confusion matrices. Pixel counts are biased (usually downward) compared with official acreage, so NASS warns that CDL acreage needs bias correction and points users to QuickStats for official estimates.

## Access methods

### Downloads

- National and state downloads: NASS "National Download" page and CroplandCROS.
- NRCS Geospatial Data Gateway (https://datagateway.nrcs.usda.gov/).
- Code list with names and colors: `cdl_codes_names.xlsx` linked from the FAQ.

### CropScape web services (CDLService)

WSDL: `https://nassgeodata.gmu.edu/axis2/services/CDLService?wsdl`. Operations are GetCDLValue, GetCDLFile, GetCDLImage, GetCDLStat, GetCDLComp, ExtractCDLByValues and GetCDLPDF. Coordinates and bounding boxes use the Albers projection in meters. Requests work over GET, POST or SOAP. Examples from the official help page:

```
# Crop code at one point (x, y in Albers meters)
https://nassgeodata.gmu.edu/axis2/services/CDLService/GetCDLValue?year=2018&x=1551565.363&y=1909363.537

# Clip CDL for a county (FIPS), several counties, a bounding box, or a polygon
https://nassgeodata.gmu.edu/axis2/services/CDLService/GetCDLFile?year=2018&fips=19015
https://nassgeodata.gmu.edu/axis2/services/CDLService/GetCDLFile?year=2018&bbox=130783,2203171,153923,2217961
https://nassgeodata.gmu.edu/axis2/services/CDLService/GetCDLFile?year=2018&aoiURL=https://crop.csiss.gmu.edu/data/York_SF_watershed.zip

# Acreage statistics by class (txt, csv or json)
https://nassgeodata.gmu.edu/axis2/services/CDLService/GetCDLStat?year=2018&bbox=130783,2203171,153923,2217961&format=json

# Change matrix between two years
https://nassgeodata.gmu.edu/axis2/services/CDLService/GetCDLComp?year1=2018&year2=2017&bbox=130783,2203171,153923,2217961&format=json

# Keep only selected crop codes (1 = corn, 5 = soybeans) from a returned GeoTIFF
https://nassgeodata.gmu.edu/axis2/services/CDLService/ExtractCDLByValues?file=https://nassgeodata.gmu.edu/webservice/nass_data_cache/byfips/CDL_2018_19015.tif&values=1,5
```

GetCDLFile returns XML with a URL to a cached GeoTIFF, which the other operations accept as input. CropScape also offers OGC WMS and WCS for CDL layers.

### CroplandCROS REST APIs

The NASS FAQ says CroplandCROS offers REST APIs and that error code 498 means an invalid or expired token, fixed by generating a new token through an ArcGIS Online or Portal for ArcGIS account. Whether anonymous access works for all CroplandCROS endpoints was not confirmed.

### Google Earth Engine

NASS announced the ACTIVE viewer, built on Google Earth Engine. A CDL collection in the Earth Engine catalog exists (USDA/NASS/CDL) but its year range was not checked here.

## Derived products

NASS lists a Cultivated Layer, Crop Frequency Data Layers, a Confidence Layer and Crop Sequence Boundaries. Details for the first three were not fetched.

### Crop Sequence Boundaries (CSB)

CSB, built with USDA ERS, delineates field polygons from the history of CDL pixels and attaches the crop sequence to each field.

- Each release covers an 8-year window. Windows exist for every span from 2008-2015 to 2018-2025.
- The 2018-2025 release came out on 27 March 2026. The page also says the "current version is v2024", which looks inconsistent with the 2025 release and is not confirmed.
- Polygons represent single-crop fields, not ownership parcels. They come from satellite and public data, not from FSA records, and hold no personal information.
- National zipped downloads, for example `https://www.nass.usda.gov/sites/default/files/Research_and_Science/Crop-Sequence-Boundaries/datasets/NationalCSB_2018-2025_rev23.zip`. File sizes were not checked and nothing was downloaded.
- NASS publishes the code on GitHub so users can build custom time windows.

## Authentication

None for downloads or the CropScape CDLService. CroplandCROS REST services may need an ArcGIS token (see above).

## License and terms

NASS states that the CDL is public domain and free to redistribute. Farmer-reported data are not revealed or derivable from the public CDL.

## Limitations

- Accuracy drops for minor crops and in areas with little FSA ground reference. Producer's accuracy of 85 to 95 percent applies to major crops only.
- A pixel holds one label per year, so cover crops are not mapped as a class. Double-crop codes capture only some sequences.
- The switch from 30 m to 10 m in 2024 changes edge effects and small-field detail. The tool should use the 30 m resampled version when it compares with earlier years.
- Pixel-count acreage is biased.
- CDL categories and colors have changed over the program's history (noted in the FAQ).

## How it plugs into the rotation tool

- CDL gives the farm's historical rotation. For a field polygon, the tool reads the majority crop code for each year from 2008 onward and reconstructs the current rotation (for example corn-soybean, or continuous corn).
- CSB gives ready-made field boundaries with 8-year crop sequences. The tool can use them when the user does not draw a field.
- GetCDLComp and county-level CDL statistics show how common each rotation is in the surrounding area, which signals local market and agronomic viability.
- The tool should report CDL classification uncertainty, especially for minor crops, as a data gap.

## Sources

- https://nassgeodata.gmu.edu/CropScape/ (login required error)
- https://nassgeodata.gmu.edu/CropScape/devhelp/help.html
- https://nassgeodata.gmu.edu/CropScape/devhelp/getexamples.html
- https://nassgeodata.gmu.edu/CropScape/devhelp/cropscapews.html
- https://www.nass.usda.gov/Research_and_Science/Cropland/SARS1a.php
- https://www.nass.usda.gov/research-and-science/cropland/sarsfaqs2
- https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php
- https://croplandcros.scinet.usda.gov/
- https://datagateway.nrcs.usda.gov/
