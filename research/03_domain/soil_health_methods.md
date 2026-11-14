# Soil health methods: soil organic carbon and erosion per rotation

This file reviews methods that estimate how a rotation changes soil organic carbon (SOC) and erosion. For each method it gives the formula, the coefficients with sources, the inputs we can get from open data, and whether a farmer could follow the calculation. The last section recommends what to compute in the hackathon and what to add later.

The rule we follow: a soil health number shown to a farmer must come from a published equation with published coefficients, and the tool must say whether the method predicts a direction (gaining or losing) or a size (tonnes per hectare).

## Summary table

| Method | Output | Predicts direction or size | Transparent to a farmer | Inputs we can supply | Fit |
| --- | --- | --- | --- | --- | --- |
| RUSLE with a rotation C factor | Average annual sheet and rill soil loss (t/ha/yr) | Size, as a long-term average | Yes, five factors multiplied | R from IMERG or published maps, K from SSURGO or SoilGrids texture, LS from SRTM, C from crop calendar and bare days, P from farmer | Core |
| STIR (Soil Tillage Intensity Rating) | Tillage disturbance per operation and per rotation year | Relative index | Yes, one product per pass | Farmer's tillage list; default implement values from NRCS | Core |
| SCI (Soil Conditioning Index) | Organic matter trend score | Direction only | Partly; the full model sits inside RUSLE2 | Biomass, STIR, erosion | Core, as an SCI-style score that we label clearly |
| ICBM two-pool model | SOC stock over time (t C/ha) | Size, with large uncertainty | Yes, two equations | Annual C inputs from yields (Bolinder et al., 2007), climate factor | Stretch |
| RothC 26.3 | SOC pools monthly (t C/ha) | Size | Moderate; five pools | Monthly temperature, rain, evaporation, clay, C inputs, plant cover | Portfolio |
| COMET-Farm (DayCent) and COMET-Planner | GHG and SOC change for US practices | Size | Low for DayCent; high for Planner lookups | US only | Reference and check, US sites only |

## RUSLE soil loss with a rotation C factor

Equation. A = R x K x LS x C x P. In imperial units A is tons per acre per year. Ontario's fact sheet gives the metric form A = 2.24 x R x K x LS x C x P in tonnes per hectare per year when R, K and LS are in the imperial-based units it tabulates.

Factors and sources.

- R, rainfall erosivity. Wischmeier and Smith (USDA Agriculture Handbook 537) define it from storm energy and 30-minute peak intensity (EI30). IMERG has 30-minute rain rates at 0.1 degree, so we can compute an EI30 climatology. IMERG smooths peak intensities, so its R will be biased low. Flag this as a data gap and compare with published R maps where they exist.
- K, soil erodibility. From SSURGO K factor columns (US) or from texture and organic matter. Ontario's table gives typical values, for example 0.38 for silt loam with average organic matter and 0.13 for sandy loam.
- LS, slope length and steepness. From SRTM slope with the Ontario equation LS = [0.065 + 0.0456 s + 0.006541 s^2] x (L / 22.1)^NN, with NN = 0.2, 0.3, 0.4 or 0.5 for slopes under 1, 1 to 3, 3 to 5 and 5 percent or more. SRTM at 30 m cannot see field-scale slope length well, so ask the farmer to confirm it.
- C, cover and management. Ontario gives a simple crop-type factor times a tillage factor. Crop factors: grain corn 0.40; silage corn, beans and canola 0.50; cereals 0.35; hay and pasture 0.02. Tillage factors: fall plow 1.0, spring plow 0.90, mulch tillage 0.60, ridge tillage 0.35, zone tillage 0.25, no-till 0.25. Ontario notes that this generalised C ignores rotation and rainfall timing.
- P, support practice. Up and down slope 1.0, cross slope 0.75, contour farming 0.50, contour strip cropping 0.25 (Ontario Table 6).

A rotation C factor we can compute. Handbook 537 computes C as soil loss ratios for each crop stage weighted by the share of annual erosivity that falls in that stage. We can do a transparent version:

