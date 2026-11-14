# Key papers

This list covers 17 papers from 2016 onward on rotation effects, mapping crop sequences from the Cropland Data Layer (CDL), satellite soil moisture and water stress in agriculture, cover crop detection, and AI for rotation planning. We found candidates with the TinyFish research-paper search and confirmed titles, authors, years, and venues with Crossref or Europe PMC records. Summaries are our own wording, based on each paper's abstract or a publisher or university summary of it.

## Rotation effects and why they matter

### 1. Long-term evidence shows that crop-rotation diversification increases agricultural resilience to adverse growing conditions in North America

- Authors: T. M. Bowles, M. Mooshammer, Y. Socolar, F. Calderón, and others
- Year and venue: 2020, One Earth 2(3)
- Link: https://doi.org/10.1016/j.oneear.2020.02.007

The authors pooled data from 11 long-term rotation experiments across North America to test whether diverse rotations protect maize yields in bad years. More diverse rotations raised maize yields by 28.1 percent on average across all conditions and cut yield losses in drought by 14 to 90 percent, which supports framing rotation diversity as climate risk reduction.

### 2. Continuous corn and soybean yield penalties across hundreds of thousands of fields

- Authors: C. A. Seifert, M. J. Roberts, D. B. Lobell
- Year and venue: 2017, Agronomy Journal 109(2)
- Link: https://doi.org/10.2134/agronj2016.03.0134

Using 748,374 commercial field yields from six Corn Belt states (2007 to 2012), the authors measured how much yield farmers lose by planting the same crop again. Continuous corn averaged a 4.3 percent penalty and continuous soybean a 10.3 percent penalty, with larger corn penalties in dry, low-yield areas and soybean penalties that grew with each extra year.

### 3. Rotational complexity across US counties is currently insufficient to observe yield gains in major crops

- Authors: E. K. Burchfield, M. S. Crossley, K. S. Nelson
- Year and venue: 2024, Environmental Research Letters 19
- Link: https://doi.org/10.1088/1748-9326/ad300b

This study built a county-by-year panel for 2008 to 2020 to test whether rotation complexity raises yields at national scale. Benefits showed up only for cotton and winter wheat, corn yields were higher where rotations were simpler, and the authors argue that most U.S. rotations are too simple and the record too short to show the gains seen in long-term trials.

## Mapping and predicting crop sequences from the CDL

### 4. Biophysical and policy factors predict simplified crop rotations in the US Midwest

- Authors: Y. Socolar, B. R. Goldstein, P. de Valpine, T. M. Bowles
- Year and venue: 2021, Environmental Research Letters 16
- Link: https://doi.org/10.1088/1748-9326/abf9ca

The authors created a rotation complexity index from CDL crop histories and applied it to 1.5 million Midwest fields. Rotations were simpler on the best land, in wetter areas, and closer to biofuel plants, which shows that both soil and policy shape rotation choices.

### 5. Pre-season crop type mapping using deep neural networks

- Authors: R. Yaramasu, V. Bandaru, K. Pnvr
- Year and venue: 2020, Computers and Electronics in Agriculture 176
- Link: https://doi.org/10.1016/j.compag.2020.105664

The authors trained a ConvLSTM encoder-decoder on historical CDL maps of Nebraska to predict each pixel's crop before the season starts. The network reached up to 88 percent accuracy for 2017 and beat a Markov chain baseline for 2018 and 2019 (overall accuracy 0.77 versus 0.67), which shows crop history alone carries strong rotation signal.

### 6. Preseason crop type prediction using crop sequence boundaries

- Authors: J. Abernethy, P. Beeson, C. Boryan, K. Hunt, L. Sartore
- Year and venue: 2023, Computers and Electronics in Agriculture 208
- Link: https://doi.org/10.1016/j.compag.2023.107768

USDA NASS staff grouped CDL pixels with identical crop histories into polygons called Crop Sequence Boundaries and used them to predict next season's crop. This approach used all CDL data without sampling and gave the best overall accuracy in 23 of 24 tests, and the boundary product gives our tool ready-made field polygons with crop history.

### 7. A new approach to characterising and predicting crop rotations using national-scale annual crop maps

- Authors: E. V. Upcott, P. A. Henrys, J. W. Redhead, S. G. Jarvis, R. F. Pywell
- Year and venue: 2023, Science of the Total Environment 860
- Link: https://doi.org/10.1016/j.scitotenv.2022.160471

