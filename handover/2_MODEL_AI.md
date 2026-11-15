# Handover 2 · Modeller + AI (M)

You are building the **models, scoring facts and AI assistant data** for Team Brackets' crop-rotation decision tool (NASA Space Apps 2026, "Adapting Farms with NASA Data"). Read the root [README.md](../README.md) first. It is the shared contract. §7 (IDs, conventions, placeholder formatting) and §8–§9 (data contract, assistant API) define exactly what you must produce. If this file and the README disagree, the README wins.

## 1. Your mission

Turn D's data and U's crop research into everything the app shows as numbers:

- **Rotation Replay:** a daily FAO-56 soil-water budget run for every rotation × water cap × climate scenario, 2000–2025.
- **Field Calendar data:** monthly climate-risk odds and crop/bare state per rotation year.
- **Scoring facts:** per-rotation criteria (raw + normalised), card facts (benefits, evidence, gaps, risks).
- **Validation:** model vs OpenET, model vs SMAP, POWER vs IMERG.
- **Assistant data:** the system prompt, per-field fact lists, cached answers to the 6 suggested questions.
- **Integration scripts:** `scripts/sync_data.py` and `scripts/check_contract.py`.
- **Docs:** `docs/METHODS.md`, `docs/AI_USE.md`.

You write **no farmer-facing sentences** except the assistant's facts (`Fact.text`) and the system prompt. Everything else is a `text_id` + `vars` that U's templates turn into words (README §5, §8.6).

## 2. What you own and must not touch

- **You own:** `model/**`, `scripts/**`, `docs/METHODS.md`, `docs/AI_USE.md`.
- **Don't edit:** `data-pipeline/`, `web/`, `content/`, `design/`, `README.md`. If the contract must change, agree it with the team first.

## 3. Folder layout to create

```text
model/
├─ README.md
├─ requirements.txt           # pandas numpy pyet pyyaml python-dotenv openai tqdm
├─ .env.example               # DATA_DIR, CONTENT_DIR, LLM_BASE_URL, LLM_MODEL, LLM_API_KEY, LLM_PROVIDER
├─ config.py                  # paths, years, scenarios, thresholds (every tunable constant lives here)
├─ run_all.py                 # library → replay → calendar → scoring → validation → summary → assistant
├─ library/
│  ├─ load_crops.py           # content/crops.yaml → dataclasses; writes out/web/crops.json
│  └─ rotations.py            # R1–R6 definitions; writes out/web/rotations.json; builds R0 per field
├─ replay/
│  ├─ et0.py                  # FAO-56 Penman–Monteith via pyet
│  ├─ crop_calendar.py        # planting dates, stage lengths, daily Kc and root depth
│  ├─ water_balance.py        # the daily bucket
│  ├─ economics.py            # yield + revenue
│  ├─ exposure.py             # bare days, storm/wind exposure, erosion indices
│  └─ run.py                  # all fields × rotations × scenarios × phases → out/web/field/{fid}/replay.json
├─ calendar/build.py          # → calendar.json
├─ scoring/
│  ├─ criteria.py             # raw criteria + normalisation
│  ├─ facts.py                # benefits, evidence, gaps, risks → strategies.json
│  └─ summary.py              # → summary.json
├─ validate/run.py            # → validation.json
├─ assistant/
│  ├─ prompt.md               # system prompt source → out/web/assistant/prompt.json
│  ├─ context.py              # → assistant_context.json
│  ├─ number_check.py         # Python port of README §9 number check
│  └─ cache.py                # calls the LLM for q1–q6 × en/es → assistant_cache.json
├─ mock/make_mocks.py         # writes schema-correct mock JSON for every M file (mock: true)
├─ mock_inputs/               # synthetic stand-ins for D's processed files until real ones land
└─ out/web/                   # committed; synced into web/public/data
scripts/
├─ sync_data.py
└─ check_contract.py
```

Read inputs through `config.DATA_DIR` (default `../data-pipeline/out`) and `config.CONTENT_DIR` (default `../content`), so you can point at `mock_inputs/` while D is still working.

