# Landsat Collection 2 Level-2 and HLS (Harmonized Landsat Sentinel-2)

## What it measures

Landsat Collection 2 Level-2 products give surface reflectance (the fraction of sunlight the ground reflects, corrected for the atmosphere) and surface temperature (in kelvin) for each scene. Landsat 8 and 9 OLI reflectance comes from the LaSRC algorithm (version 1.5.0). Landsat 4, 5 and 7 reflectance comes from LEDAPS (version 3.4.0). Surface temperature for Landsat 4 to 9 uses the Landsat surface temperature algorithm (version 1.3.0). USGS certifies these products as CEOS Analysis Ready Data.

HLS is a NASA product that puts Landsat 8/9 OLI and Sentinel-2A/2B/2C MSI on one common 30 m grid so the two can be used as one time series. NASA applies atmospheric correction (LaSRC), cloud and shadow masking (Fmask), co-registration to the Sentinel-2 MGRS tiles, view-angle normalisation (Nadir BRDF-Adjusted Reflectance, NBAR) and spectral bandpass adjustment.

| HLS product | Source | Bands |
| --- | --- | --- |
| HLSL30 v2.0 | Landsat 8 and 9 OLI | 11 bands, 1 QA band (Fmask), 4 angle bands. Includes the two TIRS thermal bands as brightness temperature, not atmospherically corrected |
| HLSS30 v2.0 | Sentinel-2A, 2B, 2C MSI | 13 bands, 1 QA band, 4 angle bands |
| HLSL30_VI, HLSS30_VI v2.0 | Derived | Vegetation index products, introduced in February 2025 |

Version 2.0 added aerosol QA bits (high, medium, low, climatology) from LaSRC into the Fmask layer.

## Spatial resolution

- Landsat Collection 2 Level-2: 30 m for reflectance bands. The Landsat thermal bands are collected at 100 m (Landsat 8/9) per the HLS user guide band table.
- HLS: 30 m for all bands, on 109.8 km MGRS tiles in UTM projection. Sentinel-2 bands at 10 m and 20 m are resampled to 30 m.

## Temporal resolution and revisit

- One Landsat satellite repeats every 16 days. With Landsat 8 and 9 both in orbit the combined repeat is shorter (the exact figure is not confirmed in the pages fetched).
- Sentinel-2A/B/C repeat every five days according to the Earthdata HLS page.
- HLS combined revisit: the HLS user guide and LP DAAC pages say "every 1.6 days on average". The Earthdata HLS page says the revisit went from 1.6 days in 2022 with four satellites to 1.4 days in 2025 with five satellites.
- These are observation rates. Cloud cover reduces the number of usable images.

## Record length

- Landsat Collection 2 Level-1 data cover all sensors since 1972. Global Level-2 surface reflectance and surface temperature run from 1982 to the present.
- HLSL30: 2013-04-11 to present.
- HLSS30: 2015-11-28 to present.

## Latency

- Landsat Level-2 products usually appear within 24 hours after a scene reaches Tier 1 or Tier 2.
- Landsat 8 takes about 4 to 11 days to reach Tier 1 or Tier 2.
- Landsat 9 delivers Level-1 Tier 1 or Tier 2 scenes within 4 to 6 hours and Level-2 products within 3 days of acquisition.
- HLS latency is not confirmed in the pages read. The Earthdata HLS page says low-latency HLS products are expected in 2027. The ECOSTRESS FAQ notes that HLS is the slowest input to its ET products, which arrive in about 3 to 5 days.

## File formats

- Landsat Collection 2: Cloud Optimized GeoTIFF (COG), one file per band, with MTL (text) and XML metadata. Surface reflectance is unsigned 16-bit with scale factor 0.0000275 and offset -0.2, fill value 0, valid range 1 to 65455. Surface temperature is unsigned 16-bit with scale 0.00341802 and offset 149.0 (kelvin). Quality bands are QA_PIXEL, QA_RADSAT and SR_QA_AEROSOL.
- HLS: COG, one file per band. Example file name `HLS.S30.T60HTE.2022103T222539.v2.0.B01.tif`, which encodes product, MGRS tile, year and day of year, time, version and band. Scale factors are stored in file metadata (`REF_SCALE_FACTOR`, `ADD_OFFSET`); the numeric value was not checked.

## Product IDs

