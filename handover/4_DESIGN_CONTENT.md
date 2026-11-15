# Handover 4 · Design + content (U)

You own the **look, the words and the pitch** for Team Brackets' crop-rotation decision tool (NASA Space Apps 2026, "Adapting Farms with NASA Data"). Read the root [README.md](../README.md) first. It is the shared contract. §7.4 (placeholder formatting) and §8.5–§8.6 (your file formats and the full list of text keys) define exactly what you must produce. If this file and the README disagree, the README wins.

## 1. Your mission

- **Design:** wireframes for the 5 main screens, and the design tokens (colours, fonts, crop and rotation colours) the app is built with.
- **Crop research:** `content/crops.yaml`, the crop parameters M's model runs on.
- **Words:** every farmer-facing sentence in the app, in English and Spanish: card templates, UI strings, glossary, suggested assistant questions.
- **Pitch:** demo video or slides, the submission text, and the project name.

**Guiding rule:** numbers come from D and M, words come from you, F joins them. You write templates with `{placeholders}`; M fills the values; F formats them. You never type a data number into a sentence.

## 2. What you own and must not touch

- **You own:** `content/**`, `design/**`, `docs/PITCH.md`, `docs/SUBMISSION.md`.
- **Don't edit:** `data-pipeline/`, `model/`, `scripts/`, `web/`, `README.md`. Ask F for UI changes and M for data changes.

## 3. Delivery order (what others are waiting for)

1. **Wireframes** (`design/wireframes/`) and a first **`design/tokens.css` + `tokens.json`**. F builds on these.
2. **`content/card_text.json` with every key in README §8.6, English first.** Then `copy.json`. F and M depend on the keys existing.
3. **`content/crops.yaml`** with researched values. M runs the real model on it.
4. `assistant_questions.json`, `glossary.json`.
5. Spanish for everything.
6. Pitch, video/slides, submission text.

Tell F and M each time a file is complete. Check `web/COPY_KEYS_ADDED.md` regularly. F lists extra keys there that need your text.

## 4. Design

### 4.1 Who it's for

A farmer in western Kansas, often on a phone or tablet, sometimes outdoors in bright light, not necessarily technical, possibly more comfortable in Spanish. Also: a K-State extension agent and the judges. Plain, calm, trustworthy, readable. Not a sci-fi NASA dashboard.

### 4.2 Wireframes (`design/wireframes/`)

PNG exports (or a Figma link in `design/wireframes/README.md`) at phone width (375 px) and desktop (1280–1440 px) for:

1. **Pick a field:** map of Finney County with 3 highlighted fields + 3 field cards.
2. **Field overview:** current rotation chips, soil card, climate shift (normal vs recent), water outlook (aquifer trend), 3 headline facts.
3. **Field Calendar:** months × rotation years per strategy, crop colours, bare-soil hatching, risk icons, climate-odds strip on top.
4. **Priorities + strategy cards:** 5 sliders, water cap, climate toggle, equipment/forage checkboxes; 4 cards side by side (stacked/swiped on phone), each with score, criterion bars, and the five sections (why / evidence / benefits / gaps / risks) with source chips.
5. **Replay + Farms Like Yours + assistant:** replay line chart with drought bands and metric switcher; neighbour mini-map + comparison table; assistant drawer with suggested-question chips, source chips and an "unverified" badge example.

Annotate what each element shows and where its text comes from (key names from README §8.6), so F's agent can build directly from the wireframes.

### 4.3 Design tokens (`design/tokens.css`, `design/tokens.json`)

Plain CSS custom properties on `:root` (no framework syntax), with these exact names (README §8.5):

