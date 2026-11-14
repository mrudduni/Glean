# GEDI (Global Ecosystem Dynamics Investigation)

## What it measures

GEDI is a full-waveform lidar mounted on the International Space Station (ISS). It measures the 3D structure of vegetation and the ground beneath it: canopy height, canopy vertical profile, canopy cover, leaf and plant area, and ground elevation. The instrument has three lasers at 1064 nm that produce eight parallel ground tracks. Each laser fires 242 times per second. The University of Maryland leads the mission with NASA Goddard Space Flight Center. It was selected as an Earth Venture Instrument mission in 2014.

GEDI was built for forests, not crops. Its value for a farm tool lies in field edges, shelterbelts, woodlots, agroforestry and terrain, not in the crop canopy itself.

| Product | Short name | What it gives | DAAC |
| --- | --- | --- | --- |
| L2A elevation and height metrics, footprint, V002 | GEDI02_A | Ground elevation, canopy top height, relative height (RH) metrics | LP DAAC |
| L2B canopy cover and vertical profile metrics, footprint, V002 | GEDI02_B | Canopy cover, plant area index (PAI), plant area volume density (PAVD), foliage height diversity (FHD). 198 layers per beam | LP DAAC |
| L4A footprint aboveground biomass density, V2.1 | GEDI_L4A_AGB_Density_V2_1 (ORNL dataset 2056) | Aboveground biomass density (Mg/ha) and its prediction standard error per footprint | ORNL DAAC |
| L4B gridded aboveground biomass density, V2.1 | GEDI_L4B_Gridded_Biomass (name not confirmed on a product page) | Mean biomass and its uncertainty in 1 km cells | ORNL DAAC |

Other products exist (L1B waveforms, L3 gridded land surface metrics, L4C structural complexity, L4D imputed waveforms) but matter less here.

L4A biomass comes from models that relate L2A height metrics to field plot biomass, calibrated by world region and plant functional type. One of those types combines grasslands, shrubs and woodlands. There is no cropland type.

## Spatial resolution

Footprints are about 25 m across. The GEDI mission page and the L2B and L4A product pages give 25 m. The Earthdata instrument page gives about 30 m. Footprints are spaced about 60 m along track, and the eight tracks sit about 600 m apart, for a swath about 4.2 km wide. GEDI samples the ground. It does not map it wall to wall, so most fields will have no footprint or only a few.

L4B is gridded at 1 km. The L3 product is also gridded (the cell size is not confirmed in the pages fetched).

Coverage runs between 51.6 N and 51.6 S, the latitude band that the ISS orbit reaches. Product bounding boxes give slightly wider limits (54 N to 54 S for L2B, 55.8 N to 53 S for L4A).

## Temporal resolution and revisit

The product pages list temporal resolution as "Varies". Acquisition planning is done weekly. GEDI does not revisit a given field on a fixed schedule, and repeat footprints at the same spot are rare. Treat the data as a structural snapshot, not a time series.

## Record length

- Science data start in April 2019 (L2B from 2019-04-04, L4A from 2019-04-17, mission week 19 starts 2019-04-18).
- Acquisitions stopped from December 19, 2019, to January 8, 2020.
- The instrument was removed from the ISS and put into storage on March 17, 2023. No data exist from March 17, 2023, to April 24, 2024.
- GEDI was reinstalled and resumed operations on April 26, 2024.
- The L2B catalog entry lists data to July 10, 2025, and the L4A entry to July 9, 2025. Both show the data state as "COMPLETE". Whether acquisitions continued after July 2025 is not confirmed in the pages fetched.
- The L4B V2.1 file name example covers mission weeks 19 to 223 (April 18, 2019, to March 16, 2023).

## Latency

Not confirmed. Data go from the Mission Operations Center at Goddard to the Science Operations Center and then to the DAACs. GEDI suits historical analysis, not near real time.

## Formats

Footprint products (L1B, L2A, L2B, L4A) are HDF5, with one group per beam. Version 2 granules cover one quarter of an ISS orbit (about 2 GB each). Gridded products (L3, L4B, L4C gridded) are GeoTIFF.

## Product IDs and DOIs

| Short name | CMR concept ID | DOI |
| --- | --- | --- |
| GEDI02_B V002 | C2142776747-LPCLOUD | 10.5067/GEDI/GEDI02_B.002 |
| GEDI L4A V2.1 | C2237824918-ORNL_CLOUD | 10.3334/ORNLDAAC/2056 |

GEDI02_A V002 has DOI 10.5067/GEDI/GEDI02_A.002 following the same pattern (not confirmed on its product page).

## Access methods

- LP DAAC serves L1 and L2 products. The L2B page links a "GEDI Spatial Querying and Subsetting Quick Guide" and LP DAAC GitHub tutorials.
- ORNL DAAC serves L3 and L4 products.
- NASA Earthdata Search and the CMR API find granules by area and date. Each granule carries georeferenced metadata for spatial queries.
- AppEEARS offers point and area extraction for some GEDI products (not confirmed for each product in the pages fetched).
- The `earthaccess` Python library can search and stream the files:

```python
import earthaccess
earthaccess.login()
results = earthaccess.search_data(
    short_name="GEDI02_A",
    version="002",
    bounding_box=(-94.0, 41.0, -93.0, 42.0),
    temporal=("2022-06-01", "2022-09-30"),
)
```

Because granules are large, filter by bounding box first, then read only the beams and variables needed (for example `rh`, `elev_lowestmode`, `quality_flag`).

## Auth needed

A free NASA Earthdata Login account is required to download from LP DAAC and ORNL DAAC.

## Known limitations

- Sampling, not mapping. Many fields have no footprint, and repeat footprints are rare.
- Built for forests. RH metrics over short crops sit close to the measurement noise, and L4A has no cropland biomass model.
- The 2023 to 2024 storage gap and the 2019 to 2020 pause break the record.
- Data end in mid-2025 in the catalogs fetched.
- No data north of about 52 N.
- Users should filter with `l2a_quality_flag`, `l2b_quality_flag` and the `degrade_flag` field, and check `leaf_off_flag` for deciduous canopies.

## How it maps to this challenge

- Shelterbelts and field margins. Canopy height and cover near a field show tree windbreaks that cut wind erosion on bare fields and change local heat and moisture.
- Agroforestry options. If one rotation strategy includes trees or perennial strips, GEDI biomass and height for nearby woody land give a regional reference for carbon storage.
- Terrain. `elev_lowestmode` gives ground elevation under vegetation, which can check SRTM in tree-covered parts of a farm. See srtm.md.
- Data gap to report. GEDI cannot measure annual crop growth or crop condition. The tool should say so and use Landsat/HLS, MODIS and ECOSTRESS for crops.

## Sources

- https://gedi.umd.edu/data/products/ (redirects to https://gedi.umd.edu/dataproducts/products/)
- https://gedi.umd.edu/mission/mission-overview/
- https://www.earthdata.nasa.gov/data/instruments/gedi-lidar
- https://www.earthdata.nasa.gov/data/catalog/lpcloud-gedi02-b-002
- https://www.earthdata.nasa.gov/data/catalog/ornl-cloud-gedi-l4a-agb-density-v2-1-2056-2.1
- Failed: https://gedi.umd.edu/data with a content selector (page structure mismatch). Facts there were taken from the products page instead.
