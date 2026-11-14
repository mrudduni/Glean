# Copernicus Sentinel-2

Sentinel-2 is the EU Copernicus optical land-imaging mission run by ESA. The Field Shift Resources tab lists it as a space agency partner (ESA) resource at https://dataspace.copernicus.eu.

## What it measures

Each satellite carries one instrument, the Multi-Spectral Instrument (MSI). It records reflected sunlight in 13 bands, from visible light through red-edge and near infrared to shortwave infrared. Level-2A (L2A) is the atmospherically corrected surface reflectance product. ESA treats L2A as analysis-ready data. L2A also includes an aerosol optical thickness map (AOT), a water vapour map (WVP) and a scene classification map (SCL), which flags clouds, cloud shadow, snow and water.

### Bands

| Band | Name | Resolution | Centre wavelength (µm) | Farm use |
|---|---|---|---|---|
| B01 | Coastal aerosol | 60 m | 0.443 | Atmosphere only |
| B02 | Blue | 10 m | 0.490 | True colour, EVI |
| B03 | Green | 10 m | 0.560 | True colour, NDWI |
| B04 | Red | 10 m | 0.665 | NDVI, EVI |
| B05 | Red edge 1 | 20 m | 0.704 | Chlorophyll, NDRE |
| B06 | Red edge 2 | 20 m | 0.740 | Canopy structure |
| B07 | Red edge 3 | 20 m | 0.783 | Canopy structure, LAI |
| B08 | NIR (wide) | 10 m | 0.842 | NDVI, biomass |
| B8A | Narrow NIR / red edge 4 | 20 m | 0.865 | NDRE, NDMI |
| B09 | Water vapour | 60 m | 0.945 | Atmosphere only |
| B11 | SWIR 1.6 | 20 m | 1.610 | Canopy and soil moisture (NDMI), crop residue, bare soil |
| B12 | SWIR 2.2 | 20 m | 2.190 | Residue, bare soil, burn |
| SCL | Scene classification | 20 m | n/a | Cloud and shadow masking |

B10 (cirrus) is in L1C but not in the L2A band list on Planetary Computer. Band data is from the Planetary Computer dataset page. The CDSE page confirms four 10 m bands, six 20 m bands and three 60 m bands.

## Resolution and revisit

- Spatial: 10 m (B02, B03, B04, B08), 20 m (red edge, B8A, SWIR), 60 m (B01, B09).
- Swath: 290 km. Tiles are about 110 x 110 km in UTM/WGS84 on the MGRS grid.
- Revisit: 10 days at the equator with one satellite, 5 days with two, and 2 to 3 days at mid-latitudes.
- Constellation: Sentinel-2B (2017) and Sentinel-2C (launched 5 September 2024, replaced 2A on 21 January 2025). Sentinel-2A ran an extension campaign from 13 March 2025, which CDSE described as lasting one year to 13 March 2026. Whether 2A still flies now is not confirmed.
- Orbit: sun-synchronous, 786 km mean altitude, 10:30 local crossing time.

## Record length

- L1C: global from 2015 (Sentinel-2A launch in 2015).
- L2A on AWS (Element 84 COGs): April 2017 over wider Europe, global since December 2018.
- L2A on Planetary Computer: temporal extent listed as 27 June 2015 to present, with the text saying the archive from 2016 was processed to L2A with Sen2Cor.
- CDSE is reprocessing the archive as "Collection-1" (processing baseline 5.0 or later for data up to 13 December 2023).

## Latency

The CDSE pages I read do not state an L2A delivery time, so it is not confirmed. The AWS registry says new scenes are usually added within a few hours of release by Copernicus.

## Formats

- CDSE native product: SAFE format (JPEG2000 bands), downloaded as a zip through OData.
- AWS (Element 84) and Planetary Computer: Cloud-Optimized GeoTIFF (COG), one file per band, with STAC metadata.

## Access

### Copernicus Data Space Ecosystem (CDSE)

STAC catalogue (STAC 1.1.0). The new endpoint is `https://stac.dataspace.copernicus.eu/v1/`. The legacy endpoint `https://catalogue.dataspace.copernicus.eu/stac` was set for deprecation from 17 November 2025.

```
# Collection info
https://stac.dataspace.copernicus.eu/v1/collections/sentinel-2-l2a
# Item search with a cloud filter (CQL2 text)
https://stac.dataspace.copernicus.eu/v1/collections/sentinel-2-l2a/items?filter-lang=cql2-text&filter=eo:cloud_cover<15
# Queryable fields
https://stac.dataspace.copernicus.eu/v1/collections/sentinel-2-l2a/queryables
```

A STAC browser is at https://browser.stac.dataspace.copernicus.eu.

OData catalogue (search needs no login):

```
https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq 'SENTINEL-2' and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 10.00) and OData.CSC.Intersects(area=geography'SRID=4326;POINT(lon lat)') and ContentDate/Start gt 2025-05-01T00:00:00.000Z&$top=10
```

This query is assembled from the filter pieces in the CDSE OData docs (product type S2MSI2A, cloud cover, point intersect, date).

Download needs a token. From the docs:

```bash
curl -d 'client_id=cdse-public' -d 'username=<LOGIN>' -d 'password=<PASSWORD>' \
  -d 'grant_type=password' \
  'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'

curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  'https://download.dataspace.copernicus.eu/odata/v1/Products(<product-id>)/$value' \
  --location-trusted --output product.zip
```

Access tokens last 10 minutes. A refresh token renews them within 60 minutes.

openEO (server-side processing, Python client), from the CDSE docs:

