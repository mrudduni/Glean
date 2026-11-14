# Science methods: indices, models, and machine learning

This file describes the indices and models our tool may compute from NASA and partner data, with formulas, data sources, pitfalls, and a fit rating for a hackathon that may grow into a portfolio project. The final section gives a recommended stack.

Fit ratings use three levels. "Core" means build it during the hackathon. "Stretch" means add it if time allows. "Later" means save it for the portfolio phase.

## Vegetation and moisture indices

| Index | Formula | Sensor bands | Use in our tool | Fit |
| --- | --- | --- | --- | --- |
| NDVI | (NIR - Red) / (NIR + Red) | Landsat 8-9 B5, B4; MODIS B2, B1; HLS | Crop vigor, phenology, bare-soil detection | Core |
| EVI | 2.5 x (NIR - Red) / (NIR + 6 x Red - 7.5 x Blue + 1) | Landsat 8-9 B5, B4, B2 | Dense canopies where NDVI saturates | Stretch |
| NDMI (often called NDWI after Gao 1996) | (NIR - SWIR1) / (NIR + SWIR1) | Landsat 8-9 B5, B6 | Canopy water content, crop water stress | Core |
| NDWI (McFeeters 1996) | (Green - NIR) / (Green + NIR) | Landsat 8-9 B3, B5 | Open water and flooding, not crop moisture | Stretch |
| Bare soil index (BSI) | ((SWIR1 + Red) - (NIR + Blue)) / ((SWIR1 + Red) + (NIR + Blue)) | Landsat 8-9 B6, B4, B5, B2 | Bare-field periods, tillage, residue loss | Core |

USGS defines the Landsat NDVI, EVI, and NDMI formulas and their band numbers on its spectral index pages, and produces them at 30 m from Collection 2 surface reflectance. Two names cause confusion. "NDWI" can mean the Gao (1996) NIR-SWIR moisture index (same as NDMI) or the McFeeters (1996) green-NIR water index; the tool should label NDMI explicitly. BSI comes from forest-canopy-density work (Rikimaru and colleagues, 2002) and is widely reused; its exact original citation is not confirmed here.

Pitfalls. Clouds and cloud shadow bias all optical indices low, so use the Landsat QA band or HLS Fmask. Landsat revisits every 8 days with two satellites, and cloudy seasons leave gaps, so use MODIS (daily, 250 m) or HLS (Landsat plus Sentinel-2, 30 m, about 2 to 3 days) to fill time series.

## Evaporative Stress Index (ESI)

The ESI describes anomalies in the ratio of actual to reference ET. It is retrieved from land surface temperature and leaf area index with the ALEXI energy balance model (Anderson et al., 2016). A low ESI means the crop uses less water than conditions allow, which signals stress. In Brazil, ESI gave higher state-level yield correlations than TRMM rainfall or MODIS LAI anomalies for most crops, and its correlation with soybean yields peaked 10 to 25 days earlier.

Data. ECOSTRESS provides Level 4 ESI products based on ALEXI and on PT-JPL (70 m, irregular overpass times). OpenET provides 30 m actual ET that we can divide by reference ET ourselves.

Use in our tool. Show how often a field reached water stress in past seasons, by crop, to support the "drought risk" section of each rotation.

Fit. Stretch. ECOSTRESS revisit is irregular, so a simple version uses ET/ETo from OpenET or ECOSTRESS monthly composites.

## Soil moisture anomaly (z-score against climatology)

Formula. For each pixel and day of year d, z = (SM - mean_d) / sd_d, where mean_d and sd_d come from the same calendar window (for example a 31-day moving window) across all years. Crop-CASMA instead reports percent departure, (SM - SMm) / SMm x 100, using a 2015-to-present mean.

Data. SMAP L4 surface and root-zone soil moisture (9 km, 3-hourly, model-assimilated), SMAP L3 (36 km, plus a 9 km version), and the 1 km downscaled product in Crop-CASMA.

Pitfalls. SMAP starts in 2015, so the climatology is short, about 11 years by 2026. Report percentiles or z-scores with that caveat, or blend with longer records (for example ESA CCI soil moisture or NASA GLDAS) for the baseline. Mladenova et al. (2020) showed that assimilating SMAP into the USDA FAS Palmer model improved root-zone soil moisture for drought monitoring, which supports using SMAP L4 rather than raw L3 for root-zone questions.