## 4. Inputs you depend on

| From | File | Used for | Until it arrives |
|---|---|---|---|
| D | `out/processed/{fid}/weather_daily.csv` | ET0, rain, heat, frost, wind | Synthetic weather in `mock_inputs/` (seasonal sine + noise, realistic ranges) |
| D | `out/web/fields.json` | Soil (AWC, K, WEG/WEI, hydgrp, slope), crop history, detected rotation | Hand-written soil for 3 fake fields |
| D | `out/processed/nass.json` | Yields, prices, county acres | Defaults from `crops.yaml` |
| D | `out/processed/{fid}/precip_imerg_daily.csv` | Storm days, rain cross-check | Use POWER precip |
| D | `out/processed/{fid}/prism_daily.csv` | Climate normals vs recent, frost dates | Use POWER temps |
| D | `out/processed/{fid}/openet_monthly.csv`, `smap_l4_daily.csv` | Validation | Skip validation items (mark `limited`) |
| D | `out/web/field/{fid}/neighbors.json`, `water.json` | Evidence (neighbours), summary (water outlook) | Omit neighbour evidence |
| U | `content/crops.yaml` | All crop parameters | Use the starter values in §5.1 |
| U | `content/assistant_questions.json`, `glossary.json` | Cache generation, context | Write placeholder questions locally (don't commit to `content/`) |

## 5. Build steps

### 5.0 Mocks first

Before anything else, run `mock/make_mocks.py` to write every file you own (README §8.4) for `f1`–`f3` with `"_meta": {"mock": true, ...}`, correct keys, all 8 scenarios, R0–R5, plausible fake numbers, and `text_id`s that exist in the README §8.6 catalog. Commit and merge so F can build against them. Replace with real output field by field.

### 5.1 Crop library (`library/load_crops.py`)

Load `content/crops.yaml` (schema in README §8.5). Validate every crop has every field; fill `null` yields and prices from `nass.json` (5-year mean 2020–2024 of Finney county or district values, by practice) and fall back to the yaml defaults. Write `out/web/crops.json`.

**Starter values while U researches** (approximate FAO-56 / FAO-33 table values; U confirms and adds Kansas planting windows and stage lengths):

| Crop | Kc ini / mid / end | Max root (m) | p | Ky | Heat stage / Tmax °C |
|---|---|---|---|---|---|
| corn | 0.30 / 1.20 / 0.35 | 1.5 | 0.55 | 1.25 | mid / 35 |
| sorghum | 0.30 / 1.05 / 0.55 | 1.5 | 0.55 | 0.90 | mid / 38 |
| wheat (winter) | 0.40 / 1.15 / 0.30 | 1.5 | 0.55 | 1.00 | late / 32 |
| soybean | 0.40 / 1.15 / 0.50 | 1.0 | 0.50 | 0.85 | mid / 35 |
| alfalfa | 0.40 / 0.95 / 0.90 | 1.5 | 0.55 | 1.10 | — |
| cotton | 0.35 / 1.15 / 0.60 | 1.4 | 0.65 | 0.85 | mid / 38 |
| triticale (forage) | 0.40 / 1.10 / 0.40 | 1.2 | 0.55 | 1.00 | — |
| rye_cover | 0.40 / 1.00 / 0.40 | 1.0 | 0.55 | — | — |
| fallow / bare | 0.30 constant (soil evaporation, see §5.3) | — | — | — | — |

### 5.2 Rotations (`library/rotations.py`)

Hard-code R1–R6 exactly as README §7.2. For each: `steps`, `irrigated`, `min_cap`, `requires_equipment` (R4 → `["hay"]`, R6 → `["cotton"]`, R3 → `["hay"]` if triticale is cut for hay), `needs_forage_market` (R3, R4 → true), `tier`. Suggested `min_cap`: R1 `cap150`, R4 `cap300`, others `dryland`. Write `out/web/rotations.json`.

**R0 per field:** from `fields.json` `detected.sequence` → steps. Store it in `summary.json` `current_rotation`.

**Season timing:** each step is one crop season in the cycle. A winter wheat step is planted in late September/October of year *Y* and harvested in late June of *Y+1*; the next summer crop is planted in spring of *Y+2* (that gap is the fallow/bare window). Implement steps as dated seasons on a continuous daily timeline using `plant_window` / `harvest_window` (middle of each window), so carry-over soil water and bare periods come out naturally.

### 5.3 Rotation Replay engine (`replay/`)

**ET0** (`et0.py`): FAO-56 Penman–Monteith with `pyet.pm_fao56` from `tmean_c, tmax_c, tmin_c, rh_pct, ws2m_ms, rs_mj_m2`, plus elevation (from `fields.json` terrain) and latitude. Check: Finney annual ET0 should come out roughly 1200–1600 mm.

**Kc and roots** (`crop_calendar.py`): standard FAO-56 piecewise-linear Kc curve over `stage_days` (ini flat at `kc.ini`, dev linear to `kc.mid`, mid flat, late linear to `kc.end`). Root depth grows linearly from 0.15 m at planting to `root_max_m` at the end of dev, capped by `restrictive_depth_cm`.

**Daily bucket** (`water_balance.py`), one profile of depth `Zmax = min(1.5 m, restrictive depth)`:

```text
TAW_profile = awc_mm_per_m × Zmax                          # capacity of the whole profile (mm)
TAW_root    = awc_mm_per_m × Zr(day)                       # what roots can reach
RAW         = p × TAW_root
Dr          = depletion of the root zone (mm, 0 = field capacity)

Runoff      = SCS curve number on daily rain P
              CN by hydgrp (row crop, straight row, good): A 67 · B 78 · C 85 · D 89
              bare/fallow: +3 · dual groups (e.g. B/D): use the drained letter
P_eff       = P − Runoff

Crop days:
  ETc = Kc × ET0
  Ks  = 1                                 if Dr ≤ RAW
      = (TAW_root − Dr) / (TAW_root − RAW) otherwise (floor 0)
  ETa = Ks × ETc
  stress day if Ks < 0.8

Bare / fallow days (no crop, no cover):
  E   = 0.30 × ET0 × f,  f = 1 if Dr < 12 mm, else max(0.1, 1 − (Dr − 12) / (0.4 × TAW_profile))
  ETa = E                                  (draws from the profile; fallow stores water for the next crop)

Irrigation (only on crop days of irrigated rotations, only if cap ≠ dryland):
  if Dr > RAW and season_irrigation + I ≤ cap_mm:
      I = Dr / 0.85                        # pivot efficiency 0.85; applied amount, refill to field capacity
      season_irrigation += I
  cap_mm: cap150 = 150 · cap300 = 300 · cap450 = 450 (per crop season)

Update:
  Dr = Dr − P_eff − 0.85 × I + ETa
  if Dr < 0: deep drainage = −Dr; Dr = 0
  if Dr > TAW_profile: Dr = TAW_profile
  When roots grow, newly reached soil brings its own stored water (track the profile, not just the root zone).
```

Start every run on 1999-10-01 at 50% depletion so 2000 starts warmed up.

**Yield and revenue** (`economics.py`), per crop season:

```text
rel_yield = max(0, 1 − Ky × (1 − ΣETa / ΣETc)) × heat_factor × frost_factor
heat_factor  = max(0.5, 1 − 0.015 × heat_days)   # heat_days = days with Tmax > heat.tmax_c during heat.stage
frost_factor = 0.85 if any day with Tmin ≤ frost_kill_c between emergence and maturity, else 1
Ym = NASS 5-year mean yield for that crop and practice (irrigated if the rotation is irrigated, else non-irrigated)
revenue_usd_ac = rel_yield × Ym × price       # constant 5-year mean price, no costs (that's a listed gap)
fallow, rye_cover: revenue 0
```

All factors and thresholds live in `config.py`. List them in `docs/METHODS.md`.

**Exposure and erosion** (`exposure.py`), daily, then summed per calendar year:

```text
bare day         = no crop and no cover in the ground
cover multiplier = 1.0 on bare days, × residue factor for 120 days after harvest:
                   residue high 0.5 · medium 0.7 · low 0.9
bare_storm_day   = bare day with rain ≥ 12.7 mm (0.5 in)   (IMERG if available, else POWER)
bare_windy_day   = bare day with ws10m_max_ms ≥ 11 (≈ 25 mph)
water_erosion_idx = Σ bare_storm_days × cover multiplier × rain_mm/25.4 × k_factor × S
                    S = 10.8 × sin(atan(slope_pct/100)) + 0.03
wind_erosion_idx  = Σ bare_windy_days × cover multiplier × (wei_t_ac_yr / 310)   # 310 = WEG 1 maximum
```

These are **relative indices** for comparing rotations on the same field, not tons of soil. Say so in METHODS.md.

**Phases and scenarios** (`run.py`):

- For a rotation with *L* steps, run *L* times, each starting at a different step, and average the results per calendar year. `crop_mix` is the share of phases in each crop that year. This represents "a farm running every phase of the rotation at once", and every crop meets every year's weather. Say this on the chart (F) and in METHODS.md.
- Scenarios: 4 caps × 2 climates. `hotdry` = Tmax, Tmin, Tmean + 1.5 °C and P × 0.85, then recompute ET0 (keep RH and wind).
- Infeasible combinations (cap below `min_cap`): still run them, set `feasible: false`. Fill the summary anyway.
- `drought_years`: years where Jun–Aug P is in the lowest 20% and Jun–Aug ET0 is in the highest 30% of 2000–2025, plus any year D listed in `observed.json drought_years` with NDVI anomaly ≤ −10%.
- Output `replay.json` exactly as README §8.4. Round per README §7.1.

**Sanity checks (stop and debug if these fail):**
- Irrigated continuous corn in Finney: a few hundred mm of irrigation a year (roughly 250–500 with `cap450`). If you get ~50 or ~1500, it's a units bug (radiation, mm vs m, AWC cm/cm).
- Dryland wheat–sorghum–fallow: sorghum rel_yield should be clearly better after fallow than after wheat.
- `hotdry` raises irrigation need and lowers dryland yields for every rotation.

### 5.4 Calendar (`calendar/build.py`)

From 2000–2025 daily weather:

- `p_heat[m]`: share of years with ≥ 3 days Tmax ≥ 35 °C in month *m*.
- `p_frost[m]`: share of years with any day Tmin ≤ −2 °C in *m* (use PRISM if available).
- `p_dry_spell[m]`: share of years with a run of ≥ 21 days with < 2 mm/day rain that overlaps *m*.
- `storm_days[m]`: mean days with rain ≥ 12.7 mm. `windy_days[m]`: mean days with ws10m_max ≥ 11 m/s.

Per rotation (R0–R5, R6 if done), using phase 0 and the season timing from §5.2: for each rotation year and month, `state` = the crop in the ground for most of the month (or `bare`), `stage` = its FAO stage, and `flags`:

- `heat` if the crop's heat stage overlaps the month and `p_heat ≥ 0.3`
- `frost` if a crop is in the ground (not dormant winter wheat) and `p_frost ≥ 0.3`
- `dry` if a crop is in the ground and `p_dry_spell ≥ 0.3`
- `bare_storm` if `bare` and `storm_days ≥ 1`
- `bare_wind` if `bare` and `windy_days ≥ 2`

Thresholds live in `config.py`.

### 5.5 Criteria, normalisation and card facts (`scoring/`)

Per field × scenario × rotation, from the replay summary:

| Criterion | raw | Better is | Vars (README §8.6) |
|---|---|---|---|
| `water_use` | `irrigation_mm_mean` | lower | `irrigation_mm`, `saved_mm` = R0 − this |
| `income_mean` | `revenue_usd_ac_mean` | higher | `revenue_usd_ac`, `diff_usd_ac` |
| `income_worst` | `revenue_usd_ac_worst5` | higher | `worst5_usd_ac`, `r0_worst5_usd_ac` |
| `soil_health` | index 0–100 (below) | higher | `score`, `living_root_days`, `legume_years` |
| `water_erosion` | `water_erosion_idx` | lower | `bare_storm_days`, `r0_bare_storm_days` |
| `wind_erosion` | `wind_erosion_idx` | lower | `bare_windy_days`, `r0_bare_windy_days` |
| `pest_break` | longest run of the same `host_group` in the cycled sequence (cap 8) | lower | `max_run_years`, `r0_max_run_years` |
| `heat_frost_risk` | `heat_days_mean + 2 × frost_events_total / 26` | lower | `heat_days`, `r0_heat_days` |

**Soil health index** (document it):
`40 × living_root_days/365 + 20 × residue_score + 15 × legume_share + 15 × min(1, families/4) + 10 × (1 − bare_days/365)`, where `residue_score` is the mean of high 1 / medium 0.6 / low 0.2 over the cycle and `legume_share` is the share of cycle years with an `n_fixing` crop.

**Normalisation:** within one field and scenario, across all feasible rotations: `norm = 100 × (raw − worst) / (best − worst)`, inverted for "lower is better". If best = worst, `norm = 50`. Infeasible rotations get the norm they would have had but `feasible: false`.

**Card facts** (`facts.py`):

- `benefits` (only when true vs R0): `water_saved` if saved_mm ≥ 25 · `bare_days_reduced` if ≥ 20 fewer bare days · `legume_added` if legume years > R0 · `income_steadier` if worst5 is ≥ $10/ac better · `pest_cycle_broken` if max run < R0's · `forage_income` if a forage crop is in the sequence.
- `evidence`: always `replay_avg`; `replay_drought` for the worst drought year; `neighbors` when D's group with `matches_rotation === rotation_id` has n ≥ 3 (use the `is_current` group for `r0_et_mm`); `validation_et` when `et_vs_openet` exists. Each with `sources` (e.g. `["MODEL","POWER","SSURGO"]`, `["OpenET","CSB"]`).
- `gap_ids`: always `model_simplified`, `costs_not_modelled`, `prices_constant`, `no_pest_data` (if `pest_break` drove the score); `crop_params_generic`; add `county_yields` if any yield came from district/state; `openet_record_short` and `neighbors_observational` when that evidence is shown; `smap_coarse` when SMAP validation is cited.
- `risk_ids` by rule: wheat→sorghum transitions: `herbicide_carryover`; any crop with no county acres: `buyer_availability` + set `crops_without_local_market`; new crops (not in R0): `seed_availability`, `new_crop_learning` (cotton), `crop_insurance`; alfalfa: `alfalfa_stand_water`; fallow: `fallow_wind`; rye_cover: `cover_establishment`; irrigated rotations: `water_rights`; equipment needs: `equipment_access`.
- `infeasible_reason_id`: `needs_more_water` (cap < min_cap), else `null` (equipment and market filtering happens in the browser).
- `confidence`: `good` if validation `et_vs_openet` level is good and neighbour evidence exists; `fair` if one of them; else `limited`.

Write `strategies.json` (README §8.4).

### 5.6 Summary (`scoring/summary.py`)

- `climate.normal` from PRISM 1991–2020, `climate.recent` from PRISM (or POWER) 2016–2025: frost-free days, median last spring frost and first fall frost (Tmin ≤ 0 °C), GDD base 10 °C (Apr–Oct, cap 30 °C), annual precip, days Tmax ≥ 35 °C, annual ET0 (from POWER).
- `water`: from D's `water.json`. `outlook`: declining if GRACE trend < −0.3 cm/yr or wells trend > 0.1 m/yr; rising if the opposite; else stable.
- `headline_facts` (3): `grace_trend {cm_per_yr}` (or `well_trend`), `frost_free_change {days}` or `heat_days_change {days}` (whichever is larger in magnitude), `current_rotation {years_from, years_to}`.

### 5.7 Validation (`validate/run.py`)

Use R0 run on the field's **actual** crop sequence from `crop_history` (not phase-averaged) for 2016–2023:

| id | How | Level rule |
|---|---|---|
| `et_vs_openet` | monthly modelled ETa vs OpenET, Apr–Oct months; `bias_pct = 100 × (Σmodel − Σopenet)/Σopenet`; also r² | good if \|bias\| ≤ 15% and r² ≥ 0.6; fair if \|bias\| ≤ 30%; else limited |
| `sm_vs_smap` | daily relative wetness `1 − Dr/TAW_root` vs SMAP L4 root-zone, both as anomalies from their own monthly means, 2015–2025; Pearson r | good r ≥ 0.6, fair ≥ 0.4 |
| `precip_power_vs_imerg` | monthly totals, bias % and r | good \|bias\| ≤ 10% and r ≥ 0.8; fair \|bias\| ≤ 20% |
| `precip_vs_cocorahs` | only if D provided gauge data | same as above |

Write `validation.json` with `vars` (`bias_pct` or `r`). Report the numbers honestly even if they're poor; a "limited" badge with an explanation earns more trust than hiding it.

### 5.8 AI assistant data (`assistant/`)

**Facts** (`context.py`) per field. Each `Fact` has a full English sentence with the number in it, a value, unit, source tag, and optional scenario/rotation:

- Field basics: area, soil texture, water storage (mm), wind erodibility, detected rotation and years.
- Climate: normal vs recent frost-free days, heat days, precip, ET0.
- Water: GRACE trend, well trend.
- For **every scenario** × rotation: irrigation mean, revenue mean, worst-5 revenue, stress days, bare windy days, soil health score, feasibility. (Tag each with `scenario` and `rotation_id`.)
- Replay drought year numbers per rotation (default scenario only).
- Neighbour groups: n, ET median, NDVI drops.
- Validation results.
- Glossary short definitions (unit null, source `MODEL`) for terms likely to come up.

Fact ids are stable and readable, e.g. `replay.R2.cap300|actual.irrigation_mm_mean`. Keep the whole file ≤ ~6k tokens when filtered to one scenario (check with a rough 4-chars-per-token estimate).

**System prompt** (`prompt.md` → `out/web/assistant/prompt.json` with `version`, `system`, `temperature: 0.2`, `max_tokens: 600`). Start from this and improve it by testing:

```text
You are the Field Assistant inside a crop-rotation planning tool for one farm field in Finney County, Kansas.
You help a farmer understand the tool's results. You support their judgement; you do not replace it.

Answer in {lang_name}. Write at about an 8th-grade reading level. Keep answers under 150 words:
short paragraphs or up to 4 bullets.

Rules:
1. Use ONLY the facts listed below. Every number you write must come from a fact. You may round it
   or convert mm to inches (1 in = 25.4 mm). Never invent or estimate a number.
2. After each sentence that uses a fact, add that fact's source tag in square brackets, e.g. [OpenET].
   Use only these tags: POWER, IMERG, SMAP, MODIS, HLS, ECOSTRESS, GRACE, SRTM, SSURGO, CSB, NASS,
   OpenET, PRISM, USGS, CoCoRaHS, GAEZ, AMS, FAO56, MODEL.
3. Say "may", "estimated" or "in similar fields". Never say "will", "guaranteed" or "proven".
4. If the facts don't answer the question, say you don't have that information and suggest asking a
   K-State Research and Extension agent or a local agronomist.
5. Never give pesticide, herbicide or fertilizer rates, legal advice about water rights, or financial
   guarantees.
6. "MODEL" numbers are estimates from a simplified water-budget model run on past weather; say so when
   it matters.

Field: {field_name}
Water and climate scenario: {scenario_label}
Strategies currently shown, best first: {top_rotations}

FACTS:
{facts_block}
```

`facts_block` lines: `- ({fact_id}) {text} [{source}]`. `scenario_label` example: "up to 300 mm (12 in) of irrigation per season, past weather as it happened". `top_rotations` example: "R2 wheat–sorghum–fallow, R1 corn–wheat–sorghum, R5 …, plus your current rotation R0".

**Number check** (`number_check.py`): implement README §9 exactly (same regex, skips, conversions, tolerance). Write unit tests with a few strings (`"about 12 inches"` vs fact 305 mm → verified; `"500 mm"` with no fact → unverified; `"in 2012"` → skipped). F implements the same in TypeScript; share your test strings with F so both agree.

**Cache** (`cache.py`): for each field, for each question in U's `assistant_questions.json` (q1–q6), for `en` and `es`, scenario `cap300|actual`, `top_rotations` = the default-weight top 3 + R0:

1. Build the prompt exactly as the web route will (README §9 server flow).
2. Call the LLM through the OpenAI Python SDK: `OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY).chat.completions.create(model=LLM_MODEL, messages=[...], temperature=0.2, max_tokens=600)`. Works for Gemini and Groq.
3. Run the number check. If any number is unverified, retry once with an extra user message: "Rewrite your answer using only numbers from the facts." If it still fails, keep the better answer and log it for manual review.
4. Store as `AskResponse` (README §9) with `cached: true`, `provider` set to the real provider, and `citations` resolved from D's `sources.json`.
5. Respect free-tier rate limits: sleep between calls, retry on 429 with backoff.

Read every cached answer yourself before calling the cache final. These are what judges will see if they click a suggested question.

### 5.9 Integration scripts (`scripts/`)

**`sync_data.py`** copies exactly the mapping in README §6.5 (create folders, overwrite files, print a summary of what was copied and from where). No transformation.

**`check_contract.py`** reads `web/public/data/` and fails (exit code 1) with a clear list if:

- any required file in README §8.1 is missing for `f1`, `f2`, `f3`
- any JSON lacks `_meta`, or any `_meta.mock` is true (warn only with `--allow-mock`)
- `replay.json` / `strategies.json` lack any of the 8 scenario keys or R0–R5
- any `text_id`, `gap_id`, `risk_id`, `infeasible_reason_id`, `headline` or `validation` id has no entry in `content/card_text.json`
- any template's `{placeholders}` aren't all present in the matching `vars`
- any `SourceTag` used anywhere is missing from `sources.json`
- any `CropId`, `RotationId`, `FieldId` outside README §7.2
- any file > 2 MB, or any `NaN` / `Infinity`
- `assistant_cache.json` lacks q1–q6 × en/es for a field

Run it before every merge to `main`.

## 6. Docs

- **`docs/METHODS.md`:** plain-language and technical description of the Replay (FAO-56 bucket, curve number, irrigation rule, yield response, heat/frost factors, phase averaging), erosion indices, soil-health index, calendar thresholds, normalisation, validation results, every constant in `config.py`, and the known simplifications. Judges look at this for "Validity".
- **`docs/AI_USE.md`:** which LLM/provider powers the in-app assistant, how it's grounded (facts only, number check, cache), and which AI tools the team used for planning and coding. Space Apps asks for this disclosure.

## 7. Acceptance checks

- [ ] `check_contract.py` passes with no mock files.
- [ ] Sanity checks in §5.3 pass for all 3 fields.
- [ ] For each field, the top-3 under default weights differ from R0 and the reasons make agronomic sense (e.g. dryland field never ranks an irrigated rotation first under `dryland`).
- [ ] Every number in every cached answer is verified, or the exception is logged and reviewed.
- [ ] `validation.json` exists for all fields, with honest levels.
- [ ] METHODS.md lists every constant and assumption.

## 8. Handover checklist

- [ ] `model/README.md` explains `run_all.py`, env vars, and how to switch from `mock_inputs/` to D's data.
- [ ] `model/out/web/` committed on branch `role/model`; mocks replaced field by field.
- [ ] Told F about any optional fields you added and any scenario/rotation that's infeasible everywhere.
- [ ] Shared the number-check test strings with F.
