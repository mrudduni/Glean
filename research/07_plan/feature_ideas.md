# Feature ideas, ranked

Written on 2026-11-14 from the research in this folder. Every feature below links to the evidence that supports it. The build order and timeline are in [build_plan.md](build_plan.md).

## How we ranked

Each feature gets a score from 0 to 3 on each judging criterion it moves (Impact, Creativity, Validity, Relevance, Presentation), plus an effort estimate in team hours. The tiers come from three tests:

1. Does it clear the judging gate or the challenge's required outputs? If yes, it is a must.
2. Does it make NASA data impossible to remove? The judging guidelines rate a project 3, not 5, on Relevance when "the method could function without it" (`../02_hackathon/judging_insights.md`).
3. Do competitors already do it? Matching the challenge's five outputs is the entry ticket, not an edge (`../02_hackathon/competition_2026.md`).

## The one question the tool answers

"If I move my Karnal field off puddled rice for the next five years, what happens to my water, my money and my risk, and how sure is that?"

Everything below serves that question. The demo shows one real field in Karnal district, Haryana.

## Must have (the hackathon build)

| ID | Feature | What the farmer sees | Criteria moved | Evidence | Effort |
|---|---|---|---|---|---|
| M1 | Field and current rotation | Pick a point or draw a field on a map of Karnal. Say what you grow now (default: puddled rice, then wheat). | Presentation 2 | WorldCereal can't infer the rotation (no rice class), so we ask (`../01_datasets/global/worldcereal.md`) | 4 h |
| M2 | Four strategies compared over 25 weather years | Current rice-wheat; direct-seeded rice-wheat (same crops, new practice); maize-wheat-mungbean; maize-mustard-mungbean. For each: irrigation need, groundwater draw, net return, and heat and dry-spell exposure, each as a median with a 10th to 90th percentile band. | Validity 3, Relevance 3, Impact 3 | FAO-56 coefficients (`../03_domain/crop_traits.csv`), measured Karnal irrigation by crop (`../03_domain/rotation_effects.csv` rows in23 to in30), engine design (`../03_domain/simulation_engines.md`) | 14 h |
| M3 | Evidence card per strategy | The five things the challenge asks for: why it was suggested, the evidence, what it may gain, where data is missing, what to check locally. Every number has a source link and a dataset badge. | Validity 2, Presentation 2 | Challenge text; card format in `../03_domain/farmer_ux_explainability.md` | 6 h |
| M4 | Uncertainty you can see | Bands on every number. A "sources disagree" strip that draws IMERG, CHIRPS v2, CHIRPS v3 and IMD rain for the same season. Resolution badges ("SMAP 9 km, your field 0.4 ha"). | Validity 3, Creativity 2, Relevance 2 | CHIRPS v2 and v3 differ by 125 mm on Karnal's 2024 kharif (`../01_datasets/global/chirps.md`); SoilGrids clay range of 3 to 86 percent (`../01_datasets/global/soilgrids.md`); the challenge video asks teams to "make uncertainty visible" | 5 h |
| M5 | Farmer priorities and rank stability | Put water, money, risk and soil in order. The app computes ROC weights, reruns TOPSIS 1,000 times with jittered weights, and says "maize-wheat-mungbean ranks first in 71 percent of draws". | Impact 2, Creativity 2, Validity 2 | `../03_domain/mcda_ranking.md`; FieldSense is the only competitor doing robustness | 4 h |
| M6 | Groundwater panel | GRACE terrestrial water storage trend for the region, and the nearest CGWB wells with their own trend lines (Kurukshetra median fall 1.15 m a year). Each source is labelled with its scale: GRACE about 300 km, wells point. | Relevance 3, Impact 3, Presentation 3 | `../01_datasets/india/cgwb_groundwater.md`; Rodell et al. 2009; Kunwar et al. 2024 (NASA co-author) in `../06_context/news_and_reports.md` | 5 h |
| M7 | Market and support risk flag | Each strategy shows its price support plainly: rice and wheat bought at MSP; maize MSP exists but HAFED bought none from 2022-23 to 2024-25; MPMV pays Rs 8,000 an acre; mustard procured at MSP. | Impact 3, Validity 2 | `../06_context/news_and_reports.md` sections 1 and 6, and the Reuters and Nature Communications reads | 3 h |
| M8 | Validation card | "How far to trust this": IMERG against IMD at Karnal; our ET against WaPOR; our irrigation numbers against the Karnal trials; plus a directional scorecard ("matched 7 of 8 published directions"). | Validity 3, Creativity 2 | `../03_domain/validation_plan.md` H1 to H3; only two competitors publish any validation | 6 h |