```python
import openeo
connection = openeo.connect("openeofed.dataspace.copernicus.eu")
connection.authenticate_oidc()          # browser login with CDSE account
cube = connection.load_collection(
    "SENTINEL2_L2A",
    spatial_extent={"west": 5.14, "south": 51.17, "east": 5.17, "north": 51.19},
    temporal_extent=["2021-02-01", "2021-04-30"],
    bands=["B02", "B04", "B08"],
    max_cloud_cover=85,
)
```

To avoid using partner back ends, use `https://openeo.dataspace.copernicus.eu/` instead of the federation endpoint.

Sentinel Hub APIs (Process API with "evalscripts") are also part of CDSE. They need an OAuth client created in the CDSE dashboard.

### Free-tier quotas for CDSE (Copernicus General Users)

| Service | Limit |
|---|---|
| S3, OData, STAC | 4 concurrent connections, 20 MB/s per connection, 12 TB per 30 days, 2000 requests per minute (S3) |
| Sentinel Hub APIs | 10,000 requests and 10,000 processing units per month, 300 per minute |
| openEO | 10,000 credits per month, 2 concurrent jobs |

### AWS Open Data (Element 84)

- Bucket: `s3://e84-earth-search-sentinel-data/` (no AWS account needed: `aws s3 ls --no-sign-request s3://e84-earth-search-sentinel-data/`).
- STAC API: Earth Search (docs at https://github.com/Element84/earth-search).

### Microsoft Planetary Computer

Collection `sentinel-2-l2a`, COGs in Azure West Europe. From the Planetary Computer quickstart:

```python
import pystac_client
import planetary_computer

catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)
items = catalog.search(collections=["sentinel-2-l2a"], intersects=aoi,
                       datetime="2025-05-01/2025-09-30").item_collection()
```

The search line is adapted from the quickstart's Landsat example. Assets sit in private Blob Storage, so URLs must be signed or the request returns 404.

### NASA link: Harmonized Landsat Sentinel-2 (HLS)

HLS is a NASA product (Goddard science team, run at Marshall IMPACT, archived at LP DAAC) that harmonizes Landsat 8/9 OLI and Sentinel-2A/B/C MSI.

| Item | HLSS30 (Sentinel-2 part) |
|---|---|
| Resolution | 30 m, MGRS tiles (same tiling as Sentinel-2) |
| Product | Nadir BRDF-adjusted reflectance (NBAR), 13 bands plus 4 angle bands and a QA (Fmask) band |
| Format | COG, one file per band |
| Temporal extent | 28 November 2015 to present |
| Combined revisit (L30 + S30) | 1.6 days in 2022 with four satellites, 1.4 days in 2025 with five |
| Latency | 2 to 3 days. NASA expects low-latency HLS in 2027 |
| Extras | HLS vegetation index products added February 2025 |
| DOI | https://doi.org/10.5067/HLS/HLSS30.002 |

HLS counts as NASA data, which matters for the "use at least one NASA data or resource" rule. Sentinel-2 itself is ESA data.

## Auth

- CDSE: free account required for download, openEO and Sentinel Hub. Registration needs an email address and acceptance of terms. Catalogue search (STAC, OData) works without login.
- AWS: no account needed for public reads.
- Planetary Computer: no account. The `planetary_computer` package signs URLs.
- HLS via LP DAAC: needs a NASA Earthdata login (not re-checked here).

## Licence

The Copernicus Sentinel data legal notice gives free, full and open access. When the data is changed, the user must add the notice "Contains modified Copernicus Sentinel data [Year]". This wording appears in the CDSE FAQ and the legal notice (search snippets). Planetary Computer lists "Copernicus Sentinel Data Terms". HLS is shared "without restriction" under NASA EOSDIS data use guidance. The Space Apps terms require every non-NASA dataset and its licence to be listed in the submission.

## Limitations

- Optical sensor, so clouds block it. Use SCL to mask clouds and expect gaps in monsoon and winter seasons.
- 20 m red-edge and SWIR bands are coarse for small plots under about 1 ha.
- Different processing baselines exist in the archive until Collection-1 reprocessing is complete. Time series should use harmonized values.
- CDSE free quotas and 10-minute tokens can slow bulk downloads during a 48-hour hackathon. Prefer COG reads from AWS or Planetary Computer, or server-side openEO.
- L2A latency is not confirmed.

## How it serves the rotation tool

- Field-scale crop history. NDVI and red-edge time series show when fields were green, which helps infer past crops and fallow periods for rotation history.
- Cover crop and residue checks. SWIR bands (B11, B12) separate bare soil from residue, which relates to soil cover goals.
- Crop stress and water. NDMI (B8A and B11) and red-edge indices flag water or nitrogen stress, which feeds the "conserve water" priority.
- Validation. Sentinel-2 at 10 m can check coarser layers such as GAEZ (9 km) or SMAP (9 to 36 km).
- Use HLS when the team needs a NASA-branded dataset with Sentinel-2 density, at the cost of 30 m pixels.

## Sources

- https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html
- https://documentation.dataspace.copernicus.eu/APIs/STAC.html
- https://documentation.dataspace.copernicus.eu/APIs/OData.html
- https://documentation.dataspace.copernicus.eu/APIs/openEO/openEO.html
- https://documentation.dataspace.copernicus.eu/APIs/openEO/Python_Client/Python.html
- https://documentation.dataspace.copernicus.eu/Registration.html
- https://documentation.dataspace.copernicus.eu/Quotas.html
- https://documentation.dataspace.copernicus.eu/FAQ.html (licence wording, search snippet)
- https://sentiwiki.copernicus.eu/web/s2-mission
- https://registry.opendata.aws/sentinel-2-l2a-cogs/
- https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a
- https://planetarycomputer.microsoft.com/docs/quickstarts/reading-stac/
- https://www.earthdata.nasa.gov/data/projects/hls
- https://lpdaac.usgs.gov/products/hlss30v002/
- https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice (PDF, read through search snippet only)