Using six years of national crop maps, the authors extracted crop sequences for every field in Great Britain, classified rotations by length, type, and diversity, and predicted the next crop with transition probability matrices. Predictions reached 36 to 89 percent accuracy and worked best at local scale with five-year histories, which offers a simple, explainable baseline we can copy with the CDL.

## Cover crops and residue from satellites

### 8. Satellite detection of cover crops and their effects on crop yield in the Midwestern United States

- Authors: C. A. Seifert, G. Azzari, D. B. Lobell
- Year and venue: 2018, Environmental Research Letters 13
- Link: https://doi.org/10.1088/1748-9326/aac4c8

The authors built a Landsat classifier for winter cover crops with 91.5 percent accuracy and mapped cover crops on Midwest maize and soybean fields since 2008. After controlling for soil quality, cover crops were linked to small yield gains of 0.65 percent for maize and 0.35 percent for soybean.

### 9. Recent rapid increase of cover crop adoption across the U.S. Midwest detected by fusing multi-source satellite data

- Authors: Q. Zhou, K. Guan, S. Wang, C. Jiang, and others
- Year and venue: 2022, Geophysical Research Letters 49
- Link: https://doi.org/10.1029/2022GL100249

The team fused Landsat and MODIS data to map winter cover crops across the Midwest from 2011 to 2021. They found adoption rose from 1.8 percent of fields to 7.2 percent, with gains linked to government programs, according to the University of Illinois summary of the paper.

### 10. Recent cover crop adoption is associated with small maize and soybean yield losses in the United States

- Authors: J. M. Deines, K. Guan, B. López, Q. Zhou, C. S. White, S. Wang, D. B. Lobell
- Year and venue: 2023, Global Change Biology 29(3)
- Link: https://doi.org/10.1111/gcb.16489

Using satellite yield maps for over 90,000 fields and causal forests, the authors estimated yield effects of cover crops as farmers actually used them in 2019 and 2020. Fields with three or more years of cover crops had average losses of 5.5 percent for maize and 3.5 percent for soybean, with larger maize losses on better soils and in cool, dry springs.

## Satellite soil moisture, ET, and water stress in agriculture

### 11. Intercomparison of soil moisture, evaporative stress, and vegetation indices for estimating corn and soybean yields over the U.S.

- Authors: I. E. Mladenova, J. D. Bolten, W. T. Crow, M. C. Anderson, C. R. Hain, D. M. Johnson, and others
- Year and venue: 2017, IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing 10
- Link: https://doi.org/10.1109/JSTARS.2016.2639338

This paper compares satellite soil moisture, the Evaporative Stress Index, and vegetation indices as predictors of U.S. corn and soybean yields. We confirmed the title, authors, and venue but could not read the abstract, so its main findings are not confirmed here and the team should read it before citing results.

### 12. Agricultural drought monitoring via the assimilation of SMAP soil moisture retrievals into a global soil water balance model

- Authors: I. E. Mladenova, J. D. Bolten, W. Crow, N. Sazib, C. Reynolds
- Year and venue: 2020, Frontiers in Big Data 3
- Link: https://doi.org/10.3389/fdata.2020.00010

The authors added SMAP soil moisture to the USDA Foreign Agricultural Service Palmer model and tested it on droughts in California (2015), South Africa (2017), and Australia (2018). The SMAP version gave more spatial detail in root-zone soil moisture and agreed better with CHIRPS rainfall and NDVI, which supports using SMAP-based root-zone products for crop decisions.

### 13. The Evaporative Stress Index as an indicator of agricultural drought in Brazil: an assessment based on crop yield impacts

- Authors: M. C. Anderson, C. A. Zolin, P. C. Sentelhas, C. R. Hain, K. Semmens, and others
- Year and venue: 2016, Remote Sensing of Environment 174
- Link: https://doi.org/10.1016/j.rse.2015.11.034

The authors correlated the ESI, TRMM rainfall anomalies, and MODIS leaf area anomalies with Brazilian crop yields from 2003 to 2013. The ESI gave higher state-level yield correlations for most crops, and for soybean its correlations peaked 10 to 25 days earlier than the other indices, which makes it a good early warning signal.

### 14. OpenET: filling a critical data gap in water management for the western United States

