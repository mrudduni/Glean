# Open-source code and libraries

This file lists open-source tools we can use to build the rotation tool. We checked each license in the repository's license file or the GitHub API, and took the latest version from PyPI on 13 November 2026. Star counts and last-commit dates come from the GitHub API on the same day and show rough maturity only.

Maturity uses three levels. "Mature" means a widely used project with years of releases. "Active" means a smaller but maintained project. "Early or slow" means a young project or one with little recent activity.

## Data access

| Library | What it does | License | Version | Maturity | GitHub |
| --- | --- | --- | --- | --- | --- |
| earthaccess | Searches NASA CMR and downloads or streams NASA Earthdata (SMAP, GPM IMERG, MODIS, ECOSTRESS, GRACE, HLS) with one Earthdata login, including direct S3 access in AWS us-west-2 | MIT | 0.19.0 | Active (651 stars, commits this week) | https://github.com/earthaccess-dev/earthaccess |
| pystac-client | Searches STAC APIs such as NASA CMR-STAC, Microsoft Planetary Computer, and Element 84 Earth Search | Apache-2.0 | 0.9.1 | Active (212 stars) | https://github.com/stac-utils/pystac-client |
| odc-stac | Loads STAC items into xarray Datasets with reprojection and dask chunking | Apache-2.0 | 0.5.3 | Active (207 stars) | https://github.com/opendatacube/odc-stac |
| stackstac | Turns a STAC item collection into a lazy dask-backed xarray DataArray | MIT | 0.5.1 | Early or slow (272 stars, last commit August 2024) | https://github.com/gjoseph92/stackstac |
| py-soildb | Python client for the USDA Soil Data Access (SDA) web service, for SSURGO soil properties | MIT | 0.8.0 | Early (first release 2025) | https://github.com/brownag/py-soildb |
| soilDB (R) | The NRCS-linked R package for SDA, SSURGO, and KSSL lab data; the reference for SDA queries | GPL-3.0 | n/a (R) | Mature (102 stars, active) | https://github.com/ncss-tech/soilDB |
| dataretrieval | Retrieves USGS water data (streamflow, groundwater levels, water quality) | Public domain in the U.S. (USGS) | 1.4.0 | Mature (270 stars) | https://github.com/DOI-USGS/dataretrieval-python |
| cdsapi | Client for the Copernicus Climate Data Store, for ERA5 reanalysis and ESA CCI soil moisture | Apache-2.0 | 0.7.7 | Mature (323 stars) | https://github.com/ecmwf/cdsapi |
| openeo | Python client for openEO back ends, which run cloud processing (for example Copernicus Data Space) with a standard API | Apache-2.0 | 0.54.0 | Active (219 stars) | https://github.com/Open-EO/openeo-python-client |

Notes.

