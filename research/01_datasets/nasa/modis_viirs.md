# MODIS and VIIRS land products

## What it measures

MODIS flies on the Terra and Aqua satellites. VIIRS flies on Suomi NPP (product prefix VNP) and NOAA-20 (prefix VJ1), with NOAA-21 (prefix VJ2) appearing in some collections. LP DAAC distributes the land products. The five products named for this tool are below, with their VIIRS continuity products.

| Product | What it gives |
| --- | --- |
| MOD13Q1 v6.1 | Terra 16-day vegetation indices: NDVI and EVI (Enhanced Vegetation Index), two quality layers, reflectance bands 1, 2, 3 and 7, and observation layers |
| MOD16A2 v6.1 | Terra 8-day evapotranspiration (ET), latent heat flux (LE), potential ET (PET) and potential LE (PLE), from a Penman-Monteith based algorithm using reanalysis weather and MODIS vegetation inputs |
| MOD16A2GF v6.1 | Gap-filled version of MOD16A2 (listed in the LP DAAC STAC catalog; its product page was not read) |
| MOD11A1 v6.1 | Terra daily land surface temperature (LST) and emissivity, day and night |
| MCD12Q1 v6.1 | Terra and Aqua combined yearly land cover, with five classification schemes (IGBP, UMD, LAI, BGC, plant functional types) plus property and QC layers |
| VNP13A1 v2 / VJ113A1 v2 | VIIRS 16-day NDVI, EVI and EVI2, designed to continue MOD13 |

ET and PET pixel values in MOD16A2 are the sum over the 8-day period. LE and PLE are the average. The last period of each year is 5 or 6 days.

## Spatial resolution

| Product | Pixel | Grid |
| --- | --- | --- |
| MOD13Q1 | 250 m | MODIS sinusoidal tiles |
| MOD16A2 | 500 m | MODIS sinusoidal tiles |
| MOD11A1 | 1 km | 1,200 x 1,200 km sinusoidal tiles |
| MCD12Q1 | 500 m | MODIS sinusoidal tiles |
| VNP13A1 / VJ113A1 | 500 m | VIIRS sinusoidal tiles |

Other related products in the same catalog include MOD13A1 (500 m), MOD13A2 (1 km), MOD15A2H (LAI/FPAR, 500 m), MOD17A2HGF (gap-filled GPP), and VIIRS LST VNP21A1D/N and VJ121A1D/N (1 km).

## Temporal resolution and revisit

- MOD13Q1, VNP13A1, VJ113A1: 16-day composites (best pixel in 16 days).
- MOD16A2: 8-day composites.
- MOD11A1: daily. Above 30 degrees latitude some pixels can have more than one clear observation per day.
- MCD12Q1: yearly.
- MODIS and VIIRS each view most of the Earth daily; composites exist to beat cloud.

## Record length

| Product | Start | End |
| --- | --- | --- |
| MOD13Q1 | 2000-02-18 | present |
| MOD11A1 | 2000-02-24 | present |
| MOD16A2 v6.1 | The LP DAAC page lists 2021-01-01 as the start. This looks narrower than expected for MODIS and is not confirmed. Use MOD16A2GF for a long record (its range was not checked) | present |
| MCD12Q1 | 2001-01-01 | present |
| VNP13A1 v1 | 2012-01-17 | 2024-06-08 (deprecated April 8, 2025) |
| VJ113A1 v2 | 2018-01-01 | present |
| VNP13A1 v2 | listed in the LP DAAC STAC catalog as `VNP13A1_002`; dates not checked | |

## MODIS end of mission

NASA posted a data alert (May 2, 2025) that the Terra and Aqua platforms will begin shutting down in late 2026 or early 2027. Both satellites are drifting from their designed orbits, which changes overpass times. MODIS data collection will stop and a final reprocessing will follow. NASA advises users to move to the equivalent VIIRS products. A tool built in 2026 should treat MODIS as a historical record (2000 onward) and VIIRS as the forward record.

## Latency

Latency for these standard LP DAAC products is not confirmed in the pages read. Composite products cannot be available until their 8-day or 16-day window closes.

## File formats

- MODIS products: HDF4 (HDF-EOS). MCD12Q1 is stated as HDF4.
- VIIRS v2 products: the format was not stated on the page read (VIIRS land products are usually HDF5; not confirmed).
- AppEEARS can return GeoTIFF or NetCDF subsets.

## Product IDs