| Product | ID |
| --- | --- |
| Landsat 8-9 OLI/TIRS C2 L2 | DOI 10.5066/P9OGBGM6 |
| Landsat 7 ETM+ C2 L2 | DOI 10.5066/P9C7I13B |
| Landsat 4-5 TM C2 L2 | DOI 10.5066/P9IAXOVV |
| HLSL30 v2.0 | CMR concept C2021957657-LPCLOUD, STAC collection `HLSL30_2.0` |
| HLSS30 v2.0 | CMR concept C2021957295-LPCLOUD, STAC collection `HLSS30_2.0` |
| HLS VI | STAC collections `HLSL30_VI_2.0`, `HLSS30_VI_2.0` |

## Access methods

Landsat Collection 2:

- EarthExplorer (https://earthexplorer.usgs.gov/). Under Data Sets choose Landsat, then Landsat Collection 2 Level-2, then the sensor group. Downloads need a USGS login (not checked further, since the task excluded signing in).
- AWS: Level-1, Level-2, Level-3 and U.S. ARD data sit in the requester-pays bucket `s3://usgs-landsat` in us-west-2. Requester pays means the user's AWS account pays transfer costs.
- STAC: all Landsat data on AWS have STAC metadata, and USGS runs a Landsat STAC API that accepts GeoJSON areas of interest. The USGS STAC page URL tried for this note returned 404, so the API endpoint URL is not confirmed here.
- SNS topics announce new scenes, for example `arn:aws:sns:us-west-2:673253540267:public-c2-notify-v2` for Level-1 and Level-2 scenes.
- Landsat data have no use restrictions under the USGS open data policy (since 2008).

HLS:

- LP DAAC distributes HLS. A free Earthdata Login account is required.
- CMR-STAC for LP DAAC cloud data: https://cmr.earthdata.nasa.gov/stac/LPCLOUD, with item search at https://cmr.earthdata.nasa.gov/stac/LPCLOUD/search.
- Earthdata Search, AppEEARS (point and area extraction), and `earthaccess`.

Example STAC search for HLS (endpoint from the LPCLOUD catalog; parameters follow the STAC API item-search standard listed in its conformance classes):

```python
from pystac_client import Client
catalog = Client.open("https://cmr.earthdata.nasa.gov/stac/LPCLOUD")
search = catalog.search(
    collections=["HLSL30_2.0", "HLSS30_2.0"],
    bbox=[-93.8, 41.9, -93.6, 42.1],
    datetime="2024-03-01/2024-11-30",
)
items = list(search.items())
```

Reading the COG assets from these items needs an Earthdata Login token or S3 credentials (handled by `earthaccess.login()`).

## Known limitations

- Optical sensors cannot see through cloud. In humid growing seasons many dates are lost. The Fmask band flags cloud, shadow, snow and water, but masks can miss thin cloud.
- Landsat Level-2 needs a solar zenith angle below 76 degrees and complete auxiliary data. Surface temperature is not produced when auxiliary data are missing.
- HLS L30 thermal bands are brightness temperature, not land surface temperature.
- Spectral and BRDF harmonisation reduces but does not remove differences between Landsat and Sentinel-2.
- The pre-2013 Landsat record (Landsat 5 and 7) is not part of HLS, so long histories need Collection 2 Level-2 directly.

## How it maps to this challenge

- Bare-field periods. NDVI from HLS every few days shows when a field is bare, when a crop emerges and when it is harvested. Counting bare days per year for each past rotation is the most direct field-scale measure the tool can compute.
- Cover crop detection. Green-up in late autumn or early spring between cash crops indicates a cover crop.
- Crop history. A 30 m time series lets the tool infer what was grown in past years (with USDA Cropland Data Layer as a check where available).
- Erosion. Bare-soil timing combined with IMERG intense rain days and SRTM slope gives a simple erosion exposure score.
- Heat stress. Landsat surface temperature at 100 m (resampled to 30 m) can show hot spots within a farm on clear days.
- HLS is the right resolution for small fields where MODIS, SMAP and IMERG pixels are too coarse.

## Sources

- https://earthexplorer.usgs.gov/
- https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products
- https://www.usgs.gov/landsat-missions/landsat-collection-2
- https://www.usgs.gov/landsat-missions/landsat-commercial-cloud-data-access
- https://lpdaac.usgs.gov/products/hlsl30v002/
- https://lpdaac.usgs.gov/products/hlss30v002/
- https://lpdaac.usgs.gov/documents/1698/HLS_User_Guide_V2.pdf
- https://www.earthdata.nasa.gov/data/projects/hls
- https://cmr.earthdata.nasa.gov/stac/LPCLOUD
- https://ecostress.jpl.nasa.gov/downloads/faq/ECOSTRESS_FAQ_20240401.pdf
- Failed to load: https://www.usgs.gov/landsat-missions/landsat-stac-catalog (404)
