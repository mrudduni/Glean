# Multi-criteria ranking of rotations

This file compares ways to rank three to five rotation strategies against farmer priorities. It covers TOPSIS, weighted sum, PROMETHEE and Pareto display, simple ways to elicit weights, and sensitivity analysis that shows when the top rank flips. It then reviews the team's proposed "Water-Smart Rotation Score" for Haryana and proposes a better-founded version. The last section lists Python libraries with licences.

## Methods compared

| Method | How it works | Strengths | Weaknesses | Fit |
| --- | --- | --- | --- | --- |
| Weighted sum (SMART family) | Normalise each criterion to a 0 to 1 value, multiply by weights, add | Easiest to explain: "40 percent of the score is water". Each criterion's contribution can be shown as a bar segment | Assumes criteria trade off linearly. Results depend on the normalisation range | Primary method |
| TOPSIS (Hwang and Yoon, 1981) | Rank by closeness to an ideal best and distance from an ideal worst option on weighted, normalised criteria | Widely used (Behzadian et al., 2012 survey); one line in pymcdm | Harder to explain. Adding or removing an option can reverse the ranking of others (García-Cascales and Lamata, 2012) | Cross-check |
| PROMETHEE II (Brans and Vincke, 1985) | Pairwise preference functions per criterion, then net outranking flow | Handles "a 10 mm difference does not matter" thresholds | Many parameters; hard to explain to farmers | Later, for agronomist view |
| AHP (Saaty, 1977) | Pairwise comparisons give weights and a consistency ratio | Catches contradictory answers | Many questions (n(n-1)/2); known rank reversal debates | Optional weight elicitation only |
| Pareto display | Show which options are dominated (worse on every criterion) and plot trade-offs | Needs no weights; honest | With 5 or more criteria few options are dominated | Always show alongside the ranking |

Recommendation. Use a weighted sum on value-normalised criteria as the main ranking, because farmers can see each part. Run TOPSIS as a check and flag any disagreement. Always mark dominated options. With three to five rotations, a small table of all criteria is readable, so the ranking supports the table rather than replacing it.

## Eliciting farmer weights simply

| Approach | Effort for the farmer | Notes |
| --- | --- | --- |
| Rank order, then rank-order centroid (ROC) weights | Lowest: order the priorities | Edwards and Barron (1994) recommend ROC in SMARTER. For n criteria, w_i = (1/n) x sum from k = i to n of 1/k. For 5 criteria: 0.457, 0.257, 0.157, 0.090, 0.040. For 6: 0.408, 0.242, 0.158, 0.103, 0.061, 0.028 (computed by us from the formula) |
| Swing weighting | Low to medium: "If you could move one criterion from its worst to its best value among these rotations, which first? How much is the next swing worth compared with that?" | Weights reflect the actual ranges in this field's options, which avoids weighting criteria that barely differ |
| Sliders | Low, interactive | Good for exploration after a first ranking. Show the rank-flip points on each slider |
| AHP pairwise | Medium to high | Use only in the agronomist view |

Riabacke et al. (2012) review weight elicitation and support simple, range-aware methods like these.

Default for the app. Ask the farmer to order five priorities, compute ROC weights, show the ranking, then let sliders adjust. Show the weights as rupees-and-millimetres statements where possible ("you value 100 mm of water as much as Rs 2,000 per acre").

## Sensitivity: when does the rank flip?

1. One-at-a-time thresholds. For each weight, find the smallest change that changes the top option. Triantaphyllou and Sánchez (1997) and Wolters and Mareschal (1995) give closed-form versions for additive models. For a weighted sum it is a small linear solve. Show it as "Rotation B stays first unless water drops below 22 percent of your priorities."
2. Monte Carlo over weights. Sample weights near the farmer's (for example from a Dirichlet distribution centred on them) and report the share of draws in which each option ranks first (Butler et al., 1997).
3. Monte Carlo over inputs. Sample uncertain inputs (Kc ranges, N credits, prices, weather years) and repeat. Kolios et al. (2016) compare MCDA methods under stochastic inputs this way.
4. Global sensitivity. SALib (MIT) gives Sobol indices that rank which inputs drive the score. Use it in the agronomist view.

Display. "Rotation B ranked first in 72 of 100 test runs. It loses first place mainly when the maize price falls."

## Review of the proposed Water-Smart Rotation Score

The proposal for the Karnal, Kurukshetra and Kaithal belt is:

Score = 0.40 x soil moisture percentile + 0.25 x rainfall anomaly + 0.20 x thermal GDD fit + 0.15 x water savings,

