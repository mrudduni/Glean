# Validation plan

Judges score Validity as "scientifically sound and technically feasible". This file sets out how we show that the tool's numbers hold up. It lists the public datasets, the exact metrics, three experiments that fit inside the hackathon, and three for the long-term project. Every experiment runs at one US site and one Indian site, so the claims hold for an Indian smallholder field as well as a Corn Belt field.

## What we can and cannot validate

The tool makes three kinds of claim, and each needs a different test.

1. Input claims. "Your field got 410 mm of rain last monsoon." "Root-zone soil moisture was in the 12th percentile in May." These can be checked against ground stations.
2. Process claims. "Rotation B needs about 300 mm less irrigation than rice-wheat." "Rotation C has a lower erosion factor." These can be checked against independent satellite ET and against field trials.
3. Outcome claims. "Diverse rotations tend to lose less yield in drought years." These can only be checked against long-term trials and yield statistics, and only as tendencies.

We cannot validate a recommendation for a specific farmer's future. The tool should say so, and the validation page should say which claim type each check covers.

## Study sites

| Site | Why | Ground truth nearby |
| --- | --- | --- |
| Marsden Farm, Boone County, Iowa | Published 2-, 3- and 4-year rotation trial from 2003 to 2011 (Davis et al., 2012) | CoCoRaHS gauges; SCAN and USCRN soil moisture stations in Iowa (exact nearest station not confirmed); NASS county yields; Crop Sequence Boundaries |
| Morrow Plots, Urbana, Illinois | Rotation and fertility plots since 1876, with a public FAIR dataset for 1888 to 2021 (Caldrone et al., 2024) | Long yield and SOC record (Nafziger and others, 2011) |
| Karnal to Kaithal belt, Haryana | Team's chosen region; rice-wheat with groundwater decline | IMD 0.25 degree gridded rain (Pai et al., 2014); ICRISAT district yields; conservation agriculture trials near Karnal (Jat et al., 2019; Sidhu et al., 2019) |

## Public datasets and access

| Dataset | What it gives | Access |
| --- | --- | --- |
| CoCoRaHS | Daily volunteer gauge rain, CC BY 4.0 (see research/01_datasets/usda_us/cocorahs.md) | https://www.cocorahs.org |
| IMD gridded rainfall | Daily rain at 0.25 degree from 1901 (Pai et al., 2014) | IMD Pune data portal; exact download URL not confirmed |
| SCAN | NRCS soil moisture and climate stations (Schaefer et al., 2007) | https://www.nrcs.usda.gov/resources/data-and-reports/soil-climate-analysis-network (timed out in our check, not confirmed) |
| USCRN | NOAA reference stations with triple-redundant soil moisture probes (Bell et al., 2013) | https://www.ncei.noaa.gov/access/crn/ |
| ISMN | Harmonised in situ soil moisture, 71 networks and 2,842 stations as of July 2021 (Dorigo et al., 2021). Python reader `ismn` | https://ismn.earth. India has one listed network, IIT_KANPUR, with 1 station |
| OpenET | 30 m field ET for the US (Melton et al., 2021) | See research/01_datasets/usda_us/openet.md |
| ECOSTRESS L3 ET and L4 ESI | 70 m ET and stress, global, irregular overpasses | AppEEARS; see research/01_datasets/nasa/ecostress.md |
| NASS Quick Stats | County yields | Free key; see research/01_datasets/usda_us/nass_quickstats.md |
| ICRISAT District Level Database | District crop area, production and yield for India, 1966 onward; the TCI-ICRISAT version covers 571 districts in 20 states to 2017 | http://data.icrisat.org/dld |
| Crop Sequence Boundaries | US field polygons with 8-year crop sequences | https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php |
| Morrow Plots dataset | Yields and management 1888 to 2021 | https://doi.org/10.1038/s41597-024-03984-9 |
| DRIVES, NAPESHM, SoilHealthDB | Rotation trial yields and soil health measurements | Ag Data Commons; see research/01_datasets/usda_us/ag_data_commons.md |
| KBS LTER Main Cropping System Experiment | Long-term rotation, tillage and cover crop treatments (Robertson et al., 2014) | https://lter.kbs.msu.edu/datatables |

## Metrics