C_rotation = sum over months m and years y of SLR(m, y) x EI_share(m), divided by the number of years,

where SLR comes from canopy and residue cover in that month (from the crop calendar, and from HLS NDVI and bare soil index for the observed history), and EI_share is the monthly share of annual erosivity from IMERG. This captures the main reason rotations differ: when the soil is bare relative to when intense rain falls. In Haryana that is the pre-monsoon and early monsoon window, when fields between wheat harvest (April) and rice transplanting (June to July) are bare.

Transparency. High. Each factor can sit on an evidence card. The farmer can see that switching from fall plough to no-till cuts C from 0.40 to 0.10 for corn in the Ontario example.

Limits. Sheet and rill erosion only; no gullies, wind or tillage erosion. Wind erosion matters in parts of Haryana with sandy soils. Mark it as not modelled.

## STIR, the Soil Tillage Intensity Rating

NRCS Agronomy Technical Note 50 (2006) defines STIR for one operation as the product of four weighted terms:

STIR = (0.5 x speed in mph) x (3.25 x tillage type) x (depth in inches) x (fraction of surface disturbed)

Tillage type values: 1.0 inversion with some mixing (moldboard plough), 0.8 mixing with some inversion (tandem disk, chisel, field cultivator), 0.7 mixing only (rotary tiller), 0.4 lifting and fracturing (subsoiler, injector), 0.15 compression. A rotation's STIR is the sum over all passes divided by the number of years. The note's three-year sorghum, wheat and cotton example sums to 302.55, or 100.85 per year. A tandem disk secondary pass rates 32.5. A runner-opener planter rates 2.6.

Büchi et al. (2026) give a metric form, STIR = (0.3107 x km/h) x (3.25 x type) x (0.3937 x cm) x surface fraction, and the R package SoilManageR implements it.

Transparency. Very high. Farmers know their passes. For Haryana, a typical conventional rice-wheat sequence includes puddling for rice and several harrow and cultivator passes for wheat, while happy seeder or zero-till wheat after rice cuts STIR sharply. Default implement speeds and depths for Indian equipment are not confirmed, so the tool should ask the farmer or use NRCS defaults with a warning.

## SCI, the Soil Conditioning Index

NRCS Soil Quality Agronomy Technical Note 16 (2003) defines SCI = OM + FO + ER, where OM is the organic material (biomass returned) subfactor, FO is the field operations subfactor and ER is the erosion subfactor. Purdue's SCI model service paper and the USDA Climate Hubs guide give the weighted form SCI = 0.4 x OM + 0.4 x FO + 0.2 x ER. Since 2006 the field operations part uses STIR.

Interpretation from the same NRCS note:

- A negative SCI predicts declining soil organic matter. A positive SCI predicts an increase.
- Values in 0 plus or minus 0.05 suggest organic matter stays near current levels.
- SCI predicts direction, not size or rate. An SCI of 0.4 is not "twice as good" as 0.2.
- Against long-term carbon experiments, SCI predicted the correct trend in about 90 percent of systems. Errors came from western sites with high manure or legume inputs.
- SCI may look better than reality when conventional tillage is paired with very low erosion or very high residue.

What we can compute. The exact OM and FO subfactor curves sit inside RUSLE2 databases. We did not find their equations in public documents, so we cannot reproduce official SCI values. We can compute an "SCI-style direction score" from the same three parts: relative biomass returned (from yields and harvest index), STIR, and RUSLE erosion. We must label it "SCI-style, not the NRCS SCI" and show only a direction with a confidence label.

## ICBM, the two-pool SOC model

Andrén and Kätterer (1997) define two pools, young Y and old O:

- dY/dt = i - k1 x r x Y
- dO/dt = h x k1 x r x Y - k2 x r x O

Coefficients from the original calibration: k1 = 0.8 per year, k2 = 0.006 per year (the paper suggests treating k2 as a global constant), humification coefficient h = 0.125 for crop residues and 0.31 for manure (0.47 for sewage sludge). The climate and soil factor r is 1.0 for the Uppsala reference site and must be scaled for other climates. The SoilR package documents the same defaults (k1 = 0.8, k2 = 0.00605, h = 0.13).

