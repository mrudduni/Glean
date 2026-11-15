# Methods

This document describes how the model (role M) turns NASA and USDA data into the numbers the app shows: the Rotation Replay, the Field Calendar, the strategy scores and card facts, and the validation badges. Every tunable constant lives in [model/config.py](../model/config.py) and is listed below. Code paths are relative to the repo root.

## In plain language

For each of the three demo fields we replay every candidate rotation on the field's real daily weather from 2000 to 2025. A simple soil-water model tracks how much water the soil holds each day. Crops draw water according to the FAO-56 method, rain refills the soil, some rain runs off, and a pivot refills the soil when it gets too dry, up to the seasonal water cap the farmer chooses. From the water the crop got, we estimate its yield as a share of the county average yield, then turn that into revenue at the 2020 to 2024 average price. We also count the days the soil lies bare, and how many of those days had heavy rain or strong wind, to compare erosion exposure.

These are estimates from a simplified model run on past weather. They compare rotations on the same field; they do not predict a future season. Costs are not modelled.

## Inputs

| Input | File (D's pipeline unless noted) | Used for |
|---|---|---|
| NASA POWER daily weather, 1981 to 2025 | `processed/{fid}/weather_daily.csv` | ET0, rain, heat, frost, wind |
| PRISM daily, 1991 to 2025 | `processed/{fid}/prism_daily.csv` | Climate normals vs recent, calendar frost odds |
| SSURGO soil, SRTM terrain, CDL/CSB crop history | `web/fields.json` | Water capacity, runoff group, erodibility, slope, current rotation |
| USDA NASS QuickStats | `processed/nass.json` | Yields, prices, local market check |
| OpenET monthly | `processed/{fid}/openet_monthly.csv` | Validation |
| GRACE, USGS wells | `web/field/{fid}/water.json` | Water outlook |
| Farms Like Yours groups | `web/field/{fid}/neighbors.json` | Neighbour evidence |
| Crop traits | U's `content/crops.yaml` | Kc, stages, roots, p, Ky, heat and frost, residue, families |
| IMERG daily, SMAP L4 daily | `processed/{fid}/precip_imerg_daily.csv`, `smap_l4_daily.csv` | Storm days and validation, read automatically once D delivers them |

At the time of this run, IMERG and SMAP files were not yet delivered, so storm days use POWER rain and the SMAP and IMERG validation items are left out (see [Validation](#validation)).

## Rotation Replay

### Reference ET

Daily reference evapotranspiration uses FAO-56 Penman-Monteith (`pyet.pm_fao56`) from POWER mean, max and min temperature, relative humidity, 2 m wind and solar radiation, with the field's SRTM elevation and latitude ([FAO-56 ch. 2](https://www.fao.org/4/x0490e/x0490e06.htm)). Annual ET0 for 2000 to 2025 comes out at about 1530 to 1540 mm on all three fields, inside the expected 1200 to 1600 mm range for Finney County.

### Season timing

Each rotation step is one dated crop season on a continuous daily timeline (`model/replay/crop_calendar.py`):

- A crop is planted in the middle of its `plant_window`. If the previous crop was harvested too late for that, it is planted `MIN_GAP_DAYS` (5) after harvest when that day is still inside the window; otherwise it waits a year.
- Grain crops grow over the FAO-56 `stage_days` from `crops.yaml`, stretched so the crop matures 14 days (`DRYDOWN_DAYS`) before the middle of `harvest_window`. The mature crop then stands, using only soil evaporation, until harvest. Forage cuts and cover crops end at the middle of `harvest_window`, with stages scaled to fit.
- A `fallow` step leaves the soil bare until 1 July (`FALLOW_END_MMDD`) of the following year, which makes wheat-sorghum-fallow a 3-year cycle with an 11-month fallow before each crop.
- Alfalfa is fall-seeded once (`plant_window` 15 August to 10 September), then each alfalfa step is one production season, from green-up to the end of FAO-56 stage days. Between seasons the stand stays in the ground with Kc 0.40 (`ALFALFA_DORMANT_KC`).
- **Spring triticale in R3.** R3 is "flex fallow": a forage crop grown in the fallow window of wheat-sorghum-fallow. K-State research at Garden City grew spring triticale for forage in that window ([Holman et al. 2022](https://doi.org/10.1002/csc2.20670)). U's `crops.yaml` lists fall-planted triticale, which cannot follow an October sorghum harvest. The replay therefore uses spring timing (`TRITICALE_SPRING`: plant 10 March to 5 April, cut 25 May to 15 June, stages 15/30/20/12 days), with Kc, p, Ky and roots from `crops.yaml`. This is our timing assumption, not a published FAO stage table.

### Kc and roots

Kc follows the FAO-56 piecewise-linear curve: flat at `kc.ini` through the initial stage, linear to `kc.mid` over development, flat through mid season, linear to `kc.end` over late season ([FAO-56 ch. 6](https://www.fao.org/4/x0490e/x0490e0b.htm)). Root depth grows linearly from 0.15 m (`ROOT_INIT_M`) at planting to `root_max_m` at the end of development, capped by the profile depth.

### Daily soil-water bucket

`model/replay/water_balance.py`, one profile of depth `Zmax = min(1.5 m, restrictive depth)`:

- `TAW_profile = awc_mm_per_m × Zmax`, `TAW_root = awc_mm_per_m × Zr`, `RAW = p × TAW_root`.
- The profile is split into the root zone and the soil below it, each with its own depletion. When roots grow they take on the stored water of the soil they reach; when a crop is harvested, the soil below keeps what it stored. This is how fallow rain stored deep reaches the next crop.
- **Runoff:** SCS curve number on daily rain, CN by hydrologic group for row crops, straight row, good condition: A 67, B 78, C 85, D 89; +3 on bare days; dual groups use the drained letter ([NRCS NEH 630 ch. 9](https://directives.nrcs.usda.gov/sites/default/files2/1720460895/Chapter%209%20-%20Hydrologic%20Soil-Cover%20Complexes.pdf)). Initial abstraction 0.2 S.
- **Crop and cover days:** `ETc = Kc × ET0`; `Ks = 1` if `Dr ≤ RAW`, else `(TAW_root − Dr)/(TAW_root − RAW)`; `ETa = Ks × ETc`. A stress day is a cash-crop day with `Ks < 0.8`.
- **Bare days:** evaporation `E = 0.30 × ET0 × f`, with `f = 1` if `Dr < 12 mm`, else `max(0.1, 1 − (Dr − 12)/(0.4 × TAW_profile))`. On bare days the upper layer is a 0.15 m surface evaporation layer (`BARE_EVAP_DEPTH_M`, FAO-56 Ze 0.10 to 0.15 m, [FAO-56 ch. 7](https://www.fao.org/4/x0490e/x0490e0c.htm)): rain wets it first and evaporation draws only from it. We first let evaporation draw on the whole profile. That made fallow nearly 100% efficient: the profile was 85 to 90% full at every sorghum planting whatever came before, so the fallow benefit vanished. The surface layer fixed that (see [Sanity checks](#sanity-checks)).
- **Irrigation** (cash-crop days of irrigated rotations, on fields with a well, cap above dryland): if `Dr > RAW` and the season total plus `I = Dr / 0.85` stays within the cap, apply `I` (pivot efficiency 0.85, refill to field capacity). Caps per crop season: 150, 300, 450 mm. If the full refill would pass the cap, the pivot applies what is left of the cap (when at least 5 mm, `IRR_MIN_EVENT_MM`). The handover rule skipped such a refill entirely; that let hotter weather (bigger refills) end up with less water applied under a cap, so we changed it.
- **Update:** `Dr = Dr − P_eff − 0.85 × I + ETa`. Water above field capacity percolates to the lower layer, then drains out of the profile.
- **Start:** 1999-10-01 at 50% depletion, so 2000 starts warmed up.

### Yield and revenue

Per cash-crop season (`model/replay/economics.py`):

```text
rel_yield    = max(0, 1 − Ky × (1 − ΣETa/ΣETc)) × heat_factor × frost_factor
heat_factor  = max(0.5, 1 − 0.015 × heat_days)
frost_factor = 0.85 if any day with Tmin ≤ frost_kill_c in the frost window, else 1
revenue      = rel_yield × Ym × price          (fallow and rye cover: 0)
```

- `Ky` is the FAO-33 yield response factor ([FAO-33](https://www.fao.org/4/i2800e/i2800e.pdf), FAO-56 Table 24).
- **Heat days** count days with Tmax above the crop's `heat.tmax_c` in the first 21 days (`HEAT_WINDOW_DAYS`) of its `heat.stage`. Corn pollination and silking last about 2 to 3 weeks ([K-State Corn Production Handbook C560](https://bookstore.ksre.ksu.edu/pubs/C560.pdf)). Counting the whole 47-day mid stage gave 20 to 39 heat days a year and cut fully irrigated corn to 58% of the NASS mean, which double-counts heat already in that mean. With the 21-day window, irrigated continuous corn at cap450 averages a relative yield of about 0.7 (f1).
- **Frost window:** from the development stage to maturity for summer crops, from mid season (heading) to maturity for winter crops. Frost thresholds are U's `frost_kill_c`. The final `crops.yaml` sets winter wheat to −18 °C (winter-hardy when dormant), so no wheat frost loss occurs in the replay, even though spring freeze at heading (30 °F, about −1 °C, [K-State freeze damage table](https://sunflower.k-state.edu/agronomy/wheat/freeze_damage.html); [C646](https://bookstore.ksre.ksu.edu/pubs/spring-freeze-injury-to-kansas-wheat_C646.pdf)) is a real risk. A heading-stage threshold would bring that back.
- **Ym** is the NASS yield for the crop and practice: irrigated if the rotation is irrigated, the field has a well and the cap is above dryland; otherwise non-irrigated. We take the most local level (county, then district, then state) with at least 3 values in 2010 to 2024 and average the last 5. If no level has that, we use the most recent 5 values at any level. If the practice has no series, we fall back to "all practices", then to `crops.yaml`. The values used are in `model/out/run_log.json` (`yields`). Alfalfa and cotton have no practice split in NASS, so dryland and irrigated use the same "all practices" yield (5.52 t/ac alfalfa, mostly irrigated stands). Dryland alfalfa (R4) is infeasible in every scenario, but its dryland revenue is optimistic. Most come from the district level (corn, wheat, soybean, alfalfa, cotton), and sorghum by practice only from 2003 to 2007 county data, so most cards show the `county_yields` gap.
- **Price** is the 2020 to 2024 mean Kansas price from NASS: corn 5.28 $/bu, sorghum 5.33 $/bu, wheat 6.51 $/bu, soybean 11.97 $/bu, alfalfa 189.8 $/ton, cotton 0.742 $/lb. Triticale has no NASS price series (`crops.yaml` price is null), so it uses the NASS Kansas alfalfa hay price, 2020 to 2024 mean, 189.8 $/ton (logged as `proxy: alfalfa` in `model/out/run_log.json`). Triticale forage usually sells below alfalfa hay, so R3 income is likely overstated. R3 cards carry the `prices_constant` gap, and the `county_yields` gap because triticale yields come from `crops.yaml` (K-State MF2227), not county NASS data. They also carry the `buyer_availability` risk, because NASS shows no Finney County triticale acres.
- Triticale yields come from `crops.yaml` (1.5 t/ac dryland, 3.0 t/ac irrigated, K-State [MF2227](https://bookstore.ksre.ksu.edu/pubs/mf2227.pdf)).

### Exposure and erosion indices

Daily, then summed per calendar year (`model/replay/exposure.py`):

- A bare day has no crop, standing crop or cover in the ground.
- Cover multiplier: 1.0 on bare days, × residue factor for 120 days after each harvest or cover termination (high 0.5, medium 0.7, low 0.9).
- Bare storm day: bare day with rain ≥ 12.7 mm (IMERG when delivered, POWER until then).
- Bare windy day: bare day with POWER `ws10m_max` ≥ 11 m/s (about 25 mph).
- `water_erosion_idx = Σ storm days × multiplier × rain/25.4 × K × S`, `S = 10.8 sin(atan(slope)) + 0.03`, with SSURGO K factor and the SSURGO map-unit slope (SRTM 30 m slope is noisy on these flat fields: it reads 9.3% on f2, a 0 to 1% slope soil). The slope factor scales every rotation on a field equally, so it does not change scores.
- `wind_erosion_idx = Σ windy days × multiplier × WEI/310` (310 t/ac/yr is the WEG 1 maximum).

These are relative indices for comparing rotations on the same field. They are not tons of soil.

### Phases and scenarios

A rotation with L steps is run L times, each starting at a different step, and the results are averaged per calendar year. This represents a farm running every phase of the rotation at once, so every crop meets every year's weather. `crop_mix` is the share of phases with each crop harvested that year.

- 8 scenarios: 4 caps (dryland, 150, 300, 450 mm per season) × 2 climates. `hotdry` adds 1.5 °C to Tmax, Tmin and Tmean, multiplies rain by 0.85, and recomputes ET0 with observed humidity and wind.
- Feasibility: a rotation is infeasible below its `min_cap` (R1 cap150, R4 cap300, R5 cap150, R0 cap150 on irrigated fields, others dryland). f2 has no well (`irrigated: false`), so it gets no irrigation in any scenario, and every rotation needing water is infeasible there. Infeasible runs are still computed and written with `feasible: false`.
- R5 needs a well (`min_cap: cap150`) because corn-soybean in Finney County is mostly irrigated: NASS reports 14,000 irrigated vs 3,000 dryland soybean acres in 2001, and dryland soybean averages about 19 bu/ac in the district.
- Drought years: Jun to Aug rain in the lowest 20% and Jun to Aug ET0 in the highest 30% of 2000 to 2025, plus any year D lists with summer NDVI anomaly ≤ −10%. Result for all three fields: 2002, 2011, 2012, 2022. The worst (largest Jun to Aug ET0 minus rain) is 2012, used for `replay_drought` evidence.

### Sanity checks

All are pytest tests in [model/tests/test_replay_sanity.py](../model/tests/test_replay_sanity.py) and pass on D's real data for f1, f2 and f3.

| Check | Result |
|---|---|
| Annual ET0 1200 to 1600 mm | about 1530 to 1540 mm on every field |
| Irrigated continuous corn at cap450: 250 to 500 mm/yr | f1 438 mm, f3 431 mm (f2 tested with a well added) |
| `hotdry` applies at least as much irrigation as actual weather at every cap | passes for every irrigated rotation at cap150, cap300, cap450 |
| Dryland W-S-F sorghum beats sorghum planted straight after wheat harvest (no fallow) | relative yield f1 0.63 vs 0.55, f2 0.68 vs 0.55, f3 0.55 vs 0.52 |
| W-S-F sorghum beats continuous sorghum | f1 0.63 vs 0.59, f2 0.68 vs 0.60, f3 0.55 vs 0.54 |
| `hotdry` raises irrigation need (uncapped) and lowers dryland relative yield for every rotation | passes for R0 to R6 on all fields |
| Water mass balance closes within the profile capacity | passes |

On the sand field (f3, 105 mm of water in 1.5 m) fallow stores little, so its fallow advantage is small. The test asks for at least 0.05 on soils with AWC ≥ 100 mm/m and 0.02 on sand.

The handover check reads "sorghum after fallow beats sorghum after wheat". In W-S-F the sorghum follows wheat after an 11-month stubble fallow, so we test fallow-stored water against no fallow (double-cropped sorghum, and continuous sorghum). A 20-month fallow scores almost the same as the 11-month one, because the profile is nearly refilled either way.

Under cap150 and cap300 nearly every irrigated rotation uses its whole cap in both climates (f1 continuous corn: 299 vs 300 mm/yr at cap300), so the `hotdry` penalty shows up as lower yield and revenue, not more water. At cap450, `hotdry` uses 5 to 22 mm/yr more.

## Field Calendar

`model/calendar/build.py`, from 2000 to 2025 daily weather:

- `p_heat[m]`: share of years with ≥ 3 days Tmax ≥ 35 °C in month m.
- `p_frost[m]`: share of years with any day Tmin ≤ −2 °C (PRISM Tmin where available).
- `p_dry_spell[m]`: share of years where a run of ≥ 21 days with < 2 mm/day overlaps month m.
- `storm_days[m]`, `windy_days[m]`: mean days with rain ≥ 12.7 mm, and with `ws10m_max` ≥ 11 m/s.

Each rotation's calendar uses phase 0. The cycle length in years comes from the timeline itself (the shortest period after which the yearly pattern repeats), and year 1 is the first year the rotation's first crop is harvested. A month's `state` is the crop in the ground for most of the month, else `bare`. Its `stage` is the most common FAO stage that month (`late` for a mature standing crop, `null` for a dormant stand). Flags use a 0.3 probability threshold (`CAL_FLAG_P`): `heat` when the crop's heat stage overlaps the month, `frost` when a crop is in the ground (except winter, cover and perennial crops from November to February), `dry` when a crop is in the ground, `bare_storm` when bare with ≥ 1 storm day, and `bare_wind` when bare with ≥ 2 windy days.

## Criteria and normalisation

`model/scoring/criteria.py`, per field × scenario × rotation:

| Criterion | Raw value | Better |
|---|---|---|
| `water_use` | mean irrigation mm/yr | lower |
| `income_mean` | mean revenue $/ac/yr | higher |
| `income_worst` | mean of the 5 worst years' revenue | higher |
| `soil_health` | index 0 to 100 (below) | higher |
| `water_erosion` | water erosion index | lower |
| `wind_erosion` | wind erosion index | lower |
| `pest_break` | longest run of the same `host_group` in the cycled sequence, cap 8 (fallow breaks a run; covers are not counted) | lower |
| `heat_frost_risk` | heat days/yr + 2 × frost events/26 | lower |

Soil health index: `40 × living_root_days/365 + 20 × residue_score + 15 × legume_share + 15 × min(1, families/4) + 10 × (1 − bare_days/365)`. Living-root days count days with a growing crop, cover or alfalfa stand. `residue_score` is the mean over cycle steps of high 1, medium 0.6, low 0.2, with fallow scored 0 because it produces no residue. `legume_share` is the share of steps with an `n_fixing` crop. Families are distinct botanical families among crops and covers. Sorghum and corn are separate pest host groups, as U's `crops.yaml` decides, so corn followed by sorghum counts as a full break. That fits corn rootworm, which does not complete its life cycle on sorghum. The two share some aphids and armyworms, so the break is partial for those pests; we found no sourced way to weight that and kept the yaml's choice. Wheat, triticale and rye share `small_grain`.

Normalisation within one field and scenario, across feasible rotations: `norm = 100 × (raw − worst)/(best − worst)`, inverted for lower-is-better, 50 when best equals worst. Infeasible rotations get the norm they would have had (clamped to 0 to 100).

## Card facts

`model/scoring/facts.py` writes `strategies.json` using only README 8.6 keys:

- Benefits vs R0: `water_saved` (≥ 25 mm), `bare_days_reduced` (≥ 20 days), `legume_added`, `income_steadier` (worst-5 ≥ $10/ac better), `pest_cycle_broken`, `forage_income`.
- Evidence: `replay_avg` always; `replay_drought` for 2012; `neighbors` when D's matching group (or, for R0, the `is_current` group) has n ≥ 3 and both groups have an OpenET median; `validation_et` when `et_vs_openet` exists.
- Gaps: always `model_simplified`, `costs_not_modelled`, `prices_constant`, `crop_params_generic`; `no_pest_data` when pest break is one of the card's 3 "why" criteria under default weights; `county_yields` when any crop's yield is not county data for its practice; `openet_record_short` and `neighbors_observational` with that evidence.
- Risks by rule: wheat→sorghum `herbicide_carryover`; crops with no county acres or yields (triticale, cotton) `buyer_availability`; new crops `seed_availability` and `crop_insurance` (not for a cover alone), cotton `new_crop_learning`; alfalfa `alfalfa_stand_water`; fallow `fallow_wind`; rye cover `cover_establishment`; irrigated rotations `water_rights`; equipment `equipment_access`.
- `infeasible_reason_id`: `needs_more_water` when infeasible.
- Confidence: `good` if ET validation is good and neighbour evidence exists, `fair` if one of them, else `limited`.

## Summary

`model/scoring/summary.py`. Climate normal (1991 to 2020) and recent (2016 to 2025) use PRISM temperatures and rain, and POWER ET0: frost-free days and median last spring and first fall frost (Tmin ≤ 0 °C), GDD base 10 °C capped at 30 °C (April to October), annual rain, days with Tmax ≥ 35 °C. Water: D's GRACE trend and the median of the nearby wells' depth-to-water trends (positive means the water table is falling). Outlook is `declining` if GRACE < −0.3 cm/yr or wells > 0.1 m/yr. All three fields are declining (GRACE −0.86 cm/yr; wells +0.25 to +1.8 m/yr). The second headline is the larger in size of the frost-free and heat-day changes: f1 −3 heat days, f2 +3 frost-free days, f3 −2 heat days.

## Validation

`model/validate/run.py`. The model side is R0 run on each field's actual CDL crop sequence (2018 to 2025, the years D provides), with full irrigation (cap450) on fields with a well, not phase-averaged.

| Field | Item | Result | Level |
|---|---|---|---|
| f1 | Model ETa vs OpenET, Apr to Oct months 2018 to 2025 (n 56) | bias −1.9%, r² 0.79 | good |
| f2 | same | bias −29.6%, r² 0.34 | fair |
| f3 | same | bias +4.7%, r² 0.57 | fair |

Level rules: ET good if |bias| ≤ 15% and r² ≥ 0.6, fair if |bias| ≤ 30%; precipitation good if |bias| ≤ 10% and r ≥ 0.8, fair if |bias| ≤ 20%; SMAP good if r ≥ 0.6, fair if r ≥ 0.4.

The dryland field f2 under-predicts ET by about 30%. Likely causes: fallow-year evaporation from a 0.15 m layer is too low next to what OpenET sees (weeds, volunteer wheat, residue), and the actual-history run starts from a bare 2017.

Not computed yet, because D has not delivered the inputs: `sm_vs_smap` (no SMAP L4 file) and `precip_power_vs_imerg` (no IMERG file; `observed.json` `imerg_mm` is all null). `precip_vs_cocorahs` needs gauge data D has not provided. These items are left out of `validation.json` rather than filled with placeholder numbers. They appear automatically when the files land and `model/run_all.py` is rerun.

Extra check, not a contract item: POWER monthly rain vs PRISM, 2000 to 2025 (n 312): POWER is 15% (f1), 12% (f2) and 12% (f3) wetter, r 0.92 to 0.93. The replay runs on POWER rain, so dryland yields and fallow storage may be a little optimistic.

## Results under default settings

The README 8.7 default is all sliders at 3, with no hay or cotton equipment and no forage buyer, so R3, R4 and R6 are excluded. Top 3 (excluding R0) at `cap300|actual`:

| Field | R0 | Top 3 | Why |
|---|---|---|---|
| f1 irrigated pivot | continuous corn | R5, R1, R2 | R5 adds soybean and a rye cover (legume, 245 living-root days vs 147, half the wind exposure). R1 breaks the 8-year corn run. R2 saves all of the 299 mm of irrigation. Continuous corn keeps the highest mean income ($669/ac). |
| f2 dryland | wheat-sorghum-fallow | R2 only | No well, so R1, R4 and R5 are infeasible, and R3 and R6 need hay or cotton equipment. R2 is the same sequence as R0. With hay equipment and a forage buyer, R3 (flex fallow) ranks first. |
| f3 sandy | corn-wheat-sorghum | R5, R1, R2 | R5 halves wind-erosion exposure on this WEG 1 sand. R1 is the same sequence as R0. |

Under `dryland`, no irrigated rotation is feasible on any field (tested).

## Known simplifications

- One soil profile per field, from the dominant SSURGO component.
- A bucket model with daily time steps; no capillary rise, no salinity, no nitrogen.
- Irrigation refills to field capacity in one event, then tops up to the cap; real pivots apply about 25 mm per pass.
- Yields scale a NASS mean by water, heat and frost factors; no cultivar, planting-date or management effects. Heat and frost factors are working values (`crops.yaml` marks them `# verify`).
- Prices are constant 2020 to 2024 means; there are no costs, so income is gross revenue.
- Erosion indices are relative and not calibrated to RUSLE2 or WEPS.
- Crop history covers 2018 to 2025 only, which limits R0 detection and validation.
- R0 can equal a library rotation (f2 R0 = R2, f3 R0 = R1). The two then score the same.

## Constants (model/config.py)

| Constant | Value | Source or reason |
|---|---|---|
| `YEAR_FROM`, `YEAR_TO` | 2000, 2025 | README replay period |
| `SPINUP_START`, `SPINUP_DEPLETION_FRAC` | 1999-10-01, 0.5 | handover 5.3 |
| `CAP_MM` | 0, 150, 300, 450 mm/season | README 7.2 |
| `HOTDRY_DT_C`, `HOTDRY_P_FACTOR` | +1.5 °C, 0.85 | README 7.2 |
| `ZMAX_M` | 1.5 m | handover 5.3 |
| `ROOT_INIT_M` | 0.15 m | handover 5.3 |
| `PIVOT_EFFICIENCY` | 0.85 | handover 5.3 |
| `IRR_MIN_EVENT_MM` | 5 mm | model rule: smallest top-up applied at the cap |
| `STRESS_KS` | 0.8 | handover 5.3 |
| `BARE_KE`, `BARE_STAGE1_MM`, `BARE_DECAY_FRAC`, `BARE_F_MIN` | 0.30, 12 mm, 0.4, 0.1 | handover 5.3 |
| `BARE_EVAP_DEPTH_M` | 0.15 m | [FAO-56 ch. 7](https://www.fao.org/4/x0490e/x0490e0c.htm) Ze 0.10 to 0.15 m |
| `CN_BY_HYDGRP`, `CN_BARE_ADD`, `CN_IA_RATIO` | A 67, B 78, C 85, D 89; +3; 0.2 | [NRCS NEH 630 ch. 9](https://directives.nrcs.usda.gov/sites/default/files2/1720460895/Chapter%209%20-%20Hydrologic%20Soil-Cover%20Complexes.pdf) |
| `MIN_GAP_DAYS` | 5 | model assumption |
| `DRYDOWN_DAYS` (crop_calendar.py) | 14 | model assumption |
| `FALLOW_END_MMDD` | 07-01 | model assumption (wheat planting follows in September) |
| `ALFALFA_DORMANT_KC` | 0.40 | FAO-56 Table 12 alfalfa Kc ini ([link](https://www.fao.org/4/x0490e/x0490e0b.htm)) |
| `TRITICALE_SPRING` | plant 03-10 to 04-05, cut 05-25 to 06-15, stages 15/30/20/12 | timing from [Holman et al. 2022](https://doi.org/10.1002/csc2.20670); stage split is a model assumption |
| `HEAT_LOSS_PER_DAY`, `HEAT_FACTOR_MIN` | 0.015, 0.5 | handover 5.3 |
| `HEAT_WINDOW_DAYS` | 21 | [K-State C560](https://bookstore.ksre.ksu.edu/pubs/C560.pdf) pollination 2 to 3 weeks |
| `FROST_FACTOR` | 0.85 | handover 5.3 |
| `NASS_RECENT_FROM/TO`, `NASS_N_YEARS`, `NASS_MIN_VALUES` | 2010 to 2024, 5, 3 | model rule (handover asks for 2020 to 2024; D's series rarely reach that by practice) |
| `PRICE_YEARS` | 2020 to 2024 | handover 5.1 |
| `RESIDUE_FACTOR`, `RESIDUE_DAYS` | 0.5 / 0.7 / 0.9, 120 days | handover 5.3 |
| `STORM_MM`, `WINDY_MS`, `WEI_MAX` | 12.7 mm, 11 m/s, 310 t/ac/yr | handover 5.3 |
| `DROUGHT_P_QUANTILE`, `DROUGHT_ET0_QUANTILE`, `DROUGHT_NDVI_ANOM_PCT` | 0.20, 0.70, −10% | handover 5.3 |
| `CAL_HEAT_TMAX`, `CAL_HEAT_MIN_DAYS`, `CAL_FROST_TMIN`, `CAL_DRY_RUN_DAYS`, `CAL_DRY_MM`, `CAL_FLAG_P`, `CAL_STORM_DAYS`, `CAL_WINDY_DAYS` | 35 °C, 3, −2 °C, 21, 2 mm, 0.3, 1, 2 | handover 5.4 |
| `SOIL_W`, `RESIDUE_SCORE`, `FAMILIES_FULL` | 40/20/15/15/10; 1 / 0.6 / 0.2 / 0; 4 | handover 5.5 (fallow 0 is ours) |
| `PEST_RUN_CAP`, `FROST_WEIGHT` | 8, 2 | handover 5.5 |
| `BENEFIT_WATER_MM`, `BENEFIT_BARE_DAYS`, `BENEFIT_WORST5_USD`, `NEIGHBOR_MIN_N` | 25 mm, 20 days, $10/ac, 3 | handover 5.5 |
| `SLIDER_DEFAULT`, `SLIDER_SHARES` | 3 each; README 8.7 shares | README 8.7, web handover 4 (used only for the acceptance check) |
| `NORMAL_PERIOD`, `RECENT_PERIOD`, `FROST_C`, `GDD_BASE_C`, `GDD_CAP_C`, `HOT_DAY_C` | 1991 to 2020, 2016 to 2025, 0 °C, 10 °C, 30 °C, 35 °C | handover 5.6 |
| `OUTLOOK_GRACE_CM`, `OUTLOOK_WELL_M` | 0.3 cm/yr, 0.1 m/yr | handover 5.6 |
| `VALID_YEARS`, `VALID_MONTHS`, `ACTUAL_RUN_CAP`, `SMAP_YEARS`, `LEVELS` | 2016 to 2025 (clipped to crop history), Apr to Oct, cap450, 2015 to 2025, see Validation | handover 5.7 |

Crop parameters (Kc, stage days, roots, p, Ky, windows, heat and frost) come from U's [content/crops.yaml](../content/crops.yaml), which cites FAO-56 Tables 11, 12, 22 and 24, FAO-33, and K-State L818 and MF2227 for each value.