| Claim | Metric | Target or reference |
| --- | --- | --- |
| Daily rain amount | Pearson r, bias in percent of monthly totals | Report as is; no fixed target |
| Rain detection | Probability of detection (POD), false alarm ratio (FAR), critical success index (CSI) for days at or above 1 mm and 25 mm | Report as is |
| Soil moisture | Unbiased RMSE (ubRMSE), bias, R, anomaly R | SMAP requirement is ubRMSE at or below 0.04 m3/m3 (Colliander et al., 2017 for L2; the GMAO L4 assessment uses the same criterion) |
| Seasonal ET and irrigation demand | Bias, RMSE, r across field-seasons | OpenET ensemble came within about 5 percent of flux towers at closed-balance sites (Melton et al., 2021), so our check is against a reference that is itself uncertain |
| Yield anomalies | R2 and RMSE of anomalies, skill score against climatology, leave-one-year-out | Report with and without the satellite inputs |
| Simulated vs measured trial values | RMSE, Willmott index of agreement d (Willmott, 1981), Nash-Sutcliffe efficiency with the decomposition of Gupta et al. (2009) | Moriasi et al. (2007) give rating bands for hydrological models |
| Direction of change | Share of published directional effects the tool reproduces | NRCS reports SCI got the SOC trend right in about 90 percent of long-term systems; use that as a bar |
| Rankings | Kendall tau between tool and trial or expert rankings | Report as is |
| Uncertainty bands | Coverage: share of observed outcomes inside the stated 80 percent band | Near 80 percent means the bands are honest |

## Hackathon experiments (fit in a few hours each)

### H1. Check the inputs against the ground

Question. Do the satellite inputs the tool shows a farmer match ground stations at our two sites?

Method.
1. US site: pull IMERG Final daily rain for the Marsden cell and the nearest three CoCoRaHS gauges for 2015 to 2025. Pull SMAP L4 surface and root-zone moisture and the nearest SCAN or USCRN station.
2. Haryana site: pull IMERG for the Karnal cells and the IMD 0.25 degree grid for the same years.
3. Compute r, monthly bias, POD, FAR and CSI for rain, and ubRMSE, bias and R for soil moisture.

Expected honesty result. The Haryana soil moisture check cannot run. ISMN lists one Indian station (Kanpur), far from Karnal. The tool should show "no ground check available here" on every SMAP card for Indian fields. That is a finding, not a failure.

Output. One validation card per input: "IMERG matched IMD at Karnal with r = x and a monsoon bias of y percent." The card links from every evidence card that uses that input.

### H2. Check the water balance against independent ET

Question. Is our FAO-56 crop water use close to satellite ET?

Method.
1. Run the FAO-56 dual Kc water balance for 20 to 50 fields at each site for 2019 to 2025, using the observed crop history (CSB in the US; farmer input or HLS classification in Haryana).
2. Compare seasonal ET per field with OpenET (US) and with ECOSTRESS L3 ET composites (Haryana). ECOSTRESS revisits are irregular, so compare only seasons with enough clear overpasses and report the count.
3. Check the order of crops. In Haryana, kharif rice ET should exceed maize, and rabi wheat ET should exceed mustard and chickpea. Davis et al. (2018) report that replacing rice with other cereals in India reduces water demand, which gives an outside reference for the direction.

Metrics. Seasonal bias and RMSE by crop; Kendall tau for the crop order.

Output. A scatter plot of our ET against satellite ET by crop, and a short "how far to trust the water numbers" paragraph.

### H3. Reproduce published rotation effects

Question. When we run the tool on a published trial, does it get the direction of each effect right?

Method.
1. Marsden Farm. Enter the 2-year corn-soybean, 3-year corn-soybean-oat with red clover, and 4-year corn-soybean-oat with alfalfa-alfalfa rotations. Davis et al. (2012) found grain yields, harvested mass and profit in the diverse systems similar to or greater than the 2-year system, with much lower agrichemical inputs and freshwater toxicity about two orders of magnitude lower. Check that the tool gives the longer rotations lower N fertiliser need, more living-cover days, a lower C factor, and an SCI-style score at least as good.
2. Morrow Plots. Enter continuous corn, corn-soybean and corn-oats-hay. Check the SOC direction against the long-term record.
3. Bowles et al. (2020). Check that the tool's drought-year comparison shows smaller relative yield loss for diverse rotations, as the 11-site analysis found.
4. Haryana. Enter conventional puddled rice-wheat and the conservation agriculture systems from Jat et al. (2019). Check water and SOC directions against the paper (values not read here; read the paper first).

Metric. A directional scorecard: number of published effects reproduced out of the number tested, and Kendall tau between tool and trial rankings per criterion.

Output. A table on the project page: "Tool matched 9 of 11 published directions." Mismatches are listed with reasons.

### Always-on check: does the ranking hold?

For every field, the tool runs a Monte Carlo over uncertain inputs (Kc ranges, N credit ranges, prices, weather years) and reports how often the top-ranked rotation stays on top. This is internal consistency, not external validity, and the page should say so. See mcda_ranking.md.

## Long-term experiments

### L1. Yield anomaly backtest at county and district scale

Train a yield-anomaly model per crop on NASS county yields (US) and ICRISAT district yields (India), with weather, SMAP, IMERG and NDVI features. Use leave-one-year-out cross-validation. Report R2, RMSE and skill against climatology, with and without the NASA features, so we can say how much NASA data adds. Check the coverage of the stated 80 percent bands.