C inputs i per year come from yields with allometric ratios. Bolinder et al. (2007) give an approach from yield to above-ground residue, roots and root exudates for common crops.

Transparency. High. Two lines of maths and five parameters. The r factor for hot Haryana conditions is the weak point; using the Swedish value would understate decomposition. The tool should show a range of r values, not one.

Fit. Stretch for the hackathon, as a 20-year SOC projection band per rotation.

## RothC 26.3

RothC (Coleman and Jenkinson, 1996) splits SOC into decomposable plant material (DPM), resistant plant material (RPM), microbial biomass (BIO), humified organic matter (HUM) and inert organic matter (IOM). It runs monthly and modifies decay rates by temperature, topsoil moisture deficit and plant cover. Inputs are clay percent, depth, monthly temperature, rain, open-pan evaporation, plant C inputs, manure C, a plant cover flag and the DPM to RPM ratio.

Rothamsted publishes an official Python version, RothC_Py, under Apache-2.0. It was written for Python 3.9.7 and reads one input file. The model is usually spun up to equilibrium with average weather and inputs, then run for the period of interest.

Commonly used constants (decay rates per year of 10 for DPM, 0.3 for RPM, 0.66 for BIO, 0.02 for HUM, and a DPM to RPM ratio of 1.44 for most crops) come from the RothC description document. We have not re-read them in the description PDF, so they are not confirmed here. Read RothC_description.pdf in the repo before coding.

Fit. Portfolio. It needs monthly evaporation (we can use POWER-based ETo as a proxy, with a note) and more care than ICBM. Smith et al. (1997) compared nine SOC models against seven long-term experiments, and RothC was among the better performers, which supports it as the heavier SOC layer.

## COMET-Farm and COMET-Planner

COMET-Farm is a USDA and Colorado State University tool that implements the USDA entity-scale inventory methods (Eve et al., 2014), with DayCent for cropland soil carbon and N2O (Paustian et al., 2017). It needs field-by-field management history and runs on the COMET servers. COMET-Planner is the simpler sibling. It gives county-level emission reduction coefficients in tonnes CO2 equivalent per acre per year for NRCS practices, including Conservation Crop Rotation (CPS 328).

Use in our tool. For US demo fields, show the COMET-Planner coefficient for CPS 328 as an outside reference beside our own estimate. COMET is US only, so for Haryana the tool must say no equivalent public tool was found (not confirmed beyond our search).

## Evidence for direction of change

| Practice | Evidence | Use in the tool |
| --- | --- | --- |
| More diverse rotations | King and Blesh (2017) compiled 27 sites and 169 cropping systems and argue that perenniality, not species count, best predicts SOC gains | Give a SOC benefit to rotations that add perennials or long-season forages, not just more species |
| Cover crops | Poeplau and Don (2015) meta-analysis on cover crop SOC sequestration. The widely quoted rate of about 0.32 t C/ha/yr is not confirmed here because we did not read the abstract | Show as a range with the citation |
| Long-term rotation and fertility | Morrow Plots SOC trends over 100 years (Nafziger and others, 2011) | Validation target (see validation_plan.md) |
| Conservation agriculture in NW India | Jat et al. (2019) on basmati rice-wheat in North-West India; Jat et al. (2020) review for South Asia | Local evidence for Haryana scenarios; the detailed SOC values were not read here |

## What works for an Indian smallholder field

- RUSLE: R from IMERG, K from SoilGrids texture and organic C, LS from SRTM with farmer-confirmed slope length, C from the crop calendar. Most Karnal to Kaithal fields are nearly flat and bunded for rice, so water erosion will often be low. The tool should say so rather than inflate the erosion benefit of switching crops.
- STIR: works if the farmer lists passes. Indian implement defaults are a data gap.
- SOC: ICBM is the safest transparent option. Residue burning after rice removes most of the C input, so the tool should model "burn", "incorporate" and "retain as mulch" as separate choices.
- COMET does not apply.

