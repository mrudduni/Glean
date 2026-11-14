# Simulation engines for comparing rotations

This file compares crop and soil models that could run each candidate rotation on each field. It covers licence, Python access, crop coverage, multi-year rotation support, input needs, run time, and package maturity. It ends with a layered design for the hackathon demo and the portfolio phase.

We checked versions and licences on 14 November 2026 through the PyPI JSON API, the GitHub API, and the licence files in each repository. We also installed AquaCrop-OSPy and PCSE in an isolated virtual environment under Python 3.14.3 on Windows 11 and ran each one. Nothing was installed globally.

## Summary table

| Engine | Licence | Python access | Multi-year rotation with carry-over | Soil C and N | Run time per season (our test) | Latest release | Fit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Custom FAO-56 dual Kc water balance | Ours (Apache-2.0) | Native, about 300 lines of numpy | Yes, by design (soil water carries day to day across crops) | No (add simple N credit and SOC models, see soil_health_methods.md) | Under 10 ms (estimate, not measured) | n/a | Core for the demo |
| AquaCrop-OSPy | Apache-2.0 in the GitHub repo; the PyPI classifier says MIT (conflict, see notes) | `pip install aquacrop` | No. One crop per model run. Chain runs by passing end soil water as the next start (manual) | No N, no SOC | About 0.45 s (6 wheat seasons in 2.7 s) | 3.1.0, 22 June 2026 | Second line of evidence for water-limited yield |
| PCSE (WOFOST 7.2, 7.3, 8.1, LINGRA) | EUPL-1.1 or later (licence file); PyPI metadata says EUPL-1.2 | `pip install pcse` | Yes. The agromanagement file accepts several campaigns in sequence | WOFOST 8.1 has an N balance; multi-year SOC carry-over not confirmed | About 0.36 s (one demo season, including setup) | 6.0.13, 10 June 2026 | Portfolio layer, good crop list for India |
| Cycles | CC BY-NC-ND 4.0 (not open source) | Executable only; driven by text files. CyclesGym wraps it | Yes. Built for multi-year, multi-crop systems with C and N cycling | Yes | Not measured | v1.5.20, 26 May 2026 | Avoid for redistribution; research comparison only |
| CyclesGym | BSD-3-Clause | Gym interface to Cycles | Yes (through Cycles) | Through Cycles | Not measured | No release; last push 10 August 2022 | Later, RL only |
| APSIM Next Generation | APSIM General Use Licence (fee-free, not OSI) | apsimNGpy 1.5.6 (Apache-2.0) drives the .NET model through pythonnet | Yes. Strong on rotations, soil water, N and SOC | Yes | Not measured | ApsimX has no GitHub releases; builds come from apsim.info. Last push 13 November 2026 | Portfolio comparison, licence review needed |
| DSSAT CSM through DSSATTools | DSSAT CSM is BSD-3-Clause; DSSATTools is GPL-3.0-or-later | `pip install DSSATTools` (README says Linux only; use WSL or Colab on Windows) | Yes, sequence runs in DSSAT | Yes (CENTURY-based SOM option) | Not measured | DSSAT v4.8.6.0, 12 August 2026; DSSATTools 3.0.2, 3 April 2026 | Portfolio comparison; GPL affects how we ship it |
| SIMPLE crop model | Model published openly; one Python port (ataraxno/SIMPLE_crop_model) is Apache-2.0 | About 100 lines; reimplement or vendor the port | No carry-over by design | No | Milliseconds (estimate) | Python port last push 12 August 2021 | Optional fast yield proxy |
| SWAT+ | LGPL-2.1 (model); pySWATPlus 1.3.0 is GPL-3.0-or-later | pySWATPlus edits inputs and runs the executable | Yes, at HRU scale in a watershed | Yes | Watershed scale; heavy setup | pySWATPlus 1.3.0, 16 November 2025 | Wrong scale for one field; later for watershed views |

## Engine notes

### Custom FAO-56 dual Kc soil water balance

FAO-56 splits crop ET into transpiration and soil evaporation: Kc = Kcb + Ke. Ke is limited by the evaporable water in the top soil layer through a reduction coefficient Kr, which depends on total and readily evaporable water (TEW and REW). The root zone balance tracks depletion Dr, and the water stress coefficient is Ks = (TAW - Dr) / ((1 - p) x TAW) once Dr exceeds the readily available water (FAO-56 Chapters 7 and 8). Allen et al. (2005) describe the dual method and its use for bare soil and partial cover, which matters for fallow and residue periods between crops.