| Short name | CMR concept ID | STAC collection (LPCLOUD) |
| --- | --- | --- |
| MOD13Q1.061 | C1748066515-LPCLOUD | MOD13Q1_061 |
| MOD16A2.061 | C2343113232-LPCLOUD | MOD16A2_061 |
| MOD16A2GF.061 | not checked | MOD16A2GF_061 |
| MOD11A1.061 | C1748058432-LPCLOUD | MOD11A1_061 |
| MCD12Q1.061 | C2484079608-LPCLOUD | MCD12Q1_061 |
| VJ113A1.002 | C2519122065-LPCLOUD | VJ113A1_002 |
| VNP13A1.002 | not checked | VNP13A1_002 |

## Access methods

- LP DAAC data pool and Earthdata Search. A free Earthdata Login account is required for downloads.
- AppEEARS API, which is the simplest way to pull a farm-sized time series. The AppEEARS API docs use MOD11A1 as their own example:

```python
import requests
token = requests.post(
    "https://appeears.earthdatacloud.nasa.gov/api/login",
    auth=("your-username", "your-password"),
).json()["token"]
task = {
    "task_type": "point",
    "task_name": "farm-lst",
    "params": {
        "dates": [{"startDate": "01-01-2010", "endDate": "01-31-2010"}],
        "layers": [{"product": "MOD11A1.061", "layer": "LST_Day_1km"}],
        "coordinates": [{"latitude": 42, "longitude": -72}],
    },
}
r = requests.post(
    "https://appeears.earthdatacloud.nasa.gov/api/task",
    json=task,
    headers={"Authorization": f"Bearer {token}"},
)
```

- CMR-STAC at https://cmr.earthdata.nasa.gov/stac/LPCLOUD for item search.
- `earthaccess.search_data(short_name="MOD13Q1", version="061", ...)`.
- NASA Worldview shows many MODIS and VIIRS layers through GIBS.
- The Earthdata Search page given in the brief (https://search.earthdata.nasa.gov/search?q=VIIRS) is a JavaScript application. It was not scraped for this note; the VIIRS facts come from LP DAAC pages and the CMR-STAC catalog instead.

## Known limitations

- Pixel size. A 250 m NDVI pixel covers about 6 hectares, and 500 m to 1 km pixels cover 25 to 100 hectares. Many fields are smaller, so pixels mix crops, roads and margins.
- Cloud. Daily LST has gaps on cloudy days. 16-day compositing reduces this but blurs short events such as a week of heat.
- MOD16 ET is modelled from reanalysis weather and MODIS vegetation inputs. The user guide lists known operational and uncertainty issues (section 3).
- MCD12Q1 is a supervised classification with known errors (user guide section 2.2). Its classes are broad (for example "croplands") and do not name crops. The "units" field is missing in its metadata.
- VNP13A1 v1 had aerosol errors that could affect indices over bright arid surfaces. V2 fixes this.
- MODIS will end in 2026 to 2027. Long time series must join MODIS with VIIRS, which differs in bands and resolution.

## How it maps to this challenge

- Bare-field periods and crop calendar. MOD13Q1 NDVI and EVI from 2000 give the longest consistent green-up and harvest record, useful for regional context and for larger fields.
- Heat stress. MOD11A1 daily daytime LST, and VIIRS VNP21/VJ121 LST, show runs of hot days during flowering.
- Frost risk. MOD11A1 nighttime LST can flag cold nights in spring and autumn (LST is skin temperature, not air temperature; compare with POWER T2M_MIN).
- Water stress. MOD16A2 ET and PET give an ET/PET ratio per 8 days, a simple water stress signal.
- Land cover context. MCD12Q1 shows whether surrounding land is cropland, grassland or forest, which helps the tool flag mixed pixels.
- Data gap to report. The tool should state the pixel size next to each MODIS value and prefer HLS for field-level questions.

## Sources

- https://lpdaac.usgs.gov/products/mod13q1v061/
- https://lpdaac.usgs.gov/products/mod16a2v061/
- https://lpdaac.usgs.gov/products/mod11a1v061/
- https://lpdaac.usgs.gov/products/mcd12q1v061/
- https://lpdaac.usgs.gov/products/vnp13a1v002/ (served the deprecated Version 1 description)
- https://lpdaac.usgs.gov/products/vj113a1v002/
- https://cmr.earthdata.nasa.gov/stac/LPCLOUD
- https://appeears.earthdatacloud.nasa.gov/api/
- https://www.earthdata.nasa.gov/data/alerts-outages/transition-from-modis-viirs
- https://earthaccess.readthedocs.io/en/latest/user/quick-start/
- Not scraped: https://search.earthdata.nasa.gov/search?q=VIIRS (JavaScript application)
