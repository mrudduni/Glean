# SSURGO, STATSGO2, gSSURGO, gNATSGO and Soil Data Access

Note on the given link: https://www.nrcs.usda.gov/resources/data-and-reports/soils now loads the Iowa NRCS soils program page. It links to Web Soil Survey, SoilWeb and the SSURGO/STATSGO2 metadata page. The national product pages listed in the sources section hold the details below.

## Products at a glance

| Product | What it is | Spatial detail | Format | Coverage |
| --- | --- | --- | --- | --- |
| SSURGO | Detailed soil survey, the NRCS flagship soil database | Vector polygons mapped at 1:12,000 to 1:63,360 | ESRI shapefile (geographic coordinates) plus text tables for an MS Access template; bundled by soil survey area | More than 90 percent of the US and territories; some land unmapped |
| STATSGO2 (US General Soil Map) | Generalized soil association map | 1:250,000 (1:1,000,000 in Alaska) | Shapefile in WGS84; pipe-delimited text tables | All US states and territories |
| gSSURGO | SSURGO packaged as an ESRI file geodatabase with a raster map unit layer | 10 m raster for state tiles; 30 m raster for the CONUS tile | ESRI file geodatabase | State and CONUS tiles |
| gNATSGO | Composite of SSURGO, STATSGO2 (gap fill) and Raster Soil Surveys | 10 m raster for state databases; 30 m for national | GeoPackage (SQLite) with 70 related tables plus GeoTIFF rasters keyed on MUKEY; no vector map units | Complete coverage of US and territories |

All products are refreshed once a year in the Annual Soils Refresh. Tabular soil properties are stored as low, representative ("_r") and high values for most properties.

### gSSURGO Valu1 table

gSSURGO and the SSURGO portal add a "Valu1" table with 57 ready-to-map attributes summarized to the map unit. Examples include soil organic carbon (g C/m2), available water storage (mm), National Commodity Crop Productivity Index (NCCPI) version 3, root zone depth of commodity crops (cm), available water storage in the root zone, a drought-vulnerable landscape flag (152 mm or less root-zone available water storage), and potential wetland soil landscapes.

## Data model and key attributes

SSURGO has a nested structure. A map unit (`mapunit`, key `mukey`) holds one or more components (`component`, key `cokey`, with percent `comppct_r`). Each component holds horizons (`chorizon`, key `chkey`) with top and bottom depths. To get one value per map unit, the tool must aggregate horizons by depth and then components by percent, or use Valu1 or Soil Data Viewer outputs.

The column names below are standard SSURGO names. The fetched pages did not list them, so they should be checked against the SDM "Tables and Columns" metadata report before coding.

| Table | Column | Meaning | Use in rotation tool |
| --- | --- | --- | --- |
| mapunit | mukey, musym, muname | Map unit key, symbol, name | Join to rasters and polygons |
| component | comppct_r, majcompflag | Component percent, major component flag | Weighting |
| component | slope_r | Representative slope (percent) | Erosion risk |
| component | hydgrp | Hydrologic soil group (A, B, C, D, dual classes) | Runoff and drainage risk |
| component | drainagecl | Drainage class | Suitability of wet-tolerant crops |
| component | nirrcapcl | Non-irrigated land capability class | Land suitability |
| chorizon | om_r | Organic matter (percent) | Soil health baseline |
| chorizon | awc_r | Available water capacity (cm/cm) | Drought risk |
| chorizon | kffact, kwfact | Erodibility factor (rock-free, whole soil) | Erosion (RUSLE K) |
| chorizon | sandtotal_r, silttotal_r, claytotal_r | Texture fractions | Texture class |
| chorizon | ph1to1h2o_r | pH in water | Crop pH limits |
| cocropyld | crop name, yield | Reported non-irrigated and irrigated yields by component | Yield priors |

## Soil Data Access (SDA)

SDA is the NRCS web service suite for SSURGO and STATSGO2. It queries the Soil Data Mart (SDM) database, which holds the official soil data for the United States and island jurisdictions.

### Services

| Service | URL | Purpose |
| --- | --- | --- |
| post.rest (Query, AOI, Interpretation, Report) | https://SDMDataAccess.sc.egov.usda.gov/Tabular/post.rest | SQL queries on tabular and spatial data; persistent AOIs |
| SOAP tabular | https://SDMDataAccess.sc.egov.usda.gov/Tabular/SDMTabularService.asmx | RunQuery method over SOAP |
| WFS (WGS84) | https://SDMDataAccess.sc.egov.usda.gov/Spatial/SDMWGS84Geographic.wfs | Features in EPSG 4326 |
| WFS (NAD83) | https://SDMDataAccess.sc.egov.usda.gov/Spatial/SDMNAD83Geographic.wfs | Features in EPSG 4269 |
| WFS (Web Mercator) | https://SDMDataAccess.sc.egov.usda.gov/Spatial/SDMWM.wfs | Features in EPSG 3857 |
| WMS | https://SDMDataAccess.sc.egov.usda.gov/Spatial/SDM.wms | Map images (OGC WMS 1.1.1) |

### post.rest query rules from the docs

- Requests must be HTTP POST. A browser URL will not work.
- Parameters: `QUERY` (required, SQL with one or more SELECT statements or a single Shape command), `FORMAT` (XML default, or JSON, JSON+COLUMNNAME, JSON+COLUMNNAME+METADATA, or `~` to echo the expanded query).
- A query returns at most 100,000 rows.
- Errors include "Invalid query", "Server error", "Your immediate query timed out" and "Memory limit".
- The AOI service (`SERVICE=aoi`, `REQUEST=create`) builds a persistent AOI from WKT or GeoJSON coordinates (`AOICOORDS`), a list of up to 1,000 map unit keys (`MUKEYLIST`), a survey area symbol (`SSA`), or an imported WSS AOI (`WSSAOIID`). The AOI persists for at least 24 hours and returns an id such as `{"id":12345}`.
- NRCS recommends reading the sample documents "Fundamental Query", "Discriminating between SSURGO and STATSGO", and "Constraining a Query to an Area of Interest" before writing queries.