| Group | Tokens | Guidance |
|---|---|---|
| Base | `--color-bg, --color-surface, --color-fg, --color-muted, --color-border, --color-accent` | High contrast for outdoor reading. Neutrals with a slight earthy or sky bias, chosen on purpose. |
| Trust levels | `--color-good, --color-fair, --color-limited` | Distinct from crop colours; always paired with text in the UI. |
| Crops | `--crop-corn, --crop-sorghum, --crop-wheat, --crop-soybean, --crop-alfalfa, --crop-triticale, --crop-rye_cover, --crop-cotton, --crop-fallow, --crop-bare` | Intuitive (wheat golden, sorghum rust, alfalfa green…), distinguishable from each other, readable with dark text on top. `bare` is a pale soil tone (F adds hatching). |
| Rotations | `--rot-R0 … --rot-R6` | Chart line colours. R0 neutral grey/dark so the current rotation reads as the baseline. Must be distinguishable for common colour-blindness types. |
| Risks | `--risk-heat, --risk-frost, --risk-dry, --risk-storm, --risk-wind` | Small icons/dots in the calendar. |
| Type | `--font-display, --font-body, --font-mono` | Google Fonts with system fallbacks. Large, legible body (≥ 16 px). Tabular numbers. |
| Shape | `--radius` | |

Dark mode is optional; if you do it, override the same tokens under `[data-theme="dark"]`.

`design/tokens.json` holds the same values as plain strings for chart and map libraries:

```json
{
  "color": { "bg": "#…", "surface": "#…", "fg": "#…", "muted": "#…", "border": "#…", "accent": "#…",
             "good": "#…", "fair": "#…", "limited": "#…" },
  "crop":  { "corn": "#…", "sorghum": "#…", "wheat": "#…", "soybean": "#…", "alfalfa": "#…",
             "triticale": "#…", "rye_cover": "#…", "cotton": "#…", "fallow": "#…", "bare": "#…" },
  "rot":   { "R0": "#…", "R1": "#…", "R2": "#…", "R3": "#…", "R4": "#…", "R5": "#…", "R6": "#…" },
  "risk":  { "heat": "#…", "frost": "#…", "dry": "#…", "storm": "#…", "wind": "#…" },
  "font":  { "display": "…", "body": "…", "mono": "…" }
}
```

Check text contrast ≥ 4.5:1 for body text and ≥ 3:1 for large text and chart marks.

## 5. Crop research (`content/crops.yaml`)

Schema: README §8.5. One entry for each of `corn, sorghum, wheat, soybean, alfalfa, triticale, rye_cover, cotton, fallow`.

| Field | Where to find it |
|---|---|
| `kc`, `stage_days` | FAO Irrigation and Drainage Paper 56, Table 11 (stage lengths) and Table 12 (Kc). Pick the stage lengths closest to the US Great Plains; adjust to Kansas planting/harvest windows. |
| `root_max_m`, `p` | FAO-56 Table 22 |
| `ky` | FAO Irrigation and Drainage Paper 33 (yield response to water); also summarised in FAO-56 |
| `plant_window`, `harvest_window` | K-State Research and Extension crop production handbooks / planting date guides for southwest Kansas |
| `heat.tmax_c`, `heat.stage`, `frost_kill_c` | Extension and agronomy references (e.g. corn pollination above ~35 °C; winter wheat grain fill above ~32 °C) |
| `yield.*_default`, `price.default` | Only as fallback: K-State or NASS Kansas averages. M overrides them with NASS data when available. |
| `family`, `host_group` | Botanical family; pest/disease host group (corn rootworm → corn; sorghum and corn share some pests, so decide and document) |
| `n_fixing`, `residue`, `root_type`, `forage`, `equipment`, `requires_irrigation` | Agronomy basics; SARE *Managing Cover Crops Profitably* for rye and triticale |

M has starter values in [2_MODEL_AI.md](2_MODEL_AI.md) §5.1 to use until yours land. **Cite a source for every number** in `sources:`. Write `null` rather than guessing. Mark anything you're unsure of with a YAML comment `# verify`.

`fallow`: `season: none`, `kc: {ini: 0.3, mid: 0.3, end: 0.3}`, no yield or price, `residue` depends on the previous crop (leave `low`).

## 6. Words

### 6.1 Writing rules