## Recommendation

Hackathon core: RUSLE with a monthly rotation C factor, STIR, and an SCI-style direction score with a clear label. Each produces an evidence card with its formula and coefficients.

Stretch: an ICBM 20-year SOC band per rotation, with r varied across a plausible range.

Portfolio: RothC_Py for the SOC layer, validated against the Morrow Plots and NAPESHM data. COMET-Planner as a US cross-check.

## Sources

- NRCS Soil Quality Agronomy Technical Note 16, Interpreting the SCI (2003): https://nrcs.usda.gov/sites/default/files/2023-04/nrcs142p2_053273.pdf
- NRCS TN Agronomy No. 50, STIR (2006): https://mssoy.org/sites/default/files/documents/nrcs-tn-agron-no-50-four.pdf
- NRCS STIR fact sheet (2020): https://nrcs.usda.gov/sites/default/files/2023-01/Soil-Tillage-Intensity-Rating-Fact-Sheet3-27-2020.pdf
- Büchi et al. (2026), quantifying tillage intensity (metric STIR): https://bsssjournals.onlinelibrary.wiley.com/doi/pdf/10.1111/sum.70299
- SoilManageR STIR source: https://rdrr.io/cran/SoilManageR/src/R/STIR.R
- Carlson (2016), SCI model service (weighted SCI): https://docs.lib.purdue.edu/cgi/viewcontent.cgi?article=1111&context=agroenviron
- USDA Climate Hubs, Re-carbonizing row crop farms (SCI weights): https://climatehubs.oce.usda.gov/sites/default/files/Re-carbonizing%20Row%20Crop%20Farms.pdf
- Ontario OMAFA, Universal Soil Loss Equation fact sheet (2023): https://ontario.ca/page/universal-soil-loss-equation
- Wischmeier and Smith, Agriculture Handbook 537: https://ars.usda.gov/ARSUserFiles/60600505/RUSLE/AH_537%20Predicting%20Rainfall%20Soil%20Losses.pdf
- Andrén and Kätterer (1997), ICBM: https://doi.org/10.1890/1051-0761(1997)007[1226:iticbm]2.0.co;2
- ICBM author copy with parameter values: http://www.oandren.com/ICBM/1-35.pdf
- SoilR ICBMModel defaults: https://search.r-project.org/CRAN/refmans/SoilR/html/ICBMModel.html
- Bolinder et al. (2007), C inputs from yields: https://doi.org/10.1016/j.agee.2006.05.013
- Coleman and Jenkinson (1996), RothC-26.3: https://doi.org/10.1007/978-3-642-61094-3_17
- RothC_Py, Rothamsted (Apache-2.0): https://github.com/Rothamsted-Models/RothC_Py
- Smith et al. (1997), nine SOC models compared: https://doi.org/10.1016/s0016-7061(97)00087-6
- Paustian et al. (2017), COMET-Farm: https://doi.org/10.2134/agronmonogr59.c16
- USDA entity-scale inventory methods: https://usda.gov/about-usda/general-information/staff-offices/office-chief-economist/office-energy-and-environmental-policy/climate-change/greenhouse-gas-inventory-and-assessment-program/quantifying-greenhouse-gas-fluxes-methods-entity-scale-inventory
- COMET-Planner report: https://comet-planner.com/api/resource/pdf/COMET-Planner_Report.pdf
- King and Blesh (2017), perenniality and SOC: https://doi.org/10.1002/eap.1648
- Poeplau and Don (2015), cover crop SOC meta-analysis: https://doi.org/10.1016/j.agee.2014.10.024
- Nafziger and others (2011), Morrow Plots SOC: https://doi.org/10.2134/agronj2010.0213ser
- Jat et al. (2019), basmati rice-wheat CA in NW India: https://doi.org/10.1080/03650340.2019.1566708
- Jat et al. (2020), conservation agriculture in South Asia: https://doi.org/10.1038/s41893-020-0500-2