with SMAP root-zone soil moisture as a 30-day leading indicator of NDVI, citing the NASA DAPI work (NTRS 20240012812).

### What is good

- It puts water first, which suits Haryana. GRACE showed severe groundwater depletion across Rajasthan, Punjab and Haryana (Rodell et al., 2009). State policy already pays farmers to move out of paddy (Mera Pani Meri Virasat).
- It uses NASA data the judges will recognise.
- GDD fit is a real rotation property: whether each crop's thermal needs fit the season.

### Problems

1. Two of the four criteria cannot tell rotations apart. For one field in one month, the soil moisture percentile and the rainfall anomaly are the same whichever rotation you plan. They describe the field's weather, not the rotation. In our test with three rotations that share the same moisture and rain values, TOPSIS gave exactly the same scores (0.357, 0.760, 0.429) with and without those two criteria. In a raw weighted sum on 0 to 100 scales they add the same amount to every option (about 25 points in our example, with moisture at 35 and rain at 45), which compresses the visible gaps (41.3, 47.8 and 47.5 out of 100) and suggests a precision the score does not have. So 65 percent of the weight does no ranking work.
2. The score mixes two decisions. A rotation is a multi-year plan. A current-month moisture percentile is in-season information, useful for "should I sow now" or "should I irrigate this week", not for "which rotation should this field follow for the next five years". Mixing them means the rotation ranking changes every month with the weather, which will confuse farmers and judges.
3. In irrigated Haryana, soil moisture mostly reflects irrigation. Most rice and wheat in the belt is irrigated from canals and tubewells (a cited irrigated share for these districts is not confirmed here; ICRISAT district data include irrigated area and can supply it). A high SMAP percentile in July may mean heavy flooding of paddy, not a wet year. As a "water-smart" signal it can point the wrong way: the most water-hungry rotation makes the soil wettest.
4. Scale mismatch. SMAP L4 is a 9 km product. A Haryana smallholder field is often under 1 ha. The percentile describes the landscape, mostly paddy in kharif.
5. Short climatology. SMAP starts in 2015, so a percentile rests on about 11 years. That is a weak base for a percentile, especially for extremes.
6. The DAPI claim needs care. Le et al. (2024, Geophysical Research Letters) combine SMAP-based root-zone soil moisture with NDVI to forecast NDVI for corn, cotton, soybean and wheat across the contiguous US. The abstract reports better skill than climatology, with the largest gains in water-limited regions and during floods and droughts. We could not extract the full text (the PDF text layer is encoded), so the "30-day lead" is not confirmed by us. The study is CONUS only and found the most benefit where water limits growth, which is the opposite of irrigated Haryana. It forecasts in-season vegetation health. It does not rank rotations.
7. Weights have no stated basis. 40, 25, 20 and 15 are not from a study or from farmers. Judges will ask why.
8. Direction is unclear. Is a high moisture percentile good or bad? For a rotation decision, neither.

### A better-founded version: two panels

Panel A, "This season on your field" (shown, not ranked).

| Signal | Data | Note |
| --- | --- | --- |
| Root-zone soil moisture percentile | SMAP L4, 9 km | Landscape-scale; reflects irrigation in kharif; climatology from 2015 |
| Rainfall to date and SPI-3 | IMERG, checked against IMD grid | Monsoon onset and breaks |
| Vegetation outlook | NDVI from HLS; DAPI-style forecast as a research feature | Label as experimental outside CONUS |
| GDD to date | NASA POWER | For sowing windows |

Panel B, "Rotation comparison" (ranked). Every criterion is computed per rotation over a weather-year ensemble (for example 2001 to 2025), so the criteria differ between rotations and carry ranges.

| Criterion | Unit | How we compute it | Why it belongs |
| --- | --- | --- | --- |
| Irrigation water need | mm per year, median and 80 percent range | FAO-56 dual Kc water balance with POWER and IMERG, including puddling and percolation for rice | The core of "water-smart"; checked against ECOSTRESS ET (validation_plan.md H2) |
| Groundwater draw | mm per year from tubewells | Irrigation need times the farmer's share from tubewells | Turns GRACE regional decline into a field-level number the farmer controls |
| Water stress exposure in sensitive stages | Share of years with root-zone depletion above the readily available water at flowering or grain fill | Same water balance, per crop window | This is where soil moisture belongs: as crop-specific exposure, not a single current percentile. SMAP climatology checks the simulated seasonal pattern |
| Heat and frost exposure | Days above crop thresholds in sensitive stages; frost probability | POWER Tmax and Tmin per crop window | Captures thermal fit better than GDD alone (for example terminal heat in wheat grain fill; thresholds need crop-specific citations before use) |
| Net return | Rs per acre per year, median and range | Yields times prices (MSP where procured, market otherwise), minus costs, plus scheme incentives | Farmers decide on money; price risk is shown as a range |
| Soil health direction | SCI-style direction, C factor, residue burning avoided | See soil_health_methods.md | Long-term field asset |
| Practicality | Farmer score 1 to 5 | Equipment, labour, market access, procurement | Local knowledge that no satellite has |

