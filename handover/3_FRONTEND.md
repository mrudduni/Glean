# Handover 3 · Frontend (F)

You are building the **web app** for Team Brackets' crop-rotation decision tool (NASA Space Apps 2026, "Adapting Farms with NASA Data"). Read the root [README.md](../README.md) first. It is the shared contract. §7 (IDs, conventions, placeholder formatting), §8 (data contract) and §9 (assistant API) define exactly what you consume and serve. If this file and the README disagree, the README wins.

## 1. Your mission

Build a Next.js app that lets a farmer pick one of 3 fields in Finney County, Kansas, see its conditions, set priorities and constraints, and compare their current rotation against the top 3 alternatives, with the Field Calendar, Rotation Replay, Farms Like Yours, trust badges and the AI Field Assistant. Deploy it on Vercel.

**The app reads only static JSON** from `web/public/data/` (README §8). The only server code is the `/api/ask` route. Nothing else fetches live data.

**Guiding rule:** numbers come from D and M, words come from U, you join them. Don't hard-code farmer-facing sentences; render U's templates with M's `vars`. You may write short English fallbacks for UI chrome (see §6).

## 2. What you own and must not touch

- **You own:** `web/**` (including `web/public/data/` mocks until the sync script replaces them, and `web/COPY_KEYS_ADDED.md`).
- **Don't edit:** `data-pipeline/`, `model/`, `scripts/`, `content/`, `design/`, `README.md`. Don't "fix" a data file by hand. Report it to its owner.

## 3. Stack and setup

- Current stable **Next.js (App Router)** + **TypeScript** (strict), Node 20 LTS.
- **Tailwind CSS** + **shadcn/ui** (Slider, Switch, Tabs, Card, Badge, Tooltip, Sheet/Drawer, Select, ToggleGroup, Skeleton).
- **react-leaflet** + Leaflet (load with `next/dynamic`, `ssr: false`). Basemap: Esri World Imagery tiles with attribution (NAIP image service is a COULD).
- **Recharts** for line/bar charts; the Field Calendar can be a CSS grid (simplest) or ECharts heatmap.
- **zod** for runtime validation of every JSON file in development (log mismatches loudly).
- No database, no auth, no state library needed (React context + URL search params).

```bash
npx create-next-app@latest web --ts --tailwind --app --eslint --src-dir=false --import-alias "@/*"
```

```text
web/
├─ app/
│  ├─ layout.tsx               # fonts, tokens, providers, mock banner, disclaimer footer
│  ├─ page.tsx                 # Pick a field
│  ├─ field/[id]/page.tsx      # field workspace (sections or tabs, see §5)
│  ├─ how-we-know/page.tsx     # trust page: sources, validation, glossary
│  └─ api/ask/route.ts         # assistant endpoint (README §9)
├─ components/                 # FieldMap, OverviewPanel, PrioritiesPanel, StrategyCard, FieldCalendar,
│                              # ReplayChart, NeighborsView, TrustBadge, AssistantDrawer, LangToggle, MockBanner
├─ lib/
│  ├─ types.ts                 # all README §7.2 / §8 / §9 types, copied verbatim
│  ├─ schemas.ts               # zod schemas mirroring types.ts
│  ├─ data.ts                  # typed loaders with caching
│  ├─ i18n.ts                  # t(), fill(), formatVar()
│  ├─ score.ts                 # README §8.7
│  ├─ numberCheck.ts           # README §9
│  ├─ state.tsx                # context: field, scenario, weights, constraints, lang
│  └─ ai/                      # prompt building + provider call (server only)
├─ styles/tokens.css           # from design/ via sync (placeholder until then)
├─ styles/tokens.json
├─ public/data/                # JSON (mocks until sync)
├─ COPY_KEYS_ADDED.md
└─ .env.example                # LLM_PROVIDER, LLM_BASE_URL, LLM_MODEL, LLM_API_KEY
```

## 4. Data layer

### 4.1 Types

Copy every type from README §7.2, §8.3, §8.4, §8.5 and §9 into `lib/types.ts` **verbatim** (same names, same fields). Mirror them as zod schemas in `lib/schemas.ts`. If the README changes, update both.

### 4.2 Loaders (`lib/data.ts`)

Client-side `fetch` from `/data/...` with an in-memory cache keyed by path:

