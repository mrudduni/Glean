# ECOSTRESS (Ecosystem Spaceborne Thermal Radiometer Experiment on Space Station)

## What it measures

ECOSTRESS is a thermal infrared radiometer mounted on the International Space Station (ISS). It launched on June 29, 2018. It measures the skin temperature of the land surface and of plants, and the mission uses that temperature to estimate how much water plants use and when they become water stressed. Earthdata says the radiometer can resolve the temperature of an individual farmer's field. The instrument has five thermal bands between 8 and 12.5 micrometres, plus a 1.6 micrometre band for geolocation and cloud detection.

LP DAAC distributes four processing levels:

- Level 1 gives radiance, attitude and geolocation.
- Level 2 gives land surface temperature (LST) and emissivity, and a cloud mask.
- Level 3 gives evapotranspiration (ET).
- Level 4 gives the evaporative stress index (ESI) and water use efficiency (WUE).

Collection 2 (Version 002) is the current collection. Level 1 and 2 products have been in Collection 2 since October 5, 2022, and Level 3 and 4 products since January 18, 2024. Collection 2 brought a new radiometric calibration, a better cloud mask, better geolocation flags and new ET models. The team also publishes the ET model inputs (NDVI and albedo from a VIIRS and HLS fusion, and resampled reanalysis). Collection 1 ended for Level 3 and 4 products on December 31, 2022, and was discontinued for all products in 2025.

The products most useful for this tool:

| Product | Short name | What it gives |
| --- | --- | --- |
| Tiled LST and emissivity, L2, 70 m, V002 | ECO_L2T_LSTE | Instantaneous land surface temperature and emissivity |
| Tiled ET instantaneous and daytime, L3, 70 m, V002 | ECO_L3T_JET | Daily ET (ETdaily), PT-JPL-SM instantaneous ET with canopy, interception and soil partitions, plus STIC, MOD16 and BESS model estimates and an ET uncertainty layer |
| Tiled ESI PT-JPL instantaneous, L4, 70 m, V002 | ECO_L4T_ESI | ESI (ratio of actual ET to potential ET, 0 to 1) and PET |
| Tiled WUE, L4, 70 m, V002 | ECO_L4T_WUE (name follows the same pattern, not confirmed on a product page) | Water use efficiency |
| Tiled ancillary NDVI and albedo, L2, 70 m, V002 | ECO_L2T_STARS | The VIIRS and HLS fusion inputs to the ET models |

The L3 ET product uses PT-JPL-SM, a version of the Priestley-Taylor JPL model that adds soil moisture as a constraint. The ESI is computed from PT-JPL-SM actual and potential ET. A low ESI means the plants transpire much less than they would with ample water.

## Spatial resolution

All products are at 70 m. Tiled products (L2T, L3T, L4T) use a modified Military Grid Reference System (MGRS) grid of 109.8 km tiles in UTM projection, each 1568 by 1568 pixels. A 70 m pixel stays in the same place from one overpass to the next, which makes time series at a field simple. Gridded products (L2G, L3G, L4G) are resampled to a 0.0006 degree WGS84 grid. Level 1 and 2 swath products need the L1B geolocation product to place them on a map.

The mission text gives coverage between 52 N and 52 S. The product metadata bounding box reads 54 N to 54 S.

## Temporal resolution and revisit

Earthdata lists the temporal resolution as "daily; variable based on the instrument's orbital cycle aboard the ISS", and the product pages list it as "Varies". The ISS orbit is not sun-synchronous (51.6 degree inclination, about 415 km altitude), so the local time of each overpass drifts. A field can be seen in the morning one week and in the afternoon the next. This lets users study the daily cycle of plant stress, but it also means two images of the same field are not comparable without accounting for time of day. A regular repeat cycle at a given farm is not confirmed in the pages fetched.

## Record length

Products start on July 10, 2018, and run to the present. The record has gaps:

- September 29 to December 5, 2018, after the primary mass storage unit failed.
- March 14 to May 15, 2019, after the secondary unit failed.
- From May 15, 2019, to April 28, 2023, only thermal bands 2, 4 and 5 were downlinked. Since then 3-band and 5-band acquisitions are interleaved.
- February 17, 2020, had no acquisitions (safe hold).