Weights. The farmer orders the criteria and the app computes ROC weights. A "water-first" preset puts irrigation water need and groundwater draw first and second (ROC 0.408 and 0.242 for six criteria), with the reason stated: groundwater decline in the region (Rodell et al., 2009) and the state's diversification policy. The farmer can change it.

What changes in the result. The ranking now responds to differences between rotations (water need, exposure, returns), not to this month's weather. The in-season signals still appear, and they feed tactical advice such as sowing date, without moving the multi-year plan.

How this works for a US field. The same two panels apply. Swap MSP for county price data, the scheme incentive for NRCS CSP payments, and the IMD check for CoCoRaHS.

## Python libraries

| Library | Version (PyPI, 14 Nov 2026) | Licence | Notes |
| --- | --- | --- | --- |
| pymcdm | 1.4.0, 31 January 2026 | MIT | TOPSIS, VIKOR, PROMETHEE, weighting methods. Needs Python 3.11 or later. Installed and ran under Python 3.14.3 in our test. 25 GitHub stars, last push 6 September 2026 |
| pyDecision | 5.1.8, 12 October 2026 | GPL-3.0 or later | Very broad method set, but GPL and heavy dependencies (flask, openai, google-genai, llmx). Avoid in the shipped app |
| mcdm | 1.4, May 2022 | MIT | Pins numpy below 2; stale. Avoid |
| SALib | 1.6.0, 19 September 2026 | MIT | Sobol and Morris sensitivity |
| pymoo | 0.6.2, 28 June 2026 | Apache-2.0 | Multi-objective optimisation and Pareto tools; only needed if we generate rotations instead of comparing a fixed set |

A weighted sum, ROC weights and one-at-a-time thresholds are each a few lines of numpy, so the core does not need any of these libraries. Use pymcdm only for the TOPSIS cross-check.

## Sources

- Hwang and Yoon (1981): https://doi.org/10.1007/978-3-642-48318-9_3
- Behzadian et al. (2012), TOPSIS survey: https://doi.org/10.1016/j.eswa.2012.05.056
- García-Cascales and Lamata (2012), rank reversal in TOPSIS: https://doi.org/10.1016/j.mcm.2011.12.022
- Brans and Vincke (1985), PROMETHEE: https://doi.org/10.1287/mnsc.31.6.647
- Saaty (1977), AHP: https://doi.org/10.1016/0022-2496(77)90033-5
- Edwards and Barron (1994), SMARTS and SMARTER: https://doi.org/10.1006/obhd.1994.1087
- Riabacke et al. (2012), weight elicitation review: https://doi.org/10.1155/2012/276584
- Triantaphyllou and Sánchez (1997): https://doi.org/10.1111/j.1540-5915.1997.tb01306.x
- Wolters and Mareschal (1995): https://doi.org/10.1016/0377-2217(93)e0343-v
- Butler et al. (1997): https://doi.org/10.1016/s0377-2217(96)00307-4
- Kolios et al. (2016): https://doi.org/10.3390/en9070566
- Le et al. (2024), DAPI, SMAP for forecasting NDVI: https://doi.org/10.1029/2024gl111187
- NTRS record 20240012812: https://ntrs.nasa.gov/citations/20240012812
- Rodell et al. (2009): https://doi.org/10.1038/nature08238
- Mera Pani Meri Virasat incentive (Tribune, June 2025): https://tribuneindia.com/news/haryana/haryana-sets-target-of-1l-acre-under-mera-pani-meri-virasat-scheme
- FAO-56 Chapter 7: https://www.fao.org/4/x0490e/x0490e0c.htm
- PyPI JSON API: https://pypi.org/pypi/pymcdm/json, https://pypi.org/pypi/pyDecision/json, https://pypi.org/pypi/mcdm/json, https://pypi.org/pypi/SALib/json, https://pypi.org/pypi/pymoo/json
- pymcdm repository: https://github.com/kotbaton/pymcdm
- pyDecision licence: https://github.com/Valdecy/pyDecision/blob/master/LICENSE
