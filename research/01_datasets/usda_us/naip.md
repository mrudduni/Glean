# National Agriculture Imagery Program (NAIP)

## What it is

NAIP acquires aerial orthoimagery over the contiguous US during the agricultural growing season ("leaf-on"). The USDA Farm Production and Conservation Business Center (FPAC-BC) Geospatial Enterprise Operations (GEO) Branch in Salt Lake City runs it. FSA county offices use NAIP as their GIS base layer and to maintain Common Land Unit (CLU) field boundaries. The program aims to make imagery available within a year of acquisition.

## Spatial and spectral resolution

- 1 m ground sample distance from 2003 to 2017.
- 0.6 m standard from 2018, with an option for 0.3 m considered over coastal states (USGS EROS page). The AWS registry describes the range as 30 cm to 100 cm.
- Natural color (red, green, blue) or four bands (red, green, blue, near infrared).
- Tiles cover a 3.75-minute by 3.75-minute quarter quadrangle plus a 300 m buffer and may contain up to 10 percent cloud cover.
- Positional accuracy: since 2009 all states meet a specification that well-defined test points fall within 6 m of true ground at 95 percent confidence.

## Temporal coverage and cycle

- Archive from 2003 to present.
- The repeat cycle moved from 5 years (2003-2009) to no longer than 3 years. In practice a variable number of states is flown each year, and each state is refreshed every two to three years.
- Recent status from the NAIP hub: the 2025 acquisition finished by 18 December 2025, with imagery delivered for 18 states; 21 states of NAIP 2024 had been published to the NAIP_CONUS_Prime image service by 21 November 2025. NAIP 2024 image dates were posted on 3 February 2026.
- Each state is flown once in its cycle year, so NAIP gives one snapshot per state every two to three years, not a seasonal series.

## Formats and projection

- USGS EarthExplorer serves GeoTIFF and JPEG2000 (10:1 lossy compression). Quarter quads use UTM on NAD83. JPEG2000 data after 2013 use WGS84 Web Mercator.
- AWS buckets hold MRF, COG and raw GeoTIFF copies.

## Access methods

| Route | Details | Auth |
| --- | --- | --- |
| NAIP GeoHub | https://naip-usdaonline.hub.arcgis.com/ for search, viewing, image dates and acquisition dashboards | None |
| USDA image services | ArcGIS REST at https://gis.apfo.usda.gov/arcgis/rest/services/NAIP (includes NAIP_CONUS_Prime) | None for public services (not checked per service) |
| USGS EarthExplorer | "Aerial Photography" category, GeoTIFF or JPEG2000 | Free USGS login for downloads (standard EarthExplorer rule, not confirmed on the NAIP page) |
| AWS Open Data | Buckets `naip-analytic` (4-band MRF and COG), `naip-source` (raw 4-band GeoTIFF), `naip-visualization` (3-band RGB COG), region us-west-2, all Requester Pays. Catalog covers 2010 to 2023 for most products | AWS account; requester pays transfer costs |
| Microsoft Planetary Computer | NAIP collection with a STAC API; the dataset page loaded only its shell during this research | Not confirmed; Planetary Computer usually needs no key for STAC search and signs asset URLs through its SAS endpoint |
| FPAC-BC ordering | Imagery acquired but not yet online can be ordered through APFO customer service | Order process |

AWS CLI example from the registry:

```
aws s3 ls --request-payer requester s3://naip-analytic/
```

Planetary Computer STAC example (pattern from Microsoft's public notebooks; collection id `naip`; not tested in this research):

```python
import pystac_client, planetary_computer
catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)
items = catalog.search(collections=["naip"],
                       intersects={"type": "Point", "coordinates": [-93.62, 42.03]},
                       datetime="2019-01-01/2023-12-31").item_collection()
```

## License and terms

USGS lists NAIP media as public domain. The AWS registry lists "Public Domain with Attribution" and asks users to cite NAIP on AWS with the access date.

## Limitations

- One acquisition date per state every two to three years. It cannot show crop phenology within a season.
- Flight dates vary across a state and within the growing season, so crop appearance differs from tile to tile. The Image Dates hub gives dates.
- Tiles can contain up to 10 percent cloud.
- Four-band data are not radiometrically calibrated surface reflectance (a general NAIP property; not stated on the fetched pages), so NDVI comparisons across years are rough.
- AWS buckets charge the requester for data transfer.

## How it plugs into the rotation tool

- NAIP at 0.6 m lets the user see and confirm field boundaries before the tool pulls CDL, SSURGO and PRISM for the field. It is a good base map for the field-drawing step.
- It can show visible features that affect rotation choices, such as grassed waterways, gullies, wet spots and terraces.
- Near-infrared bands give a coarse vegetation check for the acquisition date, which can confirm the CDL crop label for that year.

## Sources

- https://naip-usdaonline.hub.arcgis.com/
- https://gis.apfo.usda.gov/arcgis/rest/services/NAIP
- https://www.usgs.gov/centers/eros/science/usgs-eros-archive-aerial-photography-national-agriculture-imagery-program-naip
- https://registry.opendata.aws/naip/
- https://planetarycomputer.microsoft.com/dataset/naip (page shell only)
- https://github.com/microsoft/PlanetaryComputerExamples/blob/main/datasets/naip/naip-example.ipynb (not fetched)
- https://catalog.data.gov/dataset/national-agriculture-imagery-program-naip-imagery
- https://www.fpacbc.usda.gov/geospatial-services/imagery-programs/naip-imagery (404)