- earthaccess needs a free NASA Earthdata account. Each team member should create their own; the tool should read credentials from a .netrc file or environment variables and never store them in code.
- NASA POWER has no official Python client, but its REST API returns JSON or CSV for a point or region with a plain HTTP request (https://power.larc.nasa.gov/).
- SSURGO is also available as gridded gSSURGO and gNATSGO rasters, which may be faster than SDA queries for many fields. The other dataset agent covers access details.
- Python SSURGO helpers are thin. py-soildb is new; for a hackathon, sending SQL to the SDA REST endpoint directly is a safe fallback.

## Array and vector processing

| Library | What it does | License | Version | Maturity | GitHub |
| --- | --- | --- | --- | --- | --- |
| xarray | Labeled N-dimensional arrays; the base data model for gridded time series | Apache-2.0 | current | Mature (4,226 stars) | https://github.com/pydata/xarray |
| rioxarray | Adds rasterio CRS, reprojection, clipping, and GeoTIFF or COG writing to xarray | Apache-2.0 | 0.24.0 | Mature (632 stars); the repository moved from corteva to vylor | https://github.com/vylor/rioxarray |
| xESMF | Regrids between rectilinear and curvilinear grids with bilinear, conservative, and nearest methods | MIT | 0.9.2 | Active (252 stars) | https://github.com/pangeo-data/xESMF |
| geopandas | Vector data (field boundaries, soil polygons) in pandas DataFrames, with spatial joins and overlays | BSD-3-Clause | current | Mature (5,297 stars) | https://github.com/geopandas/geopandas |

## Mapping and user interface

| Library | What it does | License | Version | Maturity | GitHub |
| --- | --- | --- | --- | --- | --- |
| leafmap | Interactive maps in Jupyter and web apps with many back ends; loads COGs, STAC, and vector data with little code | MIT | 0.64.7 | Mature (3,801 stars) | https://github.com/opengeos/leafmap |
| geemap | Interactive Google Earth Engine analysis and mapping in Python; useful if we use OpenET or Landsat through Earth Engine | MIT | 0.39.0 | Mature (4,071 stars) | https://github.com/gee-community/geemap |

geemap needs a Google Earth Engine account and a registered cloud project. If the team wants to avoid that, leafmap with STAC data covers most needs.

## Agronomy and climate calculations

| Library | What it does | License | Version | Maturity | GitHub |
| --- | --- | --- | --- | --- | --- |
| pyet | Reference and potential ET with FAO-56 Penman-Monteith and about 20 other methods, on pandas and xarray | MIT | 1.5.0 | Active (166 stars) | https://github.com/pyet-org/pyet |
| climate_indices | SPI, SPEI, PET, and Palmer indices on arrays and NetCDF | BSD-3-Clause | 3.2.0 | Mature (464 stars) | https://github.com/monocongo/climate_indices |
| xclim | Climate indicators on xarray, including GDD, frost days, heat waves, SPI, and SPEI, with unit checks | Apache-2.0 | 1.0.0 | Mature (Ouranos) | https://github.com/Ouranosinc/xclim |

## Crop models

| Library | What it does | License | Version | Maturity | GitHub |
| --- | --- | --- | --- | --- | --- |
| PCSE (WOFOST) | Python Crop Simulation Environment from Wageningen; runs WOFOST and LINGRA crop growth models with weather, soil, and agromanagement files, including rotations | EUPL 1.1 or later | 6.0.13 | Mature (296 stars, active) | https://github.com/ajwdewit/pcse |
| AquaCrop-OSPy | Python version of AquaCrop-OS for water-limited yield; fast to install and script | Apache-2.0 | 3.1.0 | Active (173 stars) | https://github.com/aquacropos/aquacrop |

FAO also publishes the official AquaCrop 7.3 code in Python (https://www.fao.org/aquacrop/en/). The team should check which version best matches FAO crop files before choosing.

## Machine learning, decision analysis, and explainability

| Library | What it does | License | Version | Maturity | GitHub |
| --- | --- | --- | --- | --- | --- |
| scikit-learn | Random forests, preprocessing, model selection | BSD-3-Clause | current | Mature (68,159 stars) | https://github.com/scikit-learn/scikit-learn |
| XGBoost | Gradient boosting with missing-value handling and quantile objectives | Apache-2.0 | 3.4.1 | Mature (28,970 stars) | https://github.com/dmlc/xgboost |
| LightGBM | Fast gradient boosting for large tabular data | MIT | 4.7.0 | Mature (18,975 stars) | https://github.com/lightgbm-org/LightGBM |
| SHAP | Shapley-value explanations; fast TreeSHAP for tree models | MIT | 0.54.1 | Mature (25,860 stars) | https://github.com/shap/shap |
| MAPIE | Conformal prediction intervals for scikit-learn models | BSD-3-Clause style | current | Active | https://github.com/scikit-learn-contrib/MAPIE |
| pymcdm | Multi-criteria decision methods (TOPSIS, VIKOR, PROMETHEE, and others) and weighting methods | MIT | 1.4.0 | Active | https://github.com/kotbaton/pymcdm |
| pyDecision | Large collection of MCDA methods, including AHP and fuzzy AHP | GPL-3.0 | current | Active | https://github.com/Valdecy/pyDecision |
| TorchGeo | PyTorch datasets, samplers, and pretrained models for geospatial deep learning | MIT | current | Mature (4,244 stars) | https://github.com/torchgeo/torchgeo |
| HLS foundation model examples | NASA IMPACT examples for fine-tuning the Prithvi HLS foundation model, including crop classification | Apache-2.0 | n/a | Active (409 stars) | https://github.com/NASA-IMPACT/hls-foundation-os |

License note. pyDecision is GPL-3.0, so code that links it and is distributed must also be GPL. For a permissive project, use pymcdm for TOPSIS and write AHP in numpy.

## Recommended minimum set for the hackathon

1. earthaccess and pystac-client with odc-stac for NASA and Landsat or HLS data.
2. xarray, rioxarray, and geopandas for processing, with xESMF only where conservative regridding matters (IMERG and ET).
3. pyet for FAO-56 ETo, and xclim or climate_indices for GDD, frost, SPI, and SPEI.
4. py-soildb or direct SDA SQL for SSURGO.
5. pymcdm for TOPSIS ranking.
6. leafmap for the map view.

Add LightGBM with SHAP and AquaCrop-OSPy in the portfolio phase.

## Sources

- GitHub REST API repository records (license, stars, last push), queried 13 November 2026: https://api.github.com/repos/{owner}/{repo}
- PyPI JSON API for versions, queried 13 November 2026: https://pypi.org/pypi/{package}/json
- License files read directly: rioxarray (https://github.com/vylor/rioxarray/blob/master/LICENSE), PCSE (https://github.com/ajwdewit/pcse/blob/master/LICENSE), pystac-client (https://github.com/stac-utils/pystac-client/blob/main/LICENSE), dataretrieval (https://github.com/DOI-USGS/dataretrieval-python/blob/main/LICENSE.md), MAPIE (https://github.com/scikit-learn-contrib/MAPIE/blob/master/LICENSE), pyDecision (https://github.com/Valdecy/pyDecision/blob/master/LICENSE), pymcdm (https://github.com/kotbaton/pymcdm/blob/master/LICENSE), xclim (https://github.com/Ouranosinc/xclim/blob/main/LICENSE), py-soildb (https://github.com/brownag/py-soildb/blob/main/LICENSE), earthaccess (https://github.com/earthaccess-dev/earthaccess/blob/main/LICENSE.txt)
- earthaccess documentation: https://earthaccess.readthedocs.io/
- pystac-client documentation: https://pystac-client.readthedocs.io/
- odc-stac documentation: https://odc-stac.readthedocs.io/
- stackstac documentation: https://stackstac.readthedocs.io/
- rioxarray documentation: https://vylor.github.io/rioxarray/
- xESMF documentation: https://xesmf.readthedocs.io/
- leafmap: https://leafmap.org/
- geemap: https://geemap.org/
- pyet documentation: https://pyet.readthedocs.io/
- PCSE documentation: https://pcse.readthedocs.io/
- AquaCrop-OSPy documentation: https://aquacropos.github.io/aquacrop/
- py-soildb documentation: https://py-soildb.readthedocs.io/
- dataretrieval documentation: https://doi-usgs.github.io/dataretrieval-python/
- Copernicus CDS API guide: https://cds.climate.copernicus.eu/how-to-api
- openEO Python client documentation: https://open-eo.github.io/openeo-python-client/
- NASA POWER: https://power.larc.nasa.gov/
- FAO AquaCrop: https://www.fao.org/aquacrop/en/
