# Build plan, end to end

Written on 2026-11-14 at about 20:00 IST. Submission closes on 15 November at 23:59 local time, so about 28 hours remain and no code exists yet. This plan has two parts: what we ship by the deadline, and how the project grows after it. The features and their ranking are in [feature_ideas.md](feature_ideas.md).

## The product in one paragraph

A farmer or extension officer picks a field in Karnal district, Haryana, and says what they grow now. Field Shift runs four rotations on that field over 25 years of NASA weather. For each rotation it shows irrigation need, groundwater draw, net return, and dry-spell and heat exposure, with ranges and with the data behind every number. The farmer puts their priorities in order, and the tool says which rotation wins and how often it stays on top when the weights shift. A groundwater panel shows the regional GRACE trend next to the nearest monitoring wells. Each rotation names its market risk, because the research shows that price support, not agronomy, keeps farmers on rice.

## Fixed decisions

| Decision | Choice | Why |
|---|---|---|
| Demo place | One field in Karnal district (cropland point 29.69 N, 76.90 E, probed) | Rank 1 problem in `../06_context/problem_ranking.md`; all 22 blocks in the three districts are over-exploited; seven local trials give us ground truth |
| Strategies | Current puddled rice then wheat; direct-seeded rice then wheat; maize, wheat, mungbean; maize, mustard, mungbean | Each has measured Karnal irrigation data (`../03_domain/rotation_effects.csv`); DSR shows a practice change next to the crop changes |
| Engine core | FAO-56 dual-Kc daily water balance, plus a ponded bucket for puddled rice | Transparent and explainable in one sentence; FAO-56 p for rice is a share of saturation, so a plain bucket is wrong for paddy (`../03_domain/crop_traits.md`) |
| Ranking | ROC weights from the farmer's order, TOPSIS, 1,000-draw rank stability | `../03_domain/mcda_ranking.md` |
| LLM | Grok through the OpenAI SDK, writing card text only, with the enum guard and a template fallback | `../05_stack/stack_v2.md`; key in `.env` as `XAI_API_KEY` |
| Licence | Apache 2.0 for our code | Space Apps default |

## Hackathon stack: cut stack v2 down

Stack v2 is the right long-term design, but its database, task queue, pipeline and object store do not fit 28 hours. We recommend this cut for the deadline, keeping the same package boundaries so the cut needs no rewrite later.

| Stack v2 part | Hackathon version |
|---|---|
| `fieldshift-domain`, `fieldshift-data`, `fieldshift-engine` | Keep, as plain Python packages in one uv workspace |
| FastAPI on Cloud Run | Keep FastAPI. Deploy to Cloud Run if it is ready by Sunday 16:00; otherwise ship a static build with precomputed results |
| Neon Postgres, procrastinate | Drop. Nothing needs to persist for the demo |
| Dagster pipeline, R2 region packs | Replace with one script, `build_region_pack.py`, that writes Karnal inputs to Parquet and JSON outside the repo, plus a small committed snapshot for the demo |
| React, TanStack, Tailwind, shadcn/ui, MapLibre, ECharts | Keep React, Vite, Tailwind, MapLibre and ECharts. Add TanStack and shadcn only if someone already knows them |
| i18next, PWA | Hindi strings for the main screen only. No PWA |

Static fallback: the frontend must run from precomputed JSON with no backend. Judging links must open without a login, and NASA services may fail during judging.

## Data for the Karnal region pack

All sources below were probed live or found in CMR this session (`../04_data_probes/README.md`). Raw files go to the cache outside the repo (`FIELDSHIFT_CACHE`), never into git.