```ts
getFields(): Promise<FieldsFile>                         // /data/fields.json
getSources(): Promise<SourcesFile>                       // /data/sources.json
getCrops(), getRotations()                               // /data/crops.json, /data/rotations.json
getContent(): Promise<{ cardText, copy, glossary, questions }>   // /data/content/*.json
getFieldBundle(fid): Promise<{
  summary, calendar, replay, strategies, validation,     // M
  water, observed, neighbors                             // D
}>                                                       // /data/field/{fid}/*.json, in parallel
```

- In development, parse with zod and `console.error` the path + issues on failure (don't crash the page).
- If any loaded file has `_meta.mock === true`, set a flag that shows `<MockBanner>` (text `copy["banner.mock"]`).
- Missing optional files (e.g. no `neighbors.json`) → hide that section with a short "not available for this field" note, never a crash.

### 4.3 Mocks first

Until M, D and U deliver, write your own mock files in `web/public/data/` that follow README §8 exactly, with `_meta.mock: true`. M will also deliver schema-correct mocks early; prefer theirs once they land. Mocks must include all 8 scenarios, R0–R5, and `card_text.json` / `copy.json` with English values for every key in README §8.6.

## 5. Screens and components

App state (`lib/state.tsx`), mirrored in URL search params so a view can be shared:
`field` (`f1|f2|f3`), `cap` (`dryland|cap150|cap300|cap450`, default `cap300`), `climate` (`actual|hotdry`, default `actual`), weights for the 5 sliders (default 3 each), `hay`, `cotton`, `forage` (booleans, default false), `lang` (`en|es`, default `en`). `scenario = `${cap}|${climate}``.

### 5.1 Pick a field (`/`)

- Title + tagline (`app.name`, `app.tagline`), short intro (`pick.subtitle`).
- `FieldMap`: Finney County with the 3 field polygons highlighted (colour by `kind`), neighbour pool faint if loaded. Click → `/field/{id}`.
- 3 field cards beside/below the map: name, kind, area (ha and ac), detected rotation (crop chips with crop colours), soil texture.

### 5.2 Field workspace (`/field/[id]`)

One scrolling page with a sticky section nav (`nav.*` keys), or tabs on mobile. Order follows the demo story (README §2):

1. **Overview** (`OverviewPanel`)
   - Current rotation: crop chips from `summary.current_rotation.steps`, "detected from USDA crop history {years}" (`overview.detected_from`).
   - Soil card: texture, water storage (mm and in), organic matter, wind erodibility in plain words (use glossary short text).
   - Climate shift: normal vs recent for frost-free days, days ≥ 35 °C, precip; small paired bars.
   - Water outlook: GRACE series sparkline + trend, nearest well trend, outlook chip (`overview.outlook.*`).
   - 3 headline facts from `summary.headline_facts` rendered with `card_text.headline[text_id]` + `vars`, each with source tags.
2. **Field Calendar** (`FieldCalendar`) — see §5.3.
3. **Your priorities** (`PrioritiesPanel`): 5 sliders (0–5), water cap segmented control, climate toggle (actual / hotter-drier), equipment and forage checkboxes. Changes re-score instantly.
4. **Strategies** (`StrategyCard` ×4) — see §5.4.
5. **Rotation Replay** (`ReplayChart`) — see §5.5.
6. **Farms Like Yours** (`NeighborsView`) — see §5.6.
7. Footer: disclaimer (`disclaimer.main`) and link to "How we know this".

The **Assistant** is a floating button opening a right-side drawer (bottom sheet on mobile), available on every field page — see §7.

### 5.3 Field Calendar

Data: `calendar.json`. One block per shown rotation (R0 + current top 3, in score order). Each block is a grid: rows = rotation years (`year_index`), columns = Jan–Dec. Each cell:

- background = crop colour (`--crop-{state}`; `bare` uses `--crop-bare` with a hatched pattern),
- small icons/dots for `flags` (`--risk-heat`, `--risk-frost`, `--risk-dry`, `--risk-storm`, `--risk-wind`),
- tooltip: crop name, stage, and the month's climate odds from `climate_risk` ("Heat in 7 of 10 Julys").

Above the blocks: a 12-column strip showing `climate_risk` (p_heat, p_frost, p_dry_spell as small bars; storm/windy days as numbers). Legend uses `calendar.*` keys. Must stay readable at 375 px (horizontal scroll inside the component only).

### 5.4 Strategy cards and scoring

Implement README §8.7 in `lib/score.ts` as pure functions with unit tests:

```ts
weightsFromSliders(sliders): Record<CriterionId, number>
scoreEntry(entry: StrategyEntry, w): number                 // 0–100
excluded(entry, constraints): null | "needs_more_water" | "needs_equipment" | "no_local_market"
pickShown(entries, w, constraints): { shown: StrategyEntry[]; hidden: { entry; reason }[] }  // R0 + top 3
whyBullets(entry, w): CriterionId[]                         // top 3 by w_k × norm_k where norm ≥ 50
```

`no_local_market` only applies as a flag (not exclusion) when `crops_without_local_market` is non-empty; show it in risks. Exclusion for forage is `needs_forage_market && !forage`.

Each `StrategyCard`:

- Header: rotation name and tagline (`card_text.rotations[id]`), crop chips, score (0–100) as a bar, `card.current_badge` on R0, confidence chip (`trust.level.*`).
- Per-criterion mini bars (`criteria_labels`) showing `norm`.
- **Why** (`card.why`): 2–3 bullets from `whyBullets`, text `card_text.why[k]` filled with `criteria[k].vars`.
- **Evidence** (`card.evidence`): each `evidence[]` item → `card_text.evidence[text_id]` + vars, followed by source tag chips (hover → `sources.json` name, link).
- **Benefits** (`card.benefits`): `card_text.benefits[text_id]` + vars.
- **Information gaps** (`card.gaps`): `card_text.gaps[id]`.
- **Risks to check locally** (`card.risks`): `card_text.risks[id]`.
- R0's card shows the same sections (its why/benefits may be empty; show its numbers).

Below the cards: "{n} strategies hidden" (`card.hidden_count`) with their reasons (`card_text.infeasible[reason]`), expandable.

Layout: 4 columns on wide screens, horizontal swipe or stacked on mobile. Sections inside a card align across cards (same order, same heights where possible).

### 5.5 Rotation Replay

Data: `replay.json` for the current scenario; series for R0 + shown rotations.

- Metric switcher: irrigation (mm, show in also), revenue ($/ac), stress days, bare days (`replay.metric.*`).
- Line chart, x = 2000–2025, one line per rotation (`--rot-{id}` colours; R0 dashed or grey). Vertical shaded bands for `drought_years` (`replay.drought_marker`).
- Summary row beneath: average and worst-5 per rotation.
- Note under the chart from `copy` (e.g. "Average across every phase of the rotation, on this field's real weather").
- The climate toggle switches between `actual` and `hotdry` data instantly.

### 5.6 Farms Like Yours

Data: `neighbors.json`.

- Mini map: demo field outline + matched neighbours coloured by `rotation_class` (map class → R-id via `matches_rotation`, use `--rot-*` colours; unmatched grey).
- Comparison table: one row per group: rotation name, `n` (`neighbors.n_fields`), median ET (mm and in), NDVI drop 2012 and 2022 (`neighbors.drought_greenness`), `is_current` highlighted.
- Disclaimer (`neighbors.disclaimer`): similar fields, observational, not proof.

### 5.7 How we know this (`/how-we-know`)

- Validation badges per field from `validation.json` (`TrustBadge`: level colour + `card_text.validation[id]` + vars + source chips).
- Sources table from `sources.json`.
- Glossary from `glossary.json` (term, short, expandable long).
- Satellite-vs-ground explainer (glossary `satellite_vs_ground`), "model estimate" explainer (`model_estimate`).
- The "supports, doesn't replace your judgement" notice.

## 6. Text, language and formatting (`lib/i18n.ts`)

```ts
t(key: string, fallback?: string): string                   // copy.strings[key][lang] → en → fallback → key
fill(template: Localized, vars: Record<string, number|string>, lang): string   // replaces {name} via formatVar
formatVar(name: string, value: number|string, lang): string // README §7.4 suffix rules
```

- `_mm` → `310 mm (12.2 in)`; `_usd_ac` → `$412/ac`; `_pct` → `12%`; `_crop` → crop name from `crops.json`; etc. (README §7.4). Spanish: same with `pulg.` for inches.
- Missing placeholder value → render `—` and `console.warn`.
- Any key you need that isn't in README §8.6 → use `t("new.key", "English fallback")` and add a line to `web/COPY_KEYS_ADDED.md` (`key | where it's used | English text`). U fills it.
- `LangToggle` (EN/ES) in the header switches everything, including the assistant language.

## 7. AI Field Assistant

### 7.1 UI (`AssistantDrawer`)

- Header `assistant.title`; 6 suggested-question chips (`assistant_questions.json`, current language).
- Chat list: user messages, assistant answers rendered as markdown. In assistant answers:
  - `[TAG]` → small source chip (tooltip: `sources.json` name; link opens the source URL).
  - Each number from `numbers[]`: verified → subtle dotted underline + tooltip with the fact id/source; unverified → amber `assistant.unverified` badge next to it.
- Input with `assistant.placeholder`, send button, 500-char limit, disabled while waiting.
- `notice: "using_cache"` / `"scenario_mismatch"` → small banner (`assistant.using_cache`).
- 503 → message `assistant.error` and highlight the chips.
- Send `history` (last 6 turns), `top_rotations` (current shown order), `scenario`, `lang`, `field_id`.

### 7.2 Route (`app/api/ask/route.ts`)

Implement README §9 exactly. Notes:

- `export const runtime = "nodejs"`.
- Load `prompt.json`, each field's `assistant_context.json` and `assistant_cache.json`, `sources.json`, and `content/glossary.json` with **static imports** from `@/public/data/...` (a small map `{ f1, f2, f3 }`), so they're bundled into the function on Vercel.
- Build `facts_block`, fill the template placeholders, call `${LLM_BASE_URL}/chat/completions` with `fetch` (no SDK needed), `AbortController` timeout 20 s.
- `lang_name`: `en → "English"`, `es → "Spanish"`. `scenario_label`: from `copy` (`constraints.cap.*` + `climate.*`, English).
- `question_id` → serve from cache immediately (never call the LLM).
- Validate input: known `field_id`, `lang`, `scenario`; `question` ≤ 500 chars; `history` ≤ 6 items, each ≤ 1500 chars. Return 400 otherwise.
- Never log the API key or full prompts in production. Keys only in Vercel env vars (server-side, no `NEXT_PUBLIC_`).
- Optional: very simple in-memory rate limit (e.g. 20 requests/min per IP) to protect the free tier during judging.

### 7.3 Number check (`lib/numberCheck.ts`)

Implement README §9's algorithm exactly; M implements the same in Python. Get M's test strings and make both implementations pass the same cases. Unit test it.

## 8. Design and accessibility

- Import `styles/tokens.css` in `app/layout.tsx`; map the CSS variables into Tailwind's theme (Tailwind v4 `@theme` or v3 `theme.extend.colors`), e.g. `bg-surface`, `text-muted`, `crop-corn`. Use `styles/tokens.json` where a library needs literal colours (Recharts, Leaflet).
- Use U's wireframes for layout. Until they arrive, follow the order in §5.2.
- Mobile first: everything must work at 375 px. Charts and the calendar scroll horizontally inside their own containers; the page never scrolls sideways.
- Keyboard: all sliders, toggles, chips and the drawer operable by keyboard; visible focus rings; drawer traps focus and closes on Escape.
- Colour is never the only signal: calendar flags have icons; trust levels have text; unverified numbers have a text badge.
- Respect `prefers-reduced-motion`.
- Loading states: skeletons for each section; errors per section, never a blank page.

## 9. Deployment

- Create the Vercel project from the GitHub repo with root directory `web/`. Deploy the shell early so deployment is never a last-minute surprise.
- Env vars in Vercel: `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY` (README §9 table).
- `npm run build` must pass with no type errors. Lighthouse on the field page: aim for performance ≥ 80 and accessibility ≥ 90 on mobile.

## 10. Acceptance checks

- [ ] All three fields render every section with real data after `scripts/sync_data.py`, with no console errors and no zod failures.
- [ ] Changing a slider, the water cap or the climate toggle updates cards, calendar order and replay instantly.
- [ ] R0 is always shown; hidden strategies list their reasons.
- [ ] Every card shows why / evidence / benefits / gaps / risks, with source chips on evidence.
- [ ] EN ↔ ES switches every visible string (falls back to English where Spanish is empty).
- [ ] Suggested questions answer instantly from cache; free-text questions call the LLM; turning the key off gives the 503 path gracefully.
- [ ] Unverified numbers are visibly badged.
- [ ] Works at 375 px and on desktop; keyboard-only run-through works.
- [ ] Mock banner shows only while mock data is loaded.
- [ ] Production deploy on Vercel works from a fresh browser.

## 11. Handover checklist

- [ ] `web/README.md`: how to run locally, env vars, where data comes from.
- [ ] `web/COPY_KEYS_ADDED.md` up to date and sent to U.
- [ ] Number-check tests pass on M's shared cases.
- [ ] Live URL shared with the team; branch `role/web` merged.