Fit. Core. It is simple, uses the SMAP mission named in the challenge, and explains easily ("this spring was drier than 85 percent of springs since 2015").

## SPI and SPEI drought indices

SPI (McKee and others, 1993) fits a gamma distribution to precipitation totals over a window (1, 3, 6, 12 months) and transforms the cumulative probability to a standard normal value. SPI below -1 is moderate drought, below -1.5 severe, below -2 extreme. The WMO SPI User Guide (WMO-No. 1090, 2012) is the standard reference; it recommends long records, ideally 30 years or more.

SPEI (Vicente-Serrano, Beguería, López-Moreno, 2010) applies the same idea to climatic water balance, precipitation minus potential ET, usually with a log-logistic distribution. SPEI captures heat-driven drought that SPI misses.

Data. GPM IMERG precipitation (from 2000) or NASA POWER precipitation (from 1981) for P; FAO-56 ETo from NASA POWER weather for PET.

Libraries. climate_indices (BSD-3-Clause) and xclim (Apache-2.0) both compute SPI and SPEI on xarray data.

Fit. Core for SPI-3 and SPEI-3 at planting and flowering; they give a long-term drought frequency per field that SMAP alone cannot.

## Penman-Monteith reference ET (FAO-56)

FAO-56 Equation 6 gives daily grass reference ET:

ETo = [0.408 Δ (Rn - G) + γ (900 / (T + 273)) u2 (es - ea)] / [Δ + γ (1 + 0.34 u2)]

where Rn is net radiation (MJ/m2/day), G is soil heat flux (about 0 for daily steps), T is mean air temperature at 2 m (C), u2 is wind speed at 2 m (m/s), es - ea is vapor pressure deficit (kPa), Δ is the slope of the vapor pressure curve, and γ is the psychrometric constant.

Data. NASA POWER provides all inputs daily from 1981 at about 0.5 degree, including solar radiation, Tmax, Tmin, humidity, and 2 m wind.

Library. pyet (MIT) implements FAO-56 and about 20 other methods on pandas and xarray.

Crop ET. ETc = Kc x ETo with FAO-56 Kc values and stage lengths (see agronomy_rotations.md). Compare ETc sums per rotation to effective rainfall to give a water deficit for each strategy.

Fit. Core.

## Frost risk from Tmin

Method. From daily Tmin (NASA POWER or Daymet), find for each year the last spring date and first fall date at or below 32 F (0 C) and 28 F (-2.2 C). Fit an empirical or normal distribution across years and report the 10, 50, and 90 percent dates, matching the NOAA NCEI freeze table style. Also report freeze-free season length and its trend over recent decades.

Pitfalls. NASA POWER is a coarse grid and may miss cold-air pooling in valleys. Flag this as a local review item.

Fit. Core. It is simple, it directly supports crop choice and planting dates, and it shows climate shift.

## Heat stress degree days

Method. Count degree days above a crop threshold during sensitive stages, for example sum of max(0, T - 29 C) for corn and max(0, T - 30 C) for soybean (thresholds from Schlenker and Roberts, 2009). With only daily Tmax and Tmin, use a single-sine or double-sine interpolation to estimate hours above the threshold. Also compute GDD with the 86/50 F method for phenology.

Fit. Core for GDD and simple heat degree days; the sine method is a small extra.

## Phenology from NDVI time series

Goal. Find green-up, peak, senescence, and harvest dates for each field and season, which let us identify the crop, align Kc curves, and detect double crops or cover crops.

Methods.

