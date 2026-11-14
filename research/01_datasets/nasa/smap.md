# SMAP (Soil Moisture Active Passive)

## What it measures

SMAP is a NASA satellite launched on January 31, 2015. It carries an L-band radiometer and a radar that share one large mesh antenna. It maps surface soil moisture and the freeze or thaw state of the ground. Over ground that is not frozen or under water, it measures how much water sits in the top layer of soil, and it covers the globe every two to three days.

The radiometer signal comes mostly from the top 5 cm of soil. NSIDC user guides describe the surface soil moisture value as representing roughly the top 5 cm on average, in units of m3/m3. The mission also lists the radar products (L1B_S0_LoRes, L1C_S0_HiRes, L2_SM_A, L3_SM_A) in its product table. The radar stopped working in July 2015, so the long-running products rely on the radiometer (this date is not confirmed in the pages fetched for this note).

Three products matter most for this tool.

| Product | Short name | What it gives |
| --- | --- | --- |
| Enhanced L3 radiometer daily soil moisture, V6 | SPL3SMP_E | Daily composite of surface soil moisture (about 0 to 5 cm), retrieved from radiometer brightness temperatures interpolated to a 9 km grid |
| L4 surface and root zone soil moisture, geophysical data, V8 | SPL4SMGP | 3-hourly modelled surface and root-zone soil moisture. SMAP brightness temperatures are assimilated into the NASA Catchment land surface model (GEOS-5 system) |
| SMAP/Sentinel-1 L2 active-passive soil moisture, V3 | SPL2SMAP_S | Surface soil moisture at 3 km (validated) and 1 km (not validated), from SMAP L-band brightness temperature combined with Sentinel-1 C-band radar backscatter |

SPL4SMGP has two companion products. SPL4SMAU holds the data assimilation diagnostics, and SPL4SMLM holds the static land model constants (one file per version). The L4 version 8 notes say that precipitation outside North America and high latitudes now comes from IMERG V07, and that brightness temperature scaling now uses nine years of SMAP data (April 2015 to March 2024).

## Spatial resolution

| Product | Grid | Projection | Coverage |
| --- | --- | --- | --- |
| SPL3SMP_E | 9 km | EASE-Grid 2.0 Global (EPSG:6933) and Northern Hemisphere (EPSG:6931) | 85.044 S to 90 N |
| SPL4SMGP | 9 km | EASE-Grid 2.0 Global (EPSG:6933) | 85.044 S to 85.044 N |
| SPL2SMAP_S | 3 km (and 1 km, not validated) | EASE-Grid 2.0 Global (EPSG:6933) | 60 S to 60 N |

The standard L3 radiometer product (L3_SM_P) is on a 36 km grid. The radiometer footprints overlap considerably, so the 9 km enhanced grid is a posting interval and not the true footprint size.

## Temporal resolution and revisit

- SPL3SMP_E is a daily composite. It includes 6:00 a.m. descending and 6:00 p.m. ascending passes.
- SPL4SMGP gives 3-hourly time-averaged fields, with no gaps, because a model fills the time between overpasses.
- SPL2SMAP_S is organised as 30-second scenes. A scene exists only where a SMAP pass and a Sentinel-1 pass overlap. The file flags whether the two observations are within 36 hours of each other. The real revisit at a given farm depends on Sentinel-1 coverage and is not confirmed here. The platform list on the product page names Sentinel-1A and Sentinel-1B.
- The SMAP mission revisits most land every two to three days.

## Record length

All three products start on 31 March 2015 and run to the present.

## Latency

The SMAP mission product table on Earthdata lists these latencies. They are mission targets from the product table.

| Product level | Latency |
| --- | --- |
| L2 radiometer soil moisture (half orbit) | 24 hours |
| L3 radiometer soil moisture (daily composite) | 50 hours |
| L4_SM surface and root zone | 7 days |

NSIDC keeps a separate help article with actual latencies for each radiometer product. That article did not load (404), so actual latency for SPL3SMP_E, SPL4SMGP and SPL2SMAP_S is not confirmed.

## File formats

All three products are HDF5. NSIDC also offers reformatting through Harmony and AppEEARS (for selected SMAP products), which can return GeoTIFF or NetCDF.

## Product IDs and DOIs

| Short name | Version | DOI |
| --- | --- | --- |
| SPL3SMP_E | 6 | 10.5067/M20OXIZHY3RJ |
| SPL4SMGP | 8 | 10.5067/T5RUATAQREF8 |
| SPL4SMAU | 8 | 10.5067/02LGW4DGJYRX |
| SPL4SMLM | 8 | 10.5067/PXQIBL2ALDZD |
| SPL2SMAP_S | 3 | 10.5067/ASB0EQO2LYJV |

