# LANDFIRE (LF)

## What it is

LANDFIRE is a joint program of the US Department of the Interior (USGS) and the USDA Forest Service that maps vegetation, wildland fuels, disturbance and fire regimes for the whole country. It was built for fire and land management, so its value for crop rotation planning is indirect.

## Product groups

| Group | Content |
| --- | --- |
| Reference | LANDFIRE Reference Database (LFRDB) of plot data and contributed disturbance events |
| Disturbance | Annual and historical disturbance events (fire, treatments, insects, storms and more). The "Historical Disturbance" products were retired per a site alert |
| Vegetation | Existing vegetation type, cover and height, plus models of pre-European settlement vegetation (biophysical settings) |
| Fuel | Surface and canopy fuel characteristics, including Fire Behavior Fuel Models 13 and 40 (FBFM40), with seasonally adjusted FBFM40 releases |
| Historic Fire Regime | Pre-European settlement fire frequency and severity, succession classes (SClass), vegetation departure (VDep) and condition class (VCC) |
| Topographic | Elevation, slope, aspect |

The product list inside each group (for example the exact Existing Vegetation Type codes for agricultural land) was not read in this research. The LF Data Dictionary PDF is the reference.

## Versions

- LF 2025 Update, LF 2024 Update, LF 2023 Update, LF 2022 Update (current series).
- LF 2020 Update (archived), LF 2016 Base Map (also called the 2016 Remap), LF c2001 Base Map (archived).
- A "base map" is a full remapping from imagery and plot data. An "update" adjusts the base map for disturbance and succession.
- The LF 2025 Update was released in stages through 2026: R1 limited disturbance (January 2026), R2 southwest CONUS vegetation and fuel (April), R3 Alaska (May), R4 northwest CONUS (June), R5 disturbance (September), R6 rest of CONUS full extent (November), R7 LFRDB, SClass, VCC, VDep and Hawaii and Puerto Rico products (December). The schedule was last updated April 2026 and is subject to change. The home page reports that the 2025 full-extent CONUS products have been released.

## Spatial and temporal resolution

- 30 m raster. LANDFIRE warns that the appropriate application scale is much larger than 30 m and that single pixels or small pixel groups should not be used.
- Update cycle is roughly annual, with seasonal fuel products several times a year.

## Coverage and projection

| Extent | EPSG | Projection |
| --- | --- | --- |
| CONUS | 5070 | NAD 1983 Contiguous USA Albers |
| Alaska | 3338 | NAD 1983 Alaska Albers |
| Hawaii | 102007 | Hawaii Albers Equal Area Conic |
| Puerto Rico and US Virgin Islands | 5070 | NAD 1983 Contiguous USA Albers |
| Other insular areas | best-fit WGS 1984 UTM | |

The CONUS grid uses the same EPSG:5070 Albers projection as the CDL.

## Formats and access

- Full extent downloads by version, theme and region: https://www.landfire.gov/data/FullExtentDownloads
- LF Viewer with a data download tool, which can export in NAD83 Albers or best-fit UTM, and can build multi-band "landscape" GeoTIFFs (elevation, slope, aspect, fuel model, canopy cover) for fire models.
- LANDFIRE Product Service (LFPS), a programmatic clip-and-ship service mentioned in the FAQ. Its endpoint and parameters were not read here (not confirmed).
- LF Stream (https://www.landfire.gov/data/lf_stream), a streaming map service; details not read.
- Raster attribute tables come with viewer and mosaic downloads and on product pages for LFPS outputs.

## Authentication

No account was mentioned on the fetched pages for downloads. Whether LFPS needs a key is not confirmed.

## License and terms

LANDFIRE provides citation formats for its website and data products. A formal license statement was not on the fetched pages. As a USGS and USFS product it is presumably public domain, but this is not confirmed.

## Limitations

- Built for national and regional fire planning, not field-scale agriculture. LANDFIRE says it should not replace local products.
- Agricultural land is a minor focus. The CDL describes cropland in far more detail.
- 30 m pixels should not be read individually.

## How it plugs into the rotation tool

- LANDFIRE is a secondary source. Its topographic layers (slope, aspect, elevation) can serve as a backup to a DEM for erosion and frost-pocket risk.
- Fuel and fire regime layers around the farm can support a wildfire risk note for farms in the western states, for example near rangeland where residue or hay storage raises fire exposure.
- Disturbance layers can flag recent fire or other events near the farm.
- For crop history and soil the tool should rely on CDL and SSURGO instead.

## Sources

- https://www.landfire.gov
- https://www.landfire.gov/data
- https://www.landfire.gov/faqs
- https://www.landfire.gov/about-landfire
- https://www.landfire.gov/data/FullExtentDownloads
- https://www.landfire.gov/data/lf_stream
- https://www.landfire.gov/data-downloads/documents/LF_Data_Dictionary.pdf (not fetched)
- https://www.landfire.gov/data-downloads/documents/LF_Definitions_Quality_and_Standards_Annual_Report.pdf (not fetched)