- Authors: F. S. Melton, J. Huntington, R. Grimm, J. Herring, M. Hall, D. Rollison, and others
- Year and venue: 2021, Journal of the American Water Resources Association
- Link: https://doi.org/10.1111/1752-1688.12956

The paper describes OpenET, which runs six satellite ET models on Google Earth Engine to produce 30 m field-scale ET from Landsat. In the authors' accuracy comparison, the ensemble mean and four of the models came within about 5 percent of closed-balance flux tower ET, which makes OpenET a credible check on our Kc-based water use estimates.

### 15. Crop-CASMA: a web geoprocessing and map service based architecture and implementation for serving soil moisture and crop vegetation condition data over U.S. cropland

- Authors: C. Zhang, Z. Yang, H. Zhao, Z. Sun, L. Di, R. Bindlish, and others
- Year and venue: 2022, International Journal of Applied Earth Observation and Geoinformation
- Link: https://doi.org/10.1016/j.jag.2022.102902

The paper explains how USDA NASS and George Mason University built Crop-CASMA to serve SMAP soil moisture and MODIS vegetation indices through standard OGC web services. It is a useful design reference for serving NASA rasters to farm users, though we read only the search summary, not the full abstract.

## AI for rotation planning

### 16. AI- and data-driven crop rotation planning

- Authors: S. Fenz, T. Neubauer, J. K. Friedel, M.-L. Wohlmuth
- Year and venue: 2023, Computers and Electronics in Agriculture 212
- Link: https://doi.org/10.1016/j.compag.2023.108160

The authors trained a deep Q-network agent on crop successor suitability matrices (from literature and NDVI data), contribution margins, and nitrogen demand to generate rotation sequences. Practitioners and rotation experts judged most generated sequences realistic and consistent with existing rotation rules.

### 17. Learning long-term crop management strategies with CyclesGym

- Authors: M. Turchetta, L. Corinzia, S. Sussex, and others
- Year and venue: 2022, Advances in Neural Information Processing Systems (Datasets and Benchmarks track)
- Link: https://proceedings.neurips.cc/paper_files/paper/2022/hash/4a22ceafe2dd6e0d32df1f7c0a69ab68-Abstract-Datasets_and_Benchmarks.html

CyclesGym wraps the multi-year, multi-crop Cycles crop model as a reinforcement learning environment with modular states, rewards, and weather generators. The authors show case studies on nitrogen fertilization and crop planning, which makes it a ready test bed if our project later explores RL.

## How these papers shape our tool

- Papers 1 to 3 justify a "diversified rotation" option and also warn that national data show weaker gains than trials, so the tool should present rotation benefits with ranges, not single numbers.
- Papers 4 to 7 show how to read a field's existing rotation from the CDL and Crop Sequence Boundaries, and a transition matrix (paper 7) is the simplest explainable baseline.
- Papers 8 to 10 give both the method for detecting cover crops from Landsat and the evidence that their yield effects are small and can be negative.
- Papers 11 to 15 support SMAP root-zone soil moisture, ESI, and OpenET as water-risk evidence.
- Papers 16 and 17 point to RL as a later portfolio extension, not a hackathon core.

## Sources

- TinyFish research-paper search results (queries on CDL rotation mapping, SMAP in agriculture, ML rotation planning, cover crop detection, ESI, rotation complexity), run November 2026.
- Crossref metadata for each DOI above: https://api.crossref.org/works/{DOI}
- Europe PMC abstracts for papers 5, 6, 7, 10, 13, 16: https://www.ebi.ac.uk/europepmc/
- Bowles et al. (2020) summary values: https://experts.umn.edu/en/publications/long-term-evidence-shows-that-crop-rotation-diversification-incre/ and https://cropwatch.unl.edu/2021/more-diverse-crop-rotations-improve-yield-yield-stability-and-soil-health/
- Seifert et al. (2017) summary: https://cropwatch.unl.edu/2020/yield-penalties-continuous-corn-and-soybean-midwest-us/
- Zhou et al. (2022) adoption figures: https://aces.illinois.edu/news/cover-cropping-72-us-midwest-boosted-government-programs
- Melton et al. (2021) accuracy figure: https://digitalcommons.csumb.edu/context/aes_fac/article/1029/viewcontent/OpenET___Filling_a_Critical_Data_Gap.pdf
- Crop-CASMA paper record: https://www.sciencedirect.com/science/article/pii/S1569843222001042