| Input | Source and route | Use | Fallback |
|---|---|---|---|
| Daily weather 2001 to 2025 (Tmax, Tmin, RH, wind, radiation, rain) | NASA POWER daily point API, no login | FAO-56 ET0 and the water balance | Open-Meteo ERA5 |
| Rain cross-check | IMERG monthly (`GPM_3IMERGM`, Final ends 2025-09) through earthaccess and OPeNDAP subsets; IMD 0.25 degree daily grid; CHIRPS v2 and v3 | Sources-disagree strip and validation card | Any two of the four |
| Root-zone soil moisture | SMAP L4 `SPL4SMGP.008` point series through AppEEARS (needs Earthdata Login) | This-season panel; dry-spell context | Open-Meteo soil moisture, labelled as model |
| Groundwater | GRACE and GRACE-FO JPL mascon RL06.3 (`C3195502222-POCLOUD`), one netCDF; CGWB Haryana well CSV | Groundwater panel | Wells only, with GRACE figures from Rodell 2009 and Kunwar 2024 |
| Actual ET for validation | WaPOR v3 AETI at 300 m; ECOSTRESS `ECO_L3T_JET` through AppEEARS where clear passes exist | Validation card | WaPOR only |
| Soil | SoilGrids REST at the point, with Q0.05 and Q0.95 | Water-holding capacity, with ranges | Measured Karnal plot values from the trials, labelled |
| Crop coefficients and irrigation evidence | `../03_domain/crop_traits.csv`, `../03_domain/rotation_effects.csv` | Engine inputs and evidence cards | None needed |
| Prices and support | MSP notices, HAFED purchase data, MPMV amounts already in `../06_context/news_and_reports.md` | Net return and the risk flag | Agmarknet needs a free data.gov.in key; if nobody has one, use the cited figures |

Check before the demo: the precipitation source that POWER uses in its daily point product, so the card names it correctly.

## Work packages and owners

Four roles. One person can hold two if the team is smaller. Names go here once the team confirms them.

| Role | Owns | First deliverable |
|---|---|---|
| Data | Region pack script, Earthdata and AppEEARS jobs, CGWB and GRACE extracts, fixtures | Karnal pack on disk by Sunday 06:00 |
| Engine | Domain types, FAO-56 water balance, rice bucket, net return, TOPSIS and rank stability, validation numbers | `run_strategies(field, strategies) -> results` with tests by Sunday 12:00 |
| Frontend | Map, strategy comparison screen, evidence cards, priority order, groundwater panel | Comparison screen on fixture JSON by Sunday 12:00 |
| Story | Project page text, data and licence list, SI disclosure, 30-second video, slide backup, contact with the Local Lead | Video script by Sunday 10:00, final cut by Sunday 21:00 |

Parisha's notes already cover the region and crop choice, so she is a natural fit for Story and for checking the agronomy on every card.

## Timeline (IST)

| When | Data | Engine | Frontend | Story |
|---|---|---|---|---|
| Sat 20:00 to 21:00 | All: agree this plan, freeze the domain types and the evidence ledger schema, create the repo layout, and start the AppEEARS jobs, because they queue for a while | | | |
| Sat 21:00 to 02:00 | POWER, SoilGrids, CGWB, GRACE pulls; IMERG monthly subsets started | FAO-56 ET0 and dual-Kc balance for one crop, checked against Open-Meteo ET0 | Vite app, map with the Karnal field, comparison screen layout on dummy JSON | Ask the Local Lead how local judging runs; draft the project page skeleton |
| Sun 02:00 to 07:00 | Sleep in shifts. Data finishes the IMERG and AppEEARS pulls when the jobs complete | | | |
| Sun 07:00 to 12:00 | IMD and CHIRPS cross-check numbers; WaPOR and ECOSTRESS ET at the point | All four strategies over 25 years; rice bucket; net return; TOPSIS and rank stability | Evidence cards, bands, resolution badges, priority order | Video script; data and licence table; SI disclosure text |
| Sun 12:00 to 16:00 | Validation card numbers (H1 to H3) | Break-even line (S1) if the musts are green | Groundwater panel; sources-disagree strip; validation card | Record screen captures as each screen lands |
| Sun 16:00 to 19:00 | All: integrate, deploy, run the static fallback, add the Grok summaries with the guard (S2) if time allows, and test every link in a private window | | | |
| Sun 19:00 to 22:00 | Fix bugs | Fix bugs | Polish the one demo path only | Edit the video to 30 seconds or less, watermark any SI media, fill every field on the project page |
| Sun 22:00 to 23:00 | All: final submit. The target is 23:00, an hour before the cutoff. Resubmission is allowed until the deadline | | | |

Cut rule: at 14:00 on Sunday, anything in the "should have" list that is not started gets dropped. The musts and the video come first.