## Access methods

NSIDC DAAC distributes the products. A free NASA Earthdata Login account is required to download them.

The product pages list these routes:

- NSIDC Data Access Tool, which filters by date, area and file name and can export a Python download script.
- NASA Earthdata Search, with subsetting and reprojection for some products.
- HTTPS file system for direct download with a browser or `wget`.
- The `earthaccess` Python library.
- Harmony transformation services for spatial, temporal and variable subsetting, regridding and reformatting.
- Direct S3 access in the NASA Earthdata Cloud. This works only from the AWS us-west-2 region and needs temporary S3 credentials.
- AppEEARS point and area extraction, for selected NSIDC products.
- NASA Worldview and GIBS imagery for selected NSIDC products.

Example search with `earthaccess` (pattern from the earthaccess quick start, with the SMAP short name substituted):

```python
import earthaccess
earthaccess.login()  # reads .netrc or EARTHDATA_USERNAME / EARTHDATA_PASSWORD
results = earthaccess.search_data(
    short_name="SPL3SMP_E",
    bounding_box=(-94.0, 41.0, -93.0, 42.0),
    temporal=("2024-04-01", "2024-10-31"),
)
files = earthaccess.download(results, "./smap")
```

NASA POWER also serves SMAP L4 soil moisture through its API. The POWER methodology page lists SMAP L4 at about 0.09 degrees (about 9 km), daily UTC, from 31 March 2015 to near real time. The POWER AG daily parameter list includes SFMC (surface soil moisture), RZMC (root zone soil moisture, 0 to 100 cm) and RZMC_PRCNTL (root zone percentile). The POWER hydrology page says users get SMAP values through the high-resolution toggle in the Data Access Viewer or through SMAP-aliased parameters in the API. See nasa_power.md.

## Known limitations

- The radiometer senses only about the top 5 cm of soil. Crop water use depends on the root zone, which SMAP does not see directly. SPL4SMGP fills this gap with a model, so its root-zone values are model estimates constrained by surface observations.
- The pixel size (9 km for L3 and L4, 3 km for SPL2SMAP_S) is much larger than most fields. One pixel mixes many fields, roads, trees and water.
- The 1 km SPL2SMAP_S data are not validated, and NSIDC says to use them with caution.
- SPL2SMAP_S depends on Sentinel-1 overlap, so time series at one point have irregular gaps.
- The enhanced products do not contain the landcover_class fields that the standard L2 and L3 products carry.
- Retrievals are flagged or missing over frozen ground, snow, open water and dense vegetation. Users should read the retrieval quality flag and surface flag bits documented in the user guides.

## How it maps to this challenge

- Water stress. SPL4SMGP root-zone soil moisture shows whether the soil profile is drying during the growing season. A crop sequence that leaves a deep-rooted, water-hungry crop in a year with low spring root-zone moisture carries more risk.
- Bare-field periods. Daily SPL3SMP_E surface moisture can show how fast the top soil dries after rain when fields are bare, which links to wind erosion risk and to planting windows.
- Rainfall reliability. Soil moisture anomalies give a second view next to IMERG rainfall, showing whether rain actually stored water in the soil.
- Cover crop decisions. Comparing autumn and spring surface and root-zone moisture across years can show whether a cover crop is likely to deplete moisture needed by the next cash crop.
- Data gap to report. SMAP cannot tell one field from its neighbour, so the tool should present it as a regional water signal, not a field measurement.

## Sources

- https://www.earthdata.nasa.gov/data/platforms/space-based-platforms/smap
- https://nsidc.org/data/spl3smp_e/versions/6
- https://nsidc.org/data/spl4smgp/versions/8
- https://nsidc.org/data/spl2smap_s/versions/3
- https://nsidc.org/sites/default/files/documents/user-guide/spl3smp-v009-userguide.pdf (search snippet only, for the 5 cm statement)
- https://smap.jpl.nasa.gov/files/smap2/SMAP_handbook_web.pdf (search snippet only, for the 5 cm statement)
- https://power.larc.nasa.gov/docs/methodology/
- https://power.larc.nasa.gov/api/system/manager/parameters?community=AG&temporal=daily
- https://power.larc.nasa.gov/docs/methodology/data/sources_hydrology/ (search snippet only)
- https://earthaccess.readthedocs.io/en/latest/user/quick-start/
- Failed to load: https://nsidc.org/data/user-resources/help-center/smap-radiometer-data-latency (404)