- **Plain language,** about an 8th-grade reading level. Short sentences. Talk to the farmer as "you" / "your field".
- **Never overclaim.** Use "may", "estimated", "in similar fields", "on past weather". Never "will", "guaranteed", "proven", "best".
- **Name things the way farmers do:** "irrigation water", "bare ground", "wheat stubble", "pivot", "dryland". Explain terms like ET or NDVI in the glossary, not inline.
- **Units:** never type units next to a placeholder. F adds them from the variable name (README §7.4). Write `You'd use about {saved_mm} less irrigation water a year.` → F renders "about 120 mm (4.7 in) less…".
- **Every placeholder you use must be in that key's var list** (README §8.6). You may leave a var out, but never invent one.
- **Gaps and risks are honest and specific,** and end with what to check and with whom where it helps ("Ask your elevator or co-op before planting.").
- **Spanish:** natural Latin American Spanish as spoken in farming communities in the Great Plains, not literal translation. Keep it equally short. Have a native speaker check if anyone on the team or nearby can. `es: ""` falls back to English, so do English for everything first.

### 6.2 `content/card_text.json`

Fill **every** key in README §8.6 with `{ "en": "...", "es": "..." }`. Examples of the style (rewrite as you like):

```json
{
  "_meta": { "schema": "card_text@1", "mock": false, "generated_at": "…", "generator": "content (U)" },
  "rotations": {
    "R0": { "name": { "en": "Your current rotation", "es": "Su rotación actual" },
            "tagline": { "en": "What this field has grown in recent years", "es": "Lo que este campo ha sembrado en los últimos años" } },
    "R2": { "name": { "en": "Wheat – sorghum – fallow", "es": "Trigo – sorgo – barbecho" },
            "tagline": { "en": "The dryland classic: stores rain in the fallow year", "es": "El clásico de secano: guarda la lluvia en el año de barbecho" } }
  },
  "criteria_labels": { "water_use": { "en": "Saves water", "es": "Ahorra agua" } },
  "why": {
    "water_use": { "en": "Uses about {saved_mm} less irrigation water a year than your current rotation.",
                   "es": "Usa unos {saved_mm} menos de agua de riego al año que su rotación actual." },
    "wind_erosion": { "en": "Leaves the ground bare on {bare_windy_days} windy days a year, compared with {r0_bare_windy_days} now.",
                      "es": "Deja el suelo descubierto {bare_windy_days} días de viento al año, frente a {r0_bare_windy_days} ahora." }
  },
  "evidence": {
    "replay_drought": { "en": "In {year}, this rotation would have needed about {irrigation_mm} of irrigation, compared with {r0_irrigation_mm} for your current one.",
                        "es": "En {year}, esta rotación habría necesitado unos {irrigation_mm} de riego, frente a {r0_irrigation_mm} con la actual." },
    "neighbors": { "en": "{n} nearby fields on similar soil already farm this way. Satellites show they used about {et_mm} of water a year, compared with {r0_et_mm} on fields like yours.",
                   "es": "{n} campos cercanos con suelo parecido ya trabajan así. Los satélites muestran que usaron unos {et_mm} de agua al año, frente a {r0_et_mm} en campos como el suyo." }
  },
  "gaps": {
    "no_pest_data": { "en": "We have no pest counts for this field. The pest-cycle benefit is based on which crops host the same pests.",
                      "es": "No tenemos conteos de plagas para este campo. El beneficio contra plagas se basa en qué cultivos comparten plagas." }
  },
  "risks": {
    "herbicide_carryover": { "en": "Some wheat herbicides can harm the next crop. Check labels and plant-back times with your agronomist.",
                             "es": "Algunos herbicidas del trigo pueden dañar el siguiente cultivo. Revise las etiquetas y los plazos con su agrónomo." }
  }
}
```

The full key list (all must exist): `rotations` R0–R6 · `criteria_labels` and `why` for all 8 criteria · `benefits` (6) · `evidence` (4) · `gaps` (9) · `risks` (10) · `infeasible` (3) · `headline` (5) · `validation` (4). See README §8.6 for ids and vars.

### 6.3 `content/copy.json`

`{ "_meta": …, "strings": { "<key>": { "en": "…", "es": "…" } } }` with every key listed in README §8.6 (`app.name` … `assistant.error`), plus any F lists in `web/COPY_KEYS_ADDED.md`. Notes:

- `app.name` = the project name (see §8). `app.tagline` = one line on what the tool does.
- `disclaimer.main`: this tool supports, and doesn't replace, the farmer's judgement and local expert advice; results are estimates from satellite data, models and past weather.
- `banner.mock`: "Showing sample data" (developer-facing but visible).
- `constraints.cap.*`: "No irrigation (dryland)", "Up to 150 mm (6 in) a season", etc. (here units are fixed text, not placeholders, so write them out).
- `neighbors.disclaimer`: these are similar fields, not identical; differences may have other causes.

### 6.4 `content/glossary.json`

`{ "_meta": …, "terms": [ { "id", "term", "short", "long" } ] }` with all ids from README §8.5. `short` is one sentence (used in tooltips and by the assistant); `long` is 2–4 sentences. Include a plain explanation of how satellite measurements differ from ground measurements (`satellite_vs_ground`) and what a model estimate is (`model_estimate`). The challenge explicitly asks for these explanations.

### 6.5 `content/assistant_questions.json`

Six questions a farmer would actually ask, `q1`–`q6`, EN + ES. They must be answerable from the facts M provides (README §8.4 `AssistantContext`). Suggested set:

1. Why is the top strategy ranked first for my field?
2. How much irrigation water could I save?
3. Why not alfalfa?
4. What would a drought year like 2012 have done to each option?
5. How sure are you about these numbers?
6. What should I check with my extension agent before switching?

Send them to M early. M generates cached answers from them, and those are what judges will see first.

## 7. Pitch

### 7.1 Story

Use the demo story in README §2 as the spine: a real field, a real water problem, three better options, evidence from past weather and from neighbouring fields, an assistant that shows its sources, and a clear "you decide" ending. Mention the NASA data plainly (SMAP, GPM IMERG, MODIS, Landsat/HLS, POWER, ECOSTRESS, GRACE, SRTM) and the Dust Bowl link for western Kansas.

### 7.2 Demo video or slides

Check the 2026 Space Apps rules for the required format (past years: a 30-second video *or* up to 7 slides). Prepare:

- **Video (30 s):** script with timings in `docs/PITCH.md`, screen recording of the live app (record from the deployed site at 1080p), captions burned in, no music needed. Rough beats: problem (5 s) → pick field + calendar (6 s) → priorities + cards (8 s) → replay drought (5 s) → neighbours + assistant (4 s) → "supports your judgement" close (2 s).
- **Slides (≤ 7):** problem · our tool · how it decides (data → model → cards) · Rotation Replay · Farms Like Yours + assistant · validation and honesty · impact and next steps.

Don't use NASA logos or the "meatball" insignia (Space Apps rules). Screenshots of the app and charts are fine.

### 7.3 `docs/SUBMISSION.md`

Draft every text field of the Space Apps project page: project name, high-level summary (~200 words), detailed description (what it does, how it works, benefits, intended impact), tools and languages, NASA data used (with links, from D's `docs/DATA_SOURCES.md`), space agency partner data (Sentinel-2 if used), other data, use of AI (from M's `docs/AI_USE.md`), and links (live URL, repo, video/slides).

## 8. Decisions you own

- **Project name:** shortlist (RootCycle, FieldShift, Second Season, or your own); pick one with the team and put it in `copy.json` `app.name`.
- **Visual direction:** whatever you choose, keep it readable outdoors and colour-blind safe.

## 9. Acceptance checks

- [ ] `card_text.json` and `copy.json` contain every key in README §8.6 (and in `web/COPY_KEYS_ADDED.md`), English complete, Spanish complete or deliberately empty.
- [ ] Every `{placeholder}` is in that key's allowed var list; no units typed next to placeholders.
- [ ] `crops.yaml` has all 9 crops, every field filled or `null`, with sources.
- [ ] `tokens.css` and `tokens.json` contain every required token with matching values; contrast checked.
- [ ] No sentence promises an outcome ("will", "guaranteed").
- [ ] `scripts/check_contract.py` (run by M or the integrator) reports no missing text keys.
- [ ] Video/slides and `docs/SUBMISSION.md` ready before the deadline, using the final deployed app.

## 10. Handover checklist

- [ ] All files committed on branch `role/content`.
- [ ] Told F the tokens and wireframes are final; told M `crops.yaml` and `assistant_questions.json` are final.
- [ ] Project name agreed and in `copy.json`.