## Latency

Latency is not confirmed in the pages fetched.

## Formats

Tiled products are Cloud Optimized GeoTIFF (COG), one file per layer, with a JSON metadata file. Swath and gridded products are HDF5. A file name such as `ECOv002_L4T_ESI_40665_017_51KVB_20250907T091510_0713_01_ESI.tif` encodes orbit, scene, MGRS tile, UTC acquisition time and layer.

## Product IDs and DOIs

| Short name | CMR concept ID | DOI |
| --- | --- | --- |
| ECO_L3T_JET | C2076106409-LPCLOUD | not confirmed |
| ECO_L4T_ESI | C2076104650-LPCLOUD | 10.5067/ECOSTRESS/ECO_L4T_ESI.002 |

The `LPCLOUD` suffix shows these collections sit in the NASA Earthdata Cloud.

## Access methods

LP DAAC distributes the data. The ECOSTRESS data page points to two routes: NASA Earthdata Search (search "ECOSTRESS") and AppEEARS, using its "point samples" or "area samples" requests. AppEEARS can return a field-sized subset as GeoTIFF or NetCDF and a CSV for point samples. LP DAAC also provides a swath-to-grid conversion script and tutorials in its GitHub repository.

Example search with `earthaccess` (pattern from the earthaccess quick start, with the ECOSTRESS short name substituted):

```python
import earthaccess
earthaccess.login()
results = earthaccess.search_data(
    short_name="ECO_L4T_ESI",
    version="002",
    bounding_box=(-94.0, 41.0, -93.0, 42.0),
    temporal=("2024-06-01", "2024-08-31"),
)
```

Because tiles are COGs in the Earthdata Cloud, users can read a small window over one field without downloading the full tile. See access_tooling.md.

## Auth needed

A free NASA Earthdata Login account is required for downloads, AppEEARS and direct cloud access.

## Known limitations

- Overpass times vary with the ISS orbit, so LST and ET from different dates mix different times of day.
- Clouds block thermal sensing. Each product carries a cloud mask.
- Revisit at a single field is irregular, and the 2018 to 2019 storage failures left gaps.
- ISS solar arrays obstruct some scenes. The `FieldOfViewObstruction` metadata field is reliable only from October 24, 2024 (orbit 35724).
- ISS pointing is coarse. The team recommends using only scenes with geolocation quality "best" or "good" when field-level location matters.
- L3 and L4 products can show 500 m to 1 km artifacts when the HLS input is old and VIIRS dominates the NDVI and albedo fusion.
- ET products from January 1 to September 30, 2023, are lower quality and due for reprocessing. Data from May 15 to July 1, 2025, were noisier than normal.
- Coverage stops near 52 to 54 degrees latitude, so northern farms (for example much of Canada and northern Europe) are not covered.

## How it maps to this challenge

- Heat stress. LST at 70 m shows which fields run hotter than neighbours on the same afternoon pass. A rotation that puts a heat-sensitive crop on a hot field can be flagged.
- Water stress. ESI below 1 shows crops using less water than the atmosphere demands. Season-long ESI for past years helps judge whether a water-hungry crop such as maize is risky on a given field.
- Crop water use. Daily ET from ECO_L3T_JET can be summed over a season and compared between crops grown on the same field in past years, which gives evidence for the water cost of each rotation option.
- Bare fields. Bare soil appears hot with low canopy transpiration in the PT-JPL-SM partitions, which can help confirm fallow or post-harvest periods.
- Data gap to report. Irregular overpass times and cloud gaps mean the tool should show the number of clear scenes behind each estimate.

## Sources

- https://ecostress.jpl.nasa.gov/data
- https://www.earthdata.nasa.gov/data/instruments/ecostress
- https://www.earthdata.nasa.gov/data/catalog/lpcloud-eco-l3t-jet-002
- https://www.earthdata.nasa.gov/data/catalog/lpcloud-eco-l4t-esi-002
- https://earthaccess.readthedocs.io/en/latest/user/quick-start/ (pattern reused from smap.md)
- Not fetched: the ECO_L4T_WUE and ECO_L2T_LSTE catalog pages, so the WUE short name and per-product latency are not confirmed.