## The 30-second demo

It follows the submission guide's outline. Screen capture only, so no SI watermark is needed unless we add generated images.

| Time | On screen | Voice or caption |
|---|---|---|
| 0:00 to 0:02 | Team name and member names | Names |
| 0:02 to 0:05 | Kurukshetra well chart falling from 10 m to 38 m | "Under rice, Kurukshetra's wells have dropped about a metre a year since 2000." |
| 0:05 to 0:10 | Title card: Field Shift | "Field Shift compares rotations for one real field, with NASA data you can check." |
| 0:10 to 0:20 | The comparison screen: four rotations, water and money bands, rank stability, GRACE panel, the sources-disagree strip | "POWER and IMERG weather, SMAP soil moisture, GRACE groundwater. Every number shows its range and its source." |
| 0:20 to 0:30 | Market risk flag and break-even line, then the evidence card | "It tells the farmer what a switch saves, what it risks, and what to check locally." |

Backup: a deck of at most 7 slides with the same story, in case the video fails the length check.

## Submission checklist

- Demo video of 30 seconds or less, or at most 7 slides, on a public link.
- Every link opens without a login, tested in a private window.
- Project page lists every data source with its licence. Licences to state with care:
  - DAPI paper: CC BY-NC-ND. We cite it, we don't reuse it.
  - Open-Meteo: CC BY 4.0, non-commercial tier.
  - WaPOR: CC BY 4.0 for the global layers.
  - SoilGrids: CC BY 4.0, still to confirm.
  - IMD: no licence stated, so cite and attribute.
  - CGWB data: "Other (Open)".
- SI disclosure: Claude used for research and code help; Grok writes card text at runtime, labelled on screen. The idea came from the team (Parisha's notes), which the rules require.
- Apache 2.0 licence file in the repo. No `.env`, tokens or `.netrc` committed.
- All members on the Members tab before the deadline.

## Risks for the next 28 hours

| Risk | What we do |
|---|---|
| AppEEARS or Earthdata jobs queue too long | Start them at 20:00 tonight. If SMAP is late, the this-season panel uses Open-Meteo soil moisture, labelled as model output |
| Rice water balance takes longer than planned | Use the measured Karnal irrigation ranges (rows in23 to in30) as the rice baseline and say so on the card |
| Frontend slips | The FastAPI docs page and a printable HTML report show the same results |
| The team runs out of time for the LLM layer | Template text from the evidence ledger already covers every card. The LLM is a nice-to-have |
| Demo goes over 30 seconds | Cut the title card to 2 seconds. A 31-second video fails the gate |
| Pre-event work rule | The FAQ says teams may not start work before the hackathon. Our research is background reading; all code starts inside the event window, and the git history shows it |

## After the event: the portfolio roadmap

| Phase | Weeks | Goal | Main work |
|---|---|---|---|
| 1. Harden | 1 to 2 | The hackathon code becomes tested and reproducible | Tests and recorded fixtures for every adapter; CI; the full stack v2 backend (Neon, Cloud Run); typed client from OpenAPI |
| 2. Science depth | 3 to 6 | Tier 2 and tier 3 of the engine | AquaCrop-OSPy and WOFOST yields; RUSLE and soil carbon; LightGBM district yield with conformal intervals; full H1 to H3 validation write-up |
| 3. Second region | 7 to 9 | Show the method transfers | Kansas SD-6 with SSURGO, CDL history and OpenET; the Dagster region-pack pipeline |
| 4. Field use | 10 to 14 | Make it usable by real farmers | HLS field-history barcode; Soil Health Card input; Hindi and Punjabi voice; offline PWA; a feedback session with a Karnal KVK or CSSRI scientist |
| 5. Write-up | 15 to 16 | Portfolio and paper | A methods note with the validation results, a public demo, and a short paper draft if the validation holds |

## Open decisions for the team

1. Team names for the four roles.
2. Who has an Earthdata Login and AppEEARS access tonight. Without it, SMAP, ECOSTRESS and GRACE pulls wait.
3. Whether anyone has a data.gov.in API key for mandi prices.
4. Whether to deploy the API or ship static only. Decide at 16:00 on Sunday.
5. The local judging format, from the Local Lead.
