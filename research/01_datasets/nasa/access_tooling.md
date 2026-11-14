# Access tooling for NASA Earth data

This note covers the shared tools that the dataset notes in this folder point to. It explains what each tool does, when to use it, and gives example requests taken from the official docs.

## Quick choice

| Need | Tool |
| --- | --- |
| Make an account that unlocks downloads | Earthdata Login |
| Find a dataset or granule by hand | Earthdata Search |
| Find granules from code | CMR Search API, or `earthaccess` |
| Get a small, field-sized subset as GeoTIFF, NetCDF or CSV | AppEEARS (web or REST API) |
| Download or stream whole files in Python | `earthaccess` |
| Show a satellite basemap or daily image layer in the app | GIBS (WMTS), browse in Worldview |
| Quick area-average time series or map, no code | Giovanni |
| Large-scale processing without downloads | Direct S3 access from AWS us-west-2 |

## Earthdata Login

Earthdata Login is NASA's free single sign-on for Earth science data (https://urs.earthdata.nasa.gov). Almost every download route needs it: DAAC HTTPS links, AppEEARS, `earthaccess`, and direct S3 credentials. Search and browse tools (Earthdata Search browsing, CMR searches for public collections, GIBS, Worldview) work without login.

The `earthaccess` docs say the library looks for credentials in a `.netrc` file or in the environment variables `EARTHDATA_USERNAME` and `EARTHDATA_PASSWORD`, and otherwise prompts for them. For a hackathon app, store credentials in environment variables on the server and never in the repository or the browser.

Some DAACs (GES DISC, for example) also require the user to approve that DAAC's application in the Earthdata Login profile before the first download. This is standard practice but was not confirmed on the pages fetched for this note.

## Earthdata Search