Why it fits the demo. Every number is traceable to an FAO-56 table or a satellite input. The daily loop runs across crop boundaries, so the soil water left after rice carries into wheat or mustard. Bare periods, cover crops and residue mulch change Ke directly, which links to the bare-field detection feature. It needs only NASA POWER weather (or IMERG rain), FAO-56 Kcb and stage lengths, and soil water holding capacity from SSURGO (US) or SoilGrids 2.0 (global, 250 m, with uncertainty layers, Poggio et al. 2021).

Limits. It gives water use and water stress, not yield. Yield needs a response function such as the FAO-33 Ky approach, or a model such as AquaCrop. It does not model N, pests or SOC.

### AquaCrop-OSPy

AquaCrop-OSPy (Kelly and Foster, 2021) is a Python port of AquaCrop-OS (Foster et al., 2017), itself an open version of FAO AquaCrop. It simulates canopy cover, biomass and yield from transpiration and water productivity.

Python 3.12 and later. Issue #166 ("Installation fails with Python 3.12+", opened July 2024) is still open on GitHub. The cause was the numba ahead-of-time compile step and `distutils`. Pull request #188 removed the numba AOT step in January 2025. Release 3.1.0 (22 June 2026) lists Python 3.9 to 3.12 classifiers and `requires_python >= 3.9`. In our test it installed and ran under Python 3.14.3 with numpy 2.5.4 and pandas 3.1.1. Six seasons of Tunis wheat took 2.7 s after a 5.3 s import and weather load. So the open issue looks stale, but the team should pin the version and run the test suite in CI.

Crops. The bundled parameter set has 37 entries, including Maize, Wheat, PaddyRice, Soybean, Sorghum, Cotton, Potato, SugarCane, Sunflower, DryBean, Barley, Quinoa, Tef, Tomato and AlfalfaGDD. It has no mustard or rapeseed, no millet, no chickpea, no lentil and no mungbean. For the Haryana case this is a real gap: maize and sorghum are covered, but mustard and pulses would need new crop files that someone must calibrate.

Rotations. `AquaCropModel` takes one `Crop` per run, plus optional fallow field management and an off-season switch. Multi-crop sequences mean chaining runs and passing soil water state by hand, which is not a documented feature.

Licence conflict. The GitHub repo reports Apache-2.0. The PyPI classifier says MIT. Both are permissive, so the risk is low, but we should cite the repo licence file.

### PCSE and WOFOST

PCSE runs WOFOST and LINGRA (de Wit et al., 2019 review 25 years of WOFOST). Version 6.0.13 installed and ran the built-in demo (`start_wofost(grid=31031, mode='wlp')`) under Python 3.14.3 in 0.36 s. It wrote a demo database to the user home folder (`~/.pcse/pcse.db`), which the team should know about.

Crops. The WOFOST 8.1 parameter branch has 23 crops: barley, cassava, chickpea, cotton, cowpea, faba bean, groundnut, maize, millet, mungbean, pigeonpea, potato, rapeseed, rice, seed onion, sorghum, soybean, sugar beet, sugarcane, sunflower, sweet potato, tobacco and wheat. That covers every crop in the Haryana shortlist (rice, wheat, maize, mustard as rapeseed, pearl millet as millet, mungbean, chickpea) as generic parameter sets. Local calibration is still needed.

Rotations. The YAML agromanagement format accepts a list of campaigns, each with its own crop, so one run can hold a full rotation. Whether soil water and soil N carry over between campaigns depends on the soil module in use. This is not confirmed from the docs we read and needs a test.

Licence. EUPL is a copyleft licence, but it is OSI-approved and allows linking from Apache-2.0 code if we do not modify PCSE. The team should confirm this reading before shipping.

### Cycles and CyclesGym

Cycles is a daily agroecosystem model with coupled C and N cycling, polycultures, relay cropping, tillage and multi-year rotations (Kemanian et al., 2022, SSRN preprint). This makes it the closest fit to the rotation question in theory. The licence file is Creative Commons BY-NC-ND 4.0 (copyright 2023 Armen Kemanian). That licence forbids derivatives and commercial use, and it is not an open-source licence. Space Apps rules require non-NASA materials to be freely available or OSI licensed. Calling the free binary may be acceptable, but bundling it in our repo is not safe without the author's permission.