Must-have total: about 47 team hours. With four people that is about 12 hours each, which fits the window only if the region pack and the engine start tonight.

## Should have (build if the musts are green by Sunday 14:00)

| ID | Feature | Why it earns its place | Evidence | Effort |
|---|---|---|---|---|
| S1 | Break-even line | "Maize-wheat beats your current rotation if the maize price is above Rs X a quintal, or if MPMV pays for at least Y seasons." This answers the main finding of the news research: price support, not agronomy, keeps farmers on rice. No competitor read shows this. | Reuters Dec 2025; Chatterjee et al. 2024; HAFED data | 3 h |
| S2 | Plain-language summary in English and Hindi | Grok writes the card text from the evidence ledger. The `evidence_ids` field is an enum of real ledger IDs, the server checks every number, and a template takes over if a check fails. The card is labelled as SI-written. | `../05_stack/stack_v2.md`; SI rules in `../02_hackathon/rules_judging.md` | 4 h |
| S3 | "What would change my mind" list | For the agronomist: the two or three inputs that would flip the top rank (soil texture, maize price, tubewell share). | `../03_domain/farmer_ux_explainability.md` | 2 h |
| S4 | This-season panel (shown, not ranked) | SMAP L4 root-zone percentile, IMERG rain to date and SPI-3, POWER growing degree days. It sits apart from the multi-year ranking, which fixes the design flaw in the original score. | `../03_domain/mcda_ranking.md` "two panels"; `../00_challenge/team_notes_parisha.md` | 4 h |
| S5 | One-page printable report | Something a farmer can carry to the Krishi Vigyan Kendra. | `../03_domain/farmer_ux_explainability.md` | 2 h |
| S6 | Soil Health Card input | Typing in the card's pH, organic carbon and texture replaces SoilGrids, and the bands shrink on screen. This shows how local data reduces uncertainty. | SoilGrids organic carbon was two to three times the measured Karnal plots (`../01_datasets/global/soilgrids.md`) | 2 h |

## Stretch and after the event

| ID | Feature | Notes |
|---|---|---|
| L1 | DAPI-style greenness forecast | Label as experimental. The paper found weaker skill over irrigated land and calls 0.1 degree too coarse for fields. |
| L2 | Field history "barcode" from HLS | Infer past crops and bare-soil days from 10 years of HLS NDVI. It would replace the farmer's answer in M1 with evidence. |
| L3 | AquaCrop-OSPy and WOFOST yields | Tier 2 of the engine: a second opinion on water-limited yield. |
| L4 | LightGBM district yield model with conformal intervals | Tier 3. Needs district yield data and held-out validation. |
| L5 | Wheat terminal heat risk | Needs crop-stage heat thresholds with citations before use. |
| L6 | Residue and stubble-burning score | Haryana fire counts and fines are in the news file. Maize residue is easier to manage than paddy straw. |
| L7 | Kansas SD-6 as a second region | Shows the method transfers. SSURGO and OpenET make the US version stronger on data. |
| L8 | Offline PWA, voice, more languages | Needed for real farmer use, not for judging. |
| L9 | Groundwater draw to well depth | Converting mm of pumping into metres of water table needs specific yield by aquifer. Do it only with CGWB aquifer-mapping values and a clear caveat. |

## Ideas we drop

- 3D globes and farm "digital twins". Four competitors already do this, and it costs build time without adding Validity.
- A chatbot as the main screen. Judges look for one clear answer on screen. The language model writes card text only.
- A single 0 to 100 score with traffic lights as the main output. It mixes this month's weather with a five-year choice, and its weights came from an AI suggestion (`../03_domain/mcda_ranking.md`).
- Pearl millet as a headline strategy. MPMV does not list bajra in 2026, and Bhavantar pays the gap only at the state's purchase price (`../06_context/news_and_reports.md`). Keep it as an optional fifth strategy.
- Claims that rotation advice will fix the aquifer. The tool reports the field's share and says what it cannot control.

## How the musts map to the judging criteria

| Criterion | Features that carry it |
|---|---|
| Impact | M2, M6, M7, S1: a real decision in the worst groundwater hotspot in India, with money in view |
| Creativity | M4 (sources-disagree strip), M5 (rank stability), S1 (break-even line) |
| Validity | M2 (cited coefficients, measured irrigation), M8 (validation card), M4 (honest bands) |
| Relevance | M6 (GRACE), M2 (POWER and IMERG weather), S4 (SMAP); removing NASA data removes the water numbers |
| Presentation | One field, one question, one screen; the 30-second video follows the comparison screen |