| Method | How it works | Pros | Cons |
| --- | --- | --- | --- |
| TIMESAT (Jönsson and Eklundh, 2004) | Fits asymmetric Gaussian or double logistic functions, or Savitzky-Golay filtering, and extracts season start and end by thresholds | Long track record, many metrics | Original software is MATLAB and Fortran; licensing and Python ports vary |
| Harmonic (Fourier) regression | Fits NDVI = a0 + sum of a_k cos(2πkt/365) + b_k sin(2πkt/365), often 2 or 3 harmonics per year | Few lines of numpy, handles gaps, features feed directly to ML | Smooths sharp events like harvest |
| Double logistic per season | Fits a rise and fall curve to each season | Clear, physically meaningful dates | Needs season segmentation first |
| Whittaker or Savitzky-Golay smoothing plus thresholds | Smooth, then find dates where NDVI crosses a fraction of its amplitude | Simple and fast | Sensitive to thresholds and noise |

Fit. Core for harmonic fitting plus threshold dates; Stretch for double logistic. Harmonic coefficients also work as features for crop type classification.

## Detecting bare-field periods

Method. Classify each clear observation as bare when NDVI is below about 0.2 to 0.25 and BSI is above zero (thresholds need local tuning), then interpolate between clear observations and count bare days per year, especially from harvest to the next crop's green-up. A winter NDVI rise between cash crops signals a cover crop; Seifert et al. (2018) built a Landsat cover crop classifier with 91.5 percent accuracy using this kind of winter greenness signal.

Use. Bare months feed the RUSLE C factor, the soil cover principle, and the "living roots" metric for each rotation.

Pitfalls. Snow, standing residue, and dormant winter wheat confuse the signal. Use the snow flag and the crop history from CDL.

Fit. Core.

## Harmonizing multi-resolution data to a common grid

Our inputs range from 30 m (Landsat, HLS, OpenET) and 70 m (ECOSTRESS) to 250 m and 500 m (MODIS), 1 km and 9 km (SMAP), 0.1 degree (IMERG), about 0.5 degree (NASA POWER), and about 0.25 to 1 degree (GRACE mascons).

Approach. Pick a field-centric target. For each field polygon (from Crop Sequence Boundaries or a user upload), compute zonal statistics from fine data (mean NDVI, BSI) and area-weighted values from coarse data (the SMAP or IMERG cell that covers the field). Keep a per-variable "native resolution" note in the output so the explanation can say "soil moisture is a 9 km average, not a field measurement."

| Task | Library | Notes |
| --- | --- | --- |
| Labeled N-D arrays, time series | xarray | Base data model for everything |
| Reproject, clip, write GeoTIFF/COG | rioxarray | rio.reproject_match aligns one raster to another |
| Load cloud-hosted STAC items into xarray | odc-stac, stackstac | Lazy loading with dask |
| Conservative and bilinear regridding on curvilinear or global grids | xESMF | Conservative method keeps totals for rainfall and ET |
| Zonal statistics on polygons | rasterstats, exactextract, or xarray masks | Area-weighted means for coarse grids |
| Polygons and joins | geopandas | Field boundaries, SSURGO map units |

Rules. Use conservative regridding for fluxes and totals (rain, ET), bilinear for smooth state variables (temperature, soil moisture), and nearest or mode for categories (CDL crop type, soil map unit). Always regrid fine to coarse, not the reverse, unless a documented downscaling method is used.

Fit. Core. The field-centric approach keeps compute small enough for a hackathon.

## Machine learning approaches

### Gradient boosting and random forests

Uses. Classify crop type or detect cover crops from NDVI harmonics and bands; predict yield or a yield anomaly from weather, soil, and satellite features; predict next season's crop from crop history (Yaramasu et al., 2020; Abernethy et al., 2023).

Libraries. scikit-learn (BSD-3-Clause), XGBoost (Apache-2.0), LightGBM (MIT).

Why they fit. They train fast on tabular data, need little tuning, handle missing values (XGBoost and LightGBM), and work well with SHAP for explanations.

Fit. Core for one model, for example a yield-anomaly or water-stress model per crop.

### Time-series and sequence models

Uses. Markov chain or transition matrix models predict the next crop from history; Upcott et al. (2023) used transition probability matrices to predict rotations at national scale with 36 to 89 percent accuracy. Deep models such as ConvLSTM (Yaramasu et al., 2020) or temporal transformers capture spatial and temporal patterns. Geospatial foundation models (for example NASA and IBM Prithvi models trained on HLS) can be fine-tuned for crop mapping.

Fit. Core for a transition matrix built from CDL (it is short, clear, and explainable). Later for deep sequence models and foundation models.