### Example request

The JSON body form below is a common pattern for post.rest. The endpoint and FORMAT values are from the docs. The spatial macro `SDA_Get_Mukey_from_intersection_with_WktWgs84` appears in NRCS sample queries but was not confirmed on the pages fetched for this note.

```python
import requests

wkt = "point(-93.62 42.03)"   # lon lat, WGS84
sql = f"""
SELECT mu.mukey, mu.muname, c.cokey, c.compname, c.comppct_r, c.majcompflag,
       c.slope_r, c.hydgrp, c.drainagecl,
       h.hzdept_r, h.hzdepb_r, h.om_r, h.awc_r, h.kffact,
       h.sandtotal_r, h.silttotal_r, h.claytotal_r
FROM mapunit mu
JOIN component c ON c.mukey = mu.mukey
JOIN chorizon h ON h.cokey = c.cokey
WHERE mu.mukey IN (
  SELECT * FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('{wkt}')
)
ORDER BY c.comppct_r DESC, h.hzdept_r
"""
r = requests.post(
    "https://SDMDataAccess.sc.egov.usda.gov/Tabular/post.rest",
    json={"query": sql, "format": "JSON+COLUMNNAME"},
    timeout=60,
)
rows = r.json()["Table"]   # first row holds column names
```

To keep SSURGO and STATSGO2 apart, NRCS documents a "Discriminating between SSURGO and STATSGO" sample. STATSGO2 records sit under the area symbol "US" in `legend.areasymbol` (this convention is from SDA practice and was not confirmed on the fetched page).

### Metadata reports

The SDA Query Help page offers a Domains report, a Table Column Descriptions report, a Tables and Columns report (with units, min and max values), a Unique Constraints report and a Table Relationships report. These are the data dictionary for SSURGO and STATSGO2.

## Soil Data Viewer and SSURGO Portal

The gNATSGO page recommends the SSURGO Portal Soil Data Viewer (SDV) to aggregate the 70 related tables into simple tables that join to the rasters. The gSSURGO page also offers the Soil Data Development Toolbox for ArcGIS, whose Create Soil Map tool replicates WSS and Soil Data Viewer maps with control over aggregation method and depth.

## SoilWeb

The UC Davis California Soil Resource Lab runs SoilWeb apps over SSURGO data for most of the US. They include a browser map, a Google Earth KML version, the Soil Series Extent Explorer, a Soil Series Data Explorer, a soil properties viewer, and phone apps. These are useful for manual checks. A documented public API for SoilWeb was not confirmed.

## POLARIS

POLARIS is a 30 m probabilistic soil property map for CONUS derived from SSURGO by Duke University researchers. It was not covered by the fetched NRCS pages, and its details are not confirmed here.

## Authentication

None. SDA, WSS, gSSURGO and gNATSGO downloads need no key or account. gSSURGO and gNATSGO are hosted on NRCS Box folders (https://nrcs.app.box.com/v/soils).

## License and terms

Public USDA data. NRCS provides citation formats, for example "Soil Survey Staff (2026). Gridded national soil survey geographic (gNATSGO) database. USDA Natural Resources Conservation Service." No restrictive license was found on the fetched pages.

## Limitations

- SSURGO map units mix components, so field-level soil can differ from the map unit summary.
- Mapping scale (down to 1:63,360 in some areas) limits detail on small fields.
- SSURGO still has unmapped areas, which gNATSGO fills with coarser STATSGO2.
- The CONUS gSSURGO raster is 30 m only, and the CONUS gSSURGO download is split into many files.
- SDA caps queries at 100,000 rows and can time out on large AOIs.

## How it plugs into the rotation tool

- SSURGO texture, organic matter, available water capacity and K factor give the farm's soil baseline. The tool uses them to judge drought risk, erosion risk and soil health starting point for each candidate rotation.
- Hydrologic soil group, drainage class and slope flag fields where wet or erosive conditions argue against certain crops or for cover crops.
- NCCPI and component crop yields give yield priors that QuickStats county yields can calibrate.
- The gNATSGO or gSSURGO raster (keyed on MUKEY) aligns with the CDL and NLCD rasters, which all use Albers equal area grids, so the tool can stack soil, crop history and land cover per pixel.

## Sources

- https://www.nrcs.usda.gov/resources/data-and-reports/soils
- https://www.nrcs.usda.gov/resources/data-and-reports/soil-survey-geographic-database-ssurgo
- https://www.nrcs.usda.gov/resources/data-and-reports/description-of-statsgo2-database
- https://www.nrcs.usda.gov/resources/data-and-reports/gridded-soil-survey-geographic-gssurgo-database
- https://www.nrcs.usda.gov/resources/data-and-reports/gridded-national-soil-survey-geographic-database-gnatsgo
- https://nrcs.usda.gov/resources/data-and-reports/ssurgo/stats2go-metadata
- https://sdmdataaccess.nrcs.usda.gov/WebServiceHelp.aspx
- https://sdmdataaccess.nrcs.usda.gov/QueryHelp.aspx
- https://nrcs.app.box.com/v/soils
- https://casoilresource.lawr.ucdavis.edu/soilweb-apps/