Caution. Burchfield et al. (2024) found that at US county scale, rotation complexity showed yield benefits only for cotton and winter wheat, and corn yields were higher where rotations were simpler. County data mix many fields and practices, so a county backtest tests the weather and yield model, not the rotation effect. Do not claim it proves rotation benefits.

### L2. Process models against long-term trials

Run Layer 2 models (PCSE/WOFOST, AquaCrop-OSPy) and the SOC models (ICBM, RothC_Py) on the Morrow Plots, Marsden Farm, KBS LTER, the DRIVES sites and the Karnal conservation agriculture trials. Compare simulated yields and SOC with measurements using RMSE, Willmott d and NSE, and the sign accuracy of SOC trends. Publish one calibration file per site so others can rerun it.

### L3. Expert and farmer evaluation

Recruit two groups: agronomists (for example, Krishi Vigyan Kendra Karnal and Iowa State Extension, not yet contacted) and farmers in each region.

- Experts rank the candidate rotations for 10 real fields without seeing the tool, then with it. Report Kendall tau against the tool, and record each "what would change my mind" item they raise.
- Farmers complete a short comprehension check on uncertainty displays (for example, "how likely is the irrigation saving to exceed 200 mm?"). Report the share answered correctly and a System Usability Scale score.
- Track trust calibration: do users trust the tool more where its validation is strong and less where it is weak?

Write the protocol and hypotheses before data collection.

## What goes in the demo

- One slide or video beat: "We checked our inputs against ground gauges, our water use against satellite ET, and our rotation effects against 2 long-term trials. Here is where it matched and where it did not."
- A validation page in the app, linked from every evidence card.

## Sources

- Davis et al. (2012), Marsden Farm: https://doi.org/10.1371/journal.pone.0047149
- Liebman et al. (2008), Marsden Farm agronomic and economic performance: https://doi.org/10.2134/agronj2007.0222
- Caldrone et al. (2024), Morrow Plots dataset: https://doi.org/10.1038/s41597-024-03984-9
- Nafziger and others (2011), Morrow Plots SOC: https://doi.org/10.2134/agronj2010.0213ser
- Bowles et al. (2020): https://doi.org/10.1016/j.oneear.2020.02.007
- Burchfield et al. (2024): https://doi.org/10.1088/1748-9326/ad300b
- Robertson et al. (2014), KBS LTER: https://doi.org/10.1093/biosci/biu037
- Davis et al. (2018), alternative cereals in India: https://doi.org/10.1126/sciadv.aao1108
- Jat et al. (2019), basmati rice-wheat CA in NW India: https://doi.org/10.1080/03650340.2019.1566708
- Sidhu et al. (2019), sub-surface drip with CA in rice-wheat: https://doi.org/10.1016/j.agwat.2019.02.019
- Pai et al. (2014), IMD gridded rainfall: https://doi.org/10.54302/mausam.v65i1.851
- Reges et al. (2016), CoCoRaHS: https://doi.org/10.1175/bams-d-14-00213.1
- Schaefer et al. (2007), SCAN: https://doi.org/10.1175/2007jtecha930.1
- Bell et al. (2013), USCRN soil moisture: https://doi.org/10.1175/jhm-d-12-0146.1
- Dorigo et al. (2021), ISMN: https://doi.org/10.5194/hess-25-5749-2021
- ISMN network list (IIT_KANPUR, 1 station): https://ismn.bafg.de/en/networks
- ismn Python reader: https://github.com/TUW-GEO/ismn
- Colliander et al. (2017), SMAP validation with core sites, 0.04 m3/m3 requirement: https://doi.org/10.1016/j.rse.2017.01.021
- GMAO SMAP L4 assessment report, ubRMSE criterion: https://gmao.gsfc.nasa.gov/media/publications/zbly36ziNFDFbmYmvhQeVqPhUo/Reichle1083.pdf
- Melton et al. (2021), OpenET: https://doi.org/10.1111/1752-1688.12956
- ICRISAT District Level Data: http://data.icrisat.org/dld
- TCI and ICRISAT database coverage: https://icrisat.org/tci-and-icrisat-continue-partnership-to-improve-access-to-indian-food-systems-data
- NRCS SCI technical note (90 percent trend accuracy): https://nrcs.usda.gov/sites/default/files/2023-04/nrcs142p2_053273.pdf
- Willmott (1981): https://doi.org/10.1080/02723646.1981.10642213
- Gupta et al. (2009): https://doi.org/10.1016/j.jhydrol.2009.08.003
- Moriasi et al. (2007): https://doi.org/10.13031/2013.23153
- SCAN: https://www.nrcs.usda.gov/resources/data-and-reports/soil-climate-analysis-network
- USCRN: https://www.ncei.noaa.gov/access/crn/
- Crop Sequence Boundaries: https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php