Earthdata Search (https://search.earthdata.nasa.gov) is the web interface for finding collections and granules across all NASA DAACs. Users filter by keyword, area, date and attributes, preview footprints, and then download or send orders to subsetting services. For cloud-hosted collections, the download panel has an "AWS S3 Access" tab that lists `s3://` links for in-region use (per NASA Openscapes and PO.DAAC tutorials). GIBS imagery shows up in Earthdata Search as previews.

## CMR Search API

The Common Metadata Repository (CMR) is the catalog behind Earthdata Search. Its search API is public and returns JSON, UMM-JSON, XML and other formats. Key facts from the API docs:

- Collections live at `https://cmr.earthdata.nasa.gov/search/collections` and granules at `https://cmr.earthdata.nasa.gov/search/granules`. Add `.json` or `.umm_json` for those formats.
- `page_size` defaults to 10 and has a maximum of 2000.
- For deep paging, use the `CMR-Search-After` header. Each response returns a value in that header, and the next request sends it back. `page_num` and `offset` are deprecated.
- The docs list `Client-Id` as a supported request header. Setting a short client name helps NASA track usage.

Example requests from the docs:

```bash
# Collections by short name and version
curl "https://cmr.earthdata.nasa.gov/search/collections?short_name=DEM_100M&version=1"

# Only cloud-hosted collections
curl "https://cmr.earthdata.nasa.gov/search/collections?cloud_hosted=true"

# Collections in a bounding box (west, south, east, north)
curl "https://cmr.earthdata.nasa.gov/search/collections?bounding_box[]=-10,-5,10,5"

# Granules of one collection in a time range
curl "https://cmr.earthdata.nasa.gov/search/granules?collection_concept_id=C1234567-PODAAC&temporal\[\]=2000-01-01T10:00:00Z,2010-03-10T12:00:00Z"
```

Applied to this project, a granule search for ECOSTRESS ESI over a farm could be `https://cmr.earthdata.nasa.gov/search/granules.json?short_name=ECO_L4T_ESI&bounding_box=-94,41,-93,42&temporal=2024-06-01T00:00:00Z,2024-08-31T23:59:59Z&page_size=100` (this exact URL is composed from the documented parameters and was not run).

## AppEEARS

AppEEARS (Application for Extracting and Exploring Analysis Ready Samples, https://appeears.earthdatacloud.nasa.gov) is run by LP DAAC. It extracts subsets from many products (MODIS, VIIRS, ECOSTRESS, HLS, SRTM, SMAP and others) for a list of points or for a polygon, and handles reprojection and quality layers. Point requests return CSV tables. Area requests return GeoTIFF or NetCDF-4 (EMIT data allow NetCDF-4 or ENVI). It suits this project well, because a farm is a small polygon and the tool needs a few layers over many dates.

### AppEEARS REST API

The API at `https://appeears.earthdatacloud.nasa.gov/api/` is "largely the same API that powers the AppEEARS user interface". It follows REST conventions with JSON requests and responses. Product listing needs no login. Tasks and downloads need a bearer token from the same Earthdata Login account.

Workflow from the docs:

1. `POST /login` with Earthdata Login username and password (HTTP basic auth). The response holds a token, its type ("Bearer") and an expiry time.
2. `GET /product` lists products. `GET /product/{product_id}` lists layers, for example `SRTMGL1_NC.003`. Use `limit` and `offset` to page.
3. `POST /task` submits a `point` or `area` request.
4. `GET /task` and `GET /task/{task_id}` check status.
5. `GET /bundle/{task_id}` lists output files once the task is done. Files then download from the bundle.

Example point task from the docs (MODIS daytime LST at one point for January 2010):

```python
import requests

token_response = requests.post(
    'https://appeears.earthdatacloud.nasa.gov/api/login',
    auth=('your-username', 'your-password')).json()
token = token_response['token']

task = {
    'task_type': 'point',
    'task_name': 'my-task',
    'params': {
        'dates': [{'startDate': '01-01-2010', 'endDate': '01-31-2010'}],
        'layers': [{'product': 'MOD11A1.061', 'layer': 'LST_Day_1km'}],
        'coordinates': [{'latitude': 42, 'longitude': -72}]
    }
}
response = requests.post(
    'https://appeears.earthdatacloud.nasa.gov/api/task',
    json=task,
    headers={'Authorization': 'Bearer {0}'.format(token)})
print(response.json())
```

Area tasks add a GeoJSON polygon in `params.geo` and an `output` block with `format.type` set to `geotiff` or `netcdf4` and a `projection` such as `native` or `geographic`. The date object also supports `recurring` with a `yearRange`, which suits growing-season windows repeated across years. Dates use the `MM-DD-YYYY` format in the examples.

AppEEARS tasks run asynchronously and can take minutes to hours (queue time not confirmed). The app should submit tasks ahead of time and cache results, not call AppEEARS during a user session.

## earthaccess (Python)

`earthaccess` is an open source Python library that handles Earthdata Login, CMR search and file access in one place. It works the same way on a laptop and in the cloud. Install with `pip install earthaccess` or from conda-forge.

The quick start shows three steps:

```python
import earthaccess

earthaccess.login()

results = earthaccess.search_data(
    short_name='ATL06',
    bounding_box=(-10, 20, 10, 50),
    temporal=("1999-02", "2019-03"),
    count=10
)

files = earthaccess.download(results, "./local_folder")
```

`earthaccess.open(results)` opens files in memory instead of downloading them. The API reference describes a call that "Returns temporary (1 hour) credentials for direct access to NASA S3 buckets" and an S3 file system "for direct access when running within the AWS us-west-2 region" (search snippet). Outside us-west-2, `earthaccess` falls back to HTTPS.

## NASA Worldview and GIBS

### Worldview

Worldview (https://worldview.earthdata.nasa.gov) is NASA's browser map for over 1,000 imagery layers from GIBS. It is the quickest way to look at a farm region on a given day, check for clouds, and find the exact GIBS layer name to reuse in the app.

### GIBS

The Global Imagery Browse Services (GIBS) serve pre-rendered imagery as map tiles. Earthdata states that most imagery is updated daily and that many products are available within 3 to 5 hours of observation. Some records span almost 30 years. GIBS supports OGC WMTS (REST and key-value), OGC WMS (1.1.1 and 1.3.0), Tiled WMS, generic XYZ tiles and GDAL access, in four projections: EPSG:4326, EPSG:3857, EPSG:3413 and EPSG:3031. No login is needed.

Endpoints use `best` (best available), `std` (science quality), `nrt` (near real time) or `all`.

WMTS REST pattern and example from the GIBS docs:

```
https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/{LayerIdentifier}/default/{Time}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}.{FormatExt}

https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2012-07-09/250m/6/13/36.jpg
```

XYZ form for web maps (Web Mercator), from the docs:

```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_Aerosol/default/2014-04-09/GoogleMapsCompatible_Level6/{level}/{row}/{col}.png
```

A Leaflet, MapLibre or OpenLayers map can use the XYZ pattern directly. The WMTS GetCapabilities document lists only the latest 100 time periods per layer. A `DescribeDomains` request returns all dates.

GIBS tiles are pictures, not data values. Use them for display and visual checks (for example, bare versus green fields on a true-colour image), not for calculations. GIBS asks users to acknowledge it: "We acknowledge the use of imagery provided by services from NASA's Global Imagery Browse Services (GIBS), part of NASA's Earth Science Data and Information System (ESDIS)."

## Giovanni

Giovanni (https://giovanni.gsfc.nasa.gov/giovanni/, version 4.40 at the time of fetch) is a GES DISC web tool for making maps, area-averaged time series, comparisons and animations from gridded data without downloading files. It covers many GES DISC holdings, including GPM IMERG, NLDAS, GLDAS and MERRA-2 (the variable list was not fetched). Its main use here is to check a signal fast, for example a 20-year NLDAS root-zone soil moisture series over a county, before writing code. Giovanni needs Earthdata Login for some outputs (not confirmed).

## Cloud-hosted access (NASA Earthdata Cloud)

Many NASA collections now live in Amazon Web Services (AWS) S3 in the us-west-2 (Oregon) region. Collection concept IDs ending in `-LPCLOUD`, `_CLOUD` or similar show cloud hosting, and the CMR parameter `cloud_hosted=true` filters for them.

There are two ways to read cloud data:

- HTTPS from anywhere. Links go through Earthdata Login and work from a laptop or any server. This is the normal route for a hackathon.
- Direct S3 from inside us-west-2. Code running on AWS compute in us-west-2 gets temporary S3 credentials (one hour, per the `earthaccess` docs) and reads `s3://` paths directly, which is faster and avoids egress. Tutorials from PO.DAAC, ORNL DAAC and NASA Openscapes state that direct S3 access works only in-region. Outside us-west-2, use HTTPS.

Cloud-friendly formats help in both cases:

- Cloud Optimized GeoTIFF (COG). HLS and ECOSTRESS V002 tiles are COGs, so a reader such as `rasterio` or GDAL can fetch only the pixels over one field with HTTP range requests.
- NetCDF-4 and HDF5. These can be read remotely with `xarray` and `h5netcdf`, though less efficiently than COGs.
- Zarr. Some NASA cloud datasets and the VEDA platform offer Zarr stores for fast chunked reads of long time series. Which of this project's datasets have Zarr versions was not confirmed in the pages fetched.

Example of a windowed COG read over HTTPS (pattern, not run; needs a `.netrc` for Earthdata Login and GDAL cookie settings):

```python
import rasterio
from rasterio.windows import from_bounds

url = "https://data.lpdaac.earthdatacloud.nasa.gov/.../ECOv002_L4T_ESI_..._ESI.tif"
with rasterio.open(url) as src:
    window = from_bounds(*field_bounds_in_src_crs, transform=src.transform)
    esi = src.read(1, window=window)
```

## How it maps to this challenge

- Backend pipeline. Use `earthaccess` or the CMR API to find granules for the farm polygon, AppEEARS for multi-year field subsets (ECOSTRESS, HLS, MODIS, SMAP, SRTM), and GES DISC or Giovanni for NLDAS, GLDAS and IMERG time series. Cache results per farm.
- Front end. Use GIBS XYZ tiles for a satellite basemap and date slider, so users can see bare fields, green-up and drought browning for themselves.
- Evidence and data gaps. Record the CMR concept ID, granule IDs and dates behind each number the tool shows, so each claim about heat stress, water stress or groundwater decline links back to NASA data.
- Operating constraints. The free tier of most hackathon hosting runs outside us-west-2, so plan for HTTPS access and small subsets, not direct S3.

## Sources

- https://earthaccess.readthedocs.io/en/latest/user/quick-start/
- https://earthaccess.readthedocs.io/en/stable/api/ (search snippet only, for temporary credentials and us-west-2)
- https://appeears.earthdatacloud.nasa.gov/api/
- https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html
- https://nasa-gibs.github.io/gibs-api-docs/access-basics/
- https://www.earthdata.nasa.gov/engage/open-data-services-software/earthdata-developer-portal/gibs-api
- https://giovanni.gsfc.nasa.gov/giovanni/ (landing page only)
- https://podaac.github.io/tutorials/external/earthdata_search.html and https://ornldaac.github.io/airborne/notebooks/aviris/aviris-c-bulk-download/ (search snippets only, for in-region S3 access)
- Failed (404): https://nasa.github.io/gibs/access-basics.html, https://www.earthdata.nasa.gov/learn/earthdata-cloud-primer, https://earthaccess.readthedocs.io/en/latest/user-reference/api/api/