CyclesGym (Turchetta et al., 2022) is BSD-3-Clause and wraps Cycles as a reinforcement learning environment. Its README recommends Python 3.8 with conda, and the last push was August 2022. It is not on PyPI. Treat it as a later research option.

### APSIM Next Generation

APSIM Next Generation (Holzworth et al., 2018) models rotations, soil water, N and SOC carry-over and is widely validated. Its General Use Licence is fee-free but not OSI-approved, and it vests ownership of improvements in the licensors. apsimNGpy (Apache-2.0, version 1.5.6, August 2026) drives it from Python through pythonnet, so the user must install the .NET APSIM build separately. Good for an expert comparison run, not for the shipped core.

### DSSAT through DSSATTools

The DSSAT CSM (Jones et al., 2003) source is BSD-3-Clause and version 4.8.6.0 came out in August 2026. DSSATTools 3.0 is GPL-3.0-or-later, its README says it has only been tested on Linux, and version 3.0 broke backward compatibility. DSSAT supports sequence (rotation) runs and a CENTURY-based soil organic matter option. If we import DSSATTools in our app, the GPL applies to the distributed combination. Running it as a separate service avoids that, but the team should check.

### SIMPLE crop model

SIMPLE (Zhao et al., 2019) is a generic model with few parameters that simulates daily biomass and yield from radiation use efficiency, temperature, heat and drought stress, and CO2. The paper lists parameters for 14 crops (number from the paper abstract summary, not re-checked against the full text). It suits a fast yield proxy per crop and year, but it has no soil carry-over.

### SWAT+

SWAT+ (Bieger et al., 2017) is a watershed model with HRUs and full rotation scheduling. It is LGPL-2.1. It needs watershed delineation, which is the wrong scale for one farmer's field. It becomes useful later for a watershed view of nitrate or sediment.

## Inputs we can satisfy from open data

| Input | US source | India source | Notes |
| --- | --- | --- | --- |
| Daily weather (Tmax, Tmin, radiation, humidity, wind, rain) | NASA POWER, IMERG for rain | NASA POWER, IMERG; IMD 0.25 degree gridded rain (Pai et al., 2014) as a check | POWER is about 0.5 degree, so valley frost and local rain cells are missed |
| Soil texture, water holding, organic C, bulk density | SSURGO through SDA | SoilGrids 2.0 (250 m) | SoilGrids gives prediction quantiles, which feed uncertainty |
| Slope | SRTM | SRTM | For RUSLE LS |
| Crop history | CDL and Crop Sequence Boundaries | No national field-level product; farmer input, or classification from HLS and Sentinel-1 | Google's ALU field boundaries exist for India; licence terms not confirmed |
| Crop parameters | FAO-56 tables, AquaCrop files, WOFOST YAML | Same, plus Indian calibration papers | Calibration is the main local-review item |
| Irrigation | Farmer input; OpenET for checking | Farmer input; ECOSTRESS ET for checking | Haryana rice is almost all irrigated, so irrigation dominates the water balance |

## Recommended layered design

Layer 1, the transparent core (hackathon). A custom FAO-56 dual Kc water balance runs every rotation over every weather year (for example 2001 to 2025 from POWER and IMERG). It outputs, per rotation and year, irrigation demand, stress days in sensitive stages, bare-soil days, drainage, and a Ky-based relative yield. Every number links to its FAO-56 table row or dataset. Add rule-based N credits, a RUSLE relative C factor, an SCI-style soil score and a STIR tillage score (see soil_health_methods.md). This layer runs in well under a second per field, so sliders can recompute live.

Layer 2, a crop model as second opinion (portfolio). Run PCSE/WOFOST 8.1 for every crop in the rotation, because its 23-crop list covers both the US Corn Belt and the Haryana shortlist. Use AquaCrop-OSPy where it has the crop (maize, wheat, rice, sorghum, soybean) as a third check on water-limited yield. Show agreement or disagreement between layers as an uncertainty signal: "the simple water balance and WOFOST agree that mustard needs about half the irrigation of wheat" or "the two models disagree, so check locally".

Layer 3, expert comparison runs (later, offline). APSIM Next Gen or DSSAT runs for a few benchmark sites and rotations, done once by the team, to check Layers 1 and 2. Licences make these unsuitable for the shipped app.

