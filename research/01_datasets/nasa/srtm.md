# SRTM (Shuttle Radar Topography Mission) and NASADEM

## What it measures

SRTM flew on Space Shuttle Endeavour (mission STS-99) from February 11 to 22, 2000. It used C-band and X-band radar interferometry, with one antenna in the payload bay and another on a 200-foot mast, to map land elevation. The C-band data produced a near-global digital elevation model (DEM). SRTM covered all land between 60 N and 56 S, about 80% of Earth's land.

Two products matter here.

| Product | Description |
| --- | --- |
| SRTMGL1 v003 | NASA SRTM global 1 arc second (about 30 m) DEM. Version 3 fills voids with ASTER GDEM2, GMTED2010 or the U.S. National Elevation Dataset |
| NASADEM_HGT v001 | A reprocessing of the original SRTM telemetry, using ASTER GDEM2 and ICESat GLAS ground control points for better height and geolocation accuracy. Layers are DEM, number of scenes (NUM, which also gives the data source) and an updated SRTM water body mask |

SRTMGL3 (3 arc second, about 90 m) also exists in the LP DAAC catalog.

## Spatial resolution

1 arc second, listed by LP DAAC as 30 m x 30 m for both SRTMGL1 and NASADEM. Tiles are 1 x 1 degree.

## Temporal resolution and revisit

A single snapshot. The data were collected over 11 days in February 2000. There is no revisit.

## Record length

2000-02-11 to 2000-02-21 (one epoch). Both products have the LP DAAC data state "COMPLETE".

## Latency

Not applicable. The products are static.

## File formats

- SRTMGL1: `.hgt` raster tiles named for the lower-left corner, for example `N37W105.SRTMGL1.HGT` (LP DAAC also shows `N26W077.hgt`). Also available as NetCDF4 (`SRTMGL1_NC`) with a per-pixel source layer (`SRTMGL1_NUMNC`).
- NASADEM: `.hgt` tiles, for example `s01w047.hgt`. Also NetCDF4 as `NASADEM_NC`, with source in `NASADEM_NUMNC`.

## Product IDs

| Short name | CMR concept ID | STAC collection (LPCLOUD) |
| --- | --- | --- |
| SRTMGL1.003 | C2763266360-LPCLOUD | SRTMGL1_003 |
| SRTMGL3.003 | not checked | SRTMGL3_003 |
| NASADEM_HGT.001 | C2763264762-LPCLOUD | NASADEM_HGT_001 |

## Access methods

- LP DAAC and Earthdata Search. Downloads need a free Earthdata Login account.
- CMR-STAC: https://cmr.earthdata.nasa.gov/stac/LPCLOUD lists both collections.
- AppEEARS: the AppEEARS API docs use `SRTMGL1_NC.003` as their product example, so a farm polygon can be clipped and returned as GeoTIFF:

```
curl "https://appeears.earthdatacloud.nasa.gov/api/product/SRTMGL1_NC.003?pretty=true"
```

- `earthaccess`:

```python
import earthaccess
earthaccess.login()
tiles = earthaccess.search_data(short_name="NASADEM_HGT", bounding_box=(-94.0, 41.0, -93.0, 42.0))
earthaccess.download(tiles, "./dem")
```

## How to derive slope

The GDAL `gdaldem` tool computes slope from any GDAL-readable DEM.

```
gdaldem slope dem.tif slope_deg.tif -compute_edges
gdaldem slope dem.tif slope_pct.tif -p -compute_edges
gdaldem aspect dem.tif aspect.tif
```

Notes from the GDAL documentation:

- The output is a 32-bit float raster in degrees, or in percent with `-p`. Nodata is -9999.
- Horizontal and vertical units must match. SRTM and NASADEM tiles are in geographic coordinates (degrees) with heights in metres. The docs suggest `-s 111120` for latitude/longitude grids with heights in metres near the equator, and recommend reprojecting with `gdalwarp` to a metric projection (for example the local UTM zone) for places away from the equator.
- `-alg Horn` (default) suits rougher terrain, and `-alg ZevenbergenThorne` suits smoother landscapes, according to the GDAL docs.

A reprojection step for a mid-latitude farm:

```
gdalwarp -t_srs EPSG:32615 -tr 30 30 -r bilinear NASADEM_tile.hgt dem_utm.tif
gdaldem slope dem_utm.tif slope_deg.tif -compute_edges
```

(EPSG:32615 is UTM zone 15N, chosen only as an example.)

## Known limitations

- SRTM measures the radar reflective surface. Over trees and buildings it sits above bare ground, so it is a surface model, not a true bare-earth model.
- The data are from 2000. Land levelling, terracing or new drainage since then are not shown.
- Voids in steep terrain and water areas were filled from other sources (ASTER GDEM2, GMTED2010, NED). The NUM layer tells which source each pixel came from.
- 30 m is coarse for small terraces, grassed waterways or field edges. Slope from a 30 m DEM is smoothed and tends to understate the steepest short slopes.
- No coverage north of 60 N or south of 56 S.
- LP DAAC points to a DEM comparison guide for choosing between DEMs; it was not read here.

## How it maps to this challenge

- Erosion. Slope (and slope length, if the team computes it) is the main terrain input to water erosion risk. Combined with HLS bare-field periods and IMERG intense rain days, it lets the tool rank rotations by how much bare soil sits on steep ground during heavy rain months.
- Frost risk. Low spots and valley floors collect cold air. Elevation and topographic position from the DEM can flag fields more prone to frost pockets than POWER's coarse grid suggests.
- Water. Aspect and position on the slope affect drying and drainage, useful when the tool explains differences between fields on one farm.
- It is static, so the tool can compute it once per farm.

## Sources

- https://www.earthdata.nasa.gov/data/instruments/srtm
- https://lpdaac.usgs.gov/products/srtmgl1v003/
- https://lpdaac.usgs.gov/products/nasadem_hgtv001/
- https://cmr.earthdata.nasa.gov/stac/LPCLOUD
- https://appeears.earthdatacloud.nasa.gov/api/
- https://gdal.org/en/stable/programs/gdaldem.html
- https://earthaccess.readthedocs.io/en/latest/user/quick-start/