### Reinforcement learning for rotation planning

Fenz et al. (2023) trained a DQN agent on crop successor suitability matrices, contribution margins, and N demand to generate rotations that experts judged realistic. CyclesGym (Turchetta et al., 2022) wraps the Cycles crop model as an RL environment for multi-year, multi-crop planning.

Fit. Later. RL needs a trusted simulator and careful reward design, and its outputs are hard to explain to farmers. For three to five candidate rotations, scoring each one directly is simpler and clearer.

### Multi-criteria decision analysis for farmer priorities

AHP (Saaty) asks the farmer to compare criteria in pairs (for example "profit is moderately more important than water use") and derives weights from the pairwise matrix, with a consistency ratio to catch contradictory answers. TOPSIS (Hwang and Yoon, 1981) ranks options by their distance to an ideal best and an ideal worst option on weighted, normalized criteria.

Proposed criteria for each rotation: expected net return, seasonal water deficit, erosion (relative RUSLE A), soil cover months, N fertilizer need, pest break score, drought and frost risk, and complexity or labor.

Libraries. pymcdm (MIT) implements TOPSIS, VIKOR, PROMETHEE, and weighting methods; pyDecision (GPL-3.0) covers AHP and many others; AHP is also about 20 lines of numpy.

Why it fits. It turns farmer priorities into explicit, adjustable weights. The UI can show sliders, and the ranking changes in front of the user, which judges and farmers both understand.

Fit. Core. Use simple weight sliders or a short AHP questionnaire plus TOPSIS ranking, and show a sensitivity check (does the top option change if any weight moves by 20 percent?).

### Uncertainty quantification

Options.

| Method | What it gives | Effort |
| --- | --- | --- |
| Weather-year ensemble | Run the water balance and yield proxy for each past year (for example 2001 to 2025) and report the spread per rotation | Low; very explainable |
| Quantile regression with LightGBM or XGBoost | 10th and 90th percentile predictions | Low |
| Conformal prediction (MAPIE, BSD-3-Clause) | Prediction intervals with coverage guarantees | Low to medium |
| Monte Carlo over uncertain inputs (N credit ranges, Kc ranges, prices) | Ranking stability across plausible inputs | Medium |
| Bayesian models | Full posterior | High |

Fit. Core for the weather-year ensemble and input Monte Carlo; Stretch for conformal intervals.

### Explainability with SHAP

SHAP (Lundberg and Lee, 2017; MIT license) attributes each prediction to its input features using Shapley values; TreeSHAP is fast for tree ensembles. For our tool, SHAP turns "the model says rotation B has lower drought risk" into "mainly because July soil moisture anomalies were negative in 6 of the last 10 years and sorghum's water need is 4 inches lower."

Fit. Core if we train any ML model. Rule-based scores should carry their own plain-language reason strings, which do the same job.

## Recommended stack for a hackathon that grows into a portfolio project

Hackathon build (48 hours), in order of value:

1. Field-centric data pull for one region: CDL or Crop Sequence Boundaries history, SSURGO soil properties, SRTM slope, NASA POWER daily weather, IMERG rainfall, SMAP L4 soil moisture, and Landsat or HLS NDVI, NDMI, and BSI.
2. Rule-based rotation scoring with transparent formulas: FAO-56 ETo and Kc water balance, RUSLE relative C factor from bare months, N credits, pest break rules, GDD, frost dates, and heat degree days.
3. Climatology context: SMAP z-scores, SPI-3 and SPEI-3, and frost-date trends.
4. TOPSIS ranking with farmer weight sliders, plus a weather-year ensemble to show spread.
5. Generated explanation cards for each rotation: reasoning, evidence with source links, benefits, information gaps (for example "soil moisture is a 9 km average"), and risks needing local review.

Why this order. Judges reward clear use of NASA data, working comparisons, and honest uncertainty. Rule-based scores and MCDA are fast to build, easy to explain, and hard to get badly wrong. Heavy crop models (DSSAT, APSIM) and deep learning take too long to set up and validate in 48 hours.

Portfolio phase additions:

1. A gradient boosting yield-anomaly model per crop, trained on county yields (NASS) with satellite and weather features, explained with SHAP and wrapped in conformal intervals.
2. AquaCrop-OSPy or PCSE/WOFOST runs for water-limited yield under each rotation, as a second line of evidence.
3. OpenET and ECOSTRESS ESI history per field where coverage exists.
4. GRACE groundwater trend as a regional water-sustainability flag for irrigated rotations.
5. A next-crop transition model from CDL history to detect the existing rotation automatically and flag rootworm variant risk.
6. Validation against published rotation effects (for example the 4 to 15 percent corn rotation benefit) and expert review with an Extension partner.

## Sources

- USGS Landsat spectral indices: https://www.usgs.gov/landsat-missions/landsat-surface-reflectance-derived-spectral-indices
- USGS Landsat EVI: https://www.usgs.gov/landsat-missions/landsat-enhanced-vegetation-index
- USGS Landsat NDMI: https://www.usgs.gov/landsat-missions/normalized-difference-moisture-index
- Gao (1996), NDWI: https://doi.org/10.1016/S0034-4257(96)00067-3
- McFeeters (1996), NDWI for open water: https://doi.org/10.1080/01431169608948714
- Anderson et al. (2016), ESI in Brazil: https://doi.org/10.1016/j.rse.2015.11.034
- ECOSTRESS product summary table: https://ecostress.jpl.nasa.gov/data/science-data-products-summary-table
- Crop-CASMA metadata and anomaly formula: https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_cropcasma.htm
- Mladenova et al. (2020), SMAP assimilation into the Palmer model: https://www.frontiersin.org/journals/big-data/articles/10.3389/fdata.2020.00010/full
- WMO SPI User Guide (WMO-No. 1090): https://library.wmo.int/records/item/39629-standardized-precipitation-index-user-guide
- Vicente-Serrano et al. (2010), SPEI: https://doi.org/10.1175/2009JCLI2909.1
- FAO-56 Chapter 2, Penman-Monteith equation: https://www.fao.org/4/x0490e/x0490e06.htm
- FAO-56 Chapter 6, crop coefficients: https://www.fao.org/4/x0490e/x0490e0b.htm
- NASA POWER: https://power.larc.nasa.gov/
- NC State Extension, freeze probability tables: https://content.ces.ncsu.edu/interpreting-freezefrost-probabilities-from-the-national-centers-for-environmental-information
- Schlenker and Roberts (2009): https://www.pnas.org/doi/10.1073/pnas.0906865106
- Purdue GDD method: https://www.agry.purdue.edu/ext/corn/news/timeless/heatunits.html
- Jönsson and Eklundh (2004), TIMESAT: https://doi.org/10.1016/j.cageo.2004.05.006
- Seifert, Azzari, Lobell (2018): https://iopscience.iop.org/article/10.1088/1748-9326/aac4c8/meta
- xESMF documentation: https://xesmf.readthedocs.io/
- rioxarray documentation: https://vylor.github.io/rioxarray/
- Yaramasu et al. (2020): https://doi.org/10.1016/j.compag.2020.105664
- Abernethy et al. (2023), preseason crop type prediction using crop sequence boundaries: https://doi.org/10.1016/j.compag.2023.107768
- Upcott et al. (2023): https://doi.org/10.1016/j.scitotenv.2022.160471
- Fenz et al. (2023), AI- and data-driven crop rotation planning: https://doi.org/10.1016/j.compag.2023.108160
- Turchetta et al. (2022), CyclesGym: https://proceedings.neurips.cc/paper_files/paper/2022/hash/4a22ceafe2dd6e0d32df1f7c0a69ab68-Abstract-Datasets_and_Benchmarks.html
- NASA IMPACT HLS foundation model examples: https://github.com/NASA-IMPACT/hls-foundation-os
- pymcdm: https://github.com/kotbaton/pymcdm
- pyDecision: https://github.com/Valdecy/pyDecision
- MAPIE: https://github.com/scikit-learn-contrib/MAPIE
- Lundberg and Lee (2017), SHAP: https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html
- climate_indices: https://github.com/monocongo/climate_indices
- xclim: https://github.com/Ouranosinc/xclim