Why this split. Judges score Validity and Presentation. A transparent core that the demo can explain in one sentence beats a black-box model that takes a day to set up. The second layer adds scientific weight without blocking the demo.

## Risks

- AquaCrop-OSPy lacks mustard, millet and pulse parameters. Do not present AquaCrop yields for those crops.
- PCSE carry-over of soil water and N across campaigns is not confirmed.
- Cycles and APSIM licences are not OSI-approved. DSSATTools is GPL.
- All crop models need local calibration. Generic parameters can be far off for Indian varieties and planting dates.

## Sources

- PyPI JSON API, queried 14 November 2026: https://pypi.org/pypi/aquacrop/json, https://pypi.org/pypi/pcse/json, https://pypi.org/pypi/DSSATTools/json, https://pypi.org/pypi/apsimNGpy/json, https://pypi.org/pypi/pyswatplus/json
- GitHub API repository records, queried 14 November 2026: https://api.github.com/repos/aquacropos/aquacrop, https://api.github.com/repos/ajwdewit/pcse, https://api.github.com/repos/PSUmodeling/Cycles, https://api.github.com/repos/kora-labs/cyclesgym, https://api.github.com/repos/APSIMInitiative/ApsimX, https://api.github.com/repos/DSSAT/dssat-csm-os, https://api.github.com/repos/daquinterop/Py_DSSATTools, https://api.github.com/repos/swat-model/swatplus, https://api.github.com/repos/MAGALA-RICHARD/apsimNGpy, https://api.github.com/repos/ataraxno/SIMPLE_crop_model
- AquaCrop Python 3.12 issue: https://github.com/aquacropos/aquacrop/issues/166
- AquaCrop numba AOT removal: https://github.com/aquacropos/aquacrop/pull/188
- AquaCrop CI modernisation PR: https://github.com/aquacropos/aquacrop/pull/205
- PCSE licence: https://github.com/ajwdewit/pcse/blob/master/LICENSE
- WOFOST 8.1 crop parameters: https://github.com/ajwdewit/WOFOST_crop_parameters/tree/wofost81
- Cycles licence (CC BY-NC-ND 4.0): https://github.com/PSUmodeling/Cycles
- CyclesGym README: https://github.com/kora-labs/cyclesgym
- APSIM General Use Licence: https://github.com/APSIMInitiative/ApsimX/blob/master/LICENSE.md
- DSSATTools README: https://github.com/daquinterop/Py_DSSATTools
- SWAT+ licence: https://github.com/swat-model/swatplus/blob/main/LICENSE
- FAO-56 Chapter 7, dual crop coefficient: https://www.fao.org/4/x0490e/x0490e0c.htm
- FAO-56 Chapter 8, water stress: https://www.fao.org/4/x0490e/x0490e0e.htm
- Allen et al. (2005), FAO-56 dual crop coefficient method: https://doi.org/10.1061/(asce)0733-9437(2005)131:1(2)
- Kelly and Foster (2021), AquaCrop-OSPy: https://doi.org/10.1016/j.agwat.2021.106976
- Foster et al. (2017), AquaCrop-OS: https://doi.org/10.1016/j.agwat.2016.11.015
- de Wit et al. (2019), 25 years of WOFOST: https://doi.org/10.1016/j.agsy.2018.06.018
- Kemanian et al. (2022), Cycles model (SSRN preprint): https://doi.org/10.2139/ssrn.4188402
- Turchetta et al. (2022), CyclesGym: https://proceedings.neurips.cc/paper_files/paper/2022/hash/4a22ceafe2dd6e0d32df1f7c0a69ab68-Abstract-Datasets_and_Benchmarks.html
- Holzworth et al. (2018), APSIM Next Generation: https://doi.org/10.1016/j.envsoft.2018.02.002
- Jones et al. (2003), DSSAT: https://doi.org/10.1016/s1161-0301(02)00107-7
- Zhao et al. (2019), SIMPLE crop model: https://doi.org/10.1016/j.eja.2019.01.009
- Bieger et al. (2017), SWAT+: https://doi.org/10.1111/1752-1688.12482
- Poggio et al. (2021), SoilGrids 2.0: https://doi.org/10.5194/soil-7-217-2021
- Pai et al. (2014), IMD gridded rainfall: https://doi.org/10.54302/mausam.v65i1.851
- Google Agricultural Landscape Understanding: https://developers.google.com/agricultural-understanding/landscape-understanding
