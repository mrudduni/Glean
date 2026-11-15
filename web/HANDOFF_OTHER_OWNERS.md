# Handoff: UI/UX items owned outside `web/`

The web app works around each of these today (details per item), but the lasting fix belongs in the owner's folder. Everything here is ready to apply.

## U · content and design (`content/`, `design/`)

### 1. Form-like copy templates

`web/lib/copyPreferred.ts` shows plain versions of these strings **only while `content/` still has the old text**. Once you change a string, your version is used. Templates may now use plurals: `{years} {years|year|years}` (both `fill()` and `interpolate()`).

| Key | Now | Proposed (EN) |
|---|---|---|
| `card_text.headline.heat_days_change` | Hot days (35 °C or higher) a year, recent years versus 1991 to 2020, change in days: {days}. | Needs more/fewer, so the model should pass `days_abs` and a direction, or keep the web wording: "Recent years have had 3 fewer days at 35 °C or hotter each year than 1991 to 2020." |
| `card_text.headline.frost_free_change` | Frost-free season, recent years versus 1991 to 2020, change in days: {days}. | "The frost-free season is now 3 days longer than in 1991 to 2020." (same note on direction) |
| `card_text.headline.grace_trend` | … changing by {cm_per_yr} a year since 2002. | … changing by {cm_per_yr} since 2002. (the unit already says per year) |
| `card_text.why.soil_health` | Soil health score: {score} out of 100. Days a year with living roots … Years with a legume in the cycle: {legume_years}. | Soil health score {score} out of 100. Living roots are in the ground about {living_root_days} days a year, and a legume grows in {legume_years} {legume_years\|year\|years} of the cycle. |
| `card_text.why.pest_break` | Years in a row with the same crop family: {max_run_years}, compared with … | The same crop family runs at most {max_run_years} {max_run_years\|year\|years} in a row, against {r0_max_run_years} now. … |
| `card_text.why.water_erosion` | Stormy days a year with bare ground: {bare_storm_days}, compared with … | Bare ground on {bare_storm_days} stormy days a year, against {r0_bare_storm_days} now. |
| `card_text.why.wind_erosion` | Windy days a year with bare ground: … | Bare ground on {bare_windy_days} windy days a year, against {r0_bare_windy_days} now. |
| `card_text.why.heat_frost_risk` | Hot days a year when crops are in a heat-sensitive stage: {heat_days}, … | Crops are in a heat-sensitive stage on {heat_days} hot days a year, against {r0_heat_days} now. |
| `card_text.benefits.pest_cycle_broken` | … Longest run of one crop family, in years: {max_run_years}. | … The longest run of one crop family is {max_run_years} {max_run_years\|year\|years}. |
| `card_text.benefits.bare_days_reduced` | Days a year with the ground covered may rise by about {days}. | The ground may be covered about {days} more days a year. |
| `card_text.benefits.legume_added` | Legume years in the cycle: {legume_years} of {cycle_years}. … | A legume grows in {legume_years} of {cycle_years} years. … |
| `copy.card.hidden_count` | Options hidden by your limits: {n} | {n} more {n\|option is\|options are} hidden by your limits |
| `copy.card.shown_at` | Numbers shown with: {cap}. | Numbers shown at {cap}. |

Spanish for each is in `web/lib/copyPreferred.ts`.

### 2. Criterion label and score name
- `card_text.criteria_labels.heat_frost_risk` = "Heat and frost risk" reads backwards on a bar where 100 is best. The web shows "Avoids heat and frost damage" (your wireframe's wording) via `criteria.heat_frost_display`. Please change the label itself.
- `copy.card.score` "Match score": the web shows "Fit with your priorities" (wireframe wording) via `card.fit_label`.

### 3. New copy keys
All keys the web added are listed in `web/COPY_KEYS_ADDED.md`, with Spanish in `web/lib/copyFallbacks.ts` (used only until the key is in `content/copy.json`). Please copy them across.

### 4. Tokens
`web/styles/tokens.css` and `web/styles/tokens.json` now hold:
- **Rotation colours** re-stepped with the dataviz palette validator over all pairs (any three can appear together). Light: R1 #893A0E, R2 #2F40C2, R3 #B688FE, R4 #2FBDA7, R5 #F97C3D, R6 #D03275 (normal-vision ΔE 19.3, deutan 13.0). Dark: R0 #BDBDBD, R1 #A14206, R2 #3B51D3, R3 #A76EF8, R4 #61A82D, R5 #ED4F8D, R6 #AA167D (16.9 / 9.5). R0 light stays #4B4B4B, drawn dashed. The previous sets failed (light R0↔R1 ΔE 12.9 normal; dark R6↔R3 3.6 deutan).
- **Dark theme** surface, text and accent back to your `design/tokens.css` values.

Please copy the rotation colours into `design/tokens.json` / `design/build_tokens.py` so `design/check_cvd.py` and the generated files agree.

## M · model and assistant (`model/`)

1. **Assistant cache order.** `assistant_cache.json` records `top_rotations` (f1: R4, R5, R1, R0), but the default cards are R0, R5, R1, R2 (alfalfa needs a forage buyer, off by default). The web now answers a mismatched suggested question live when a model is configured, and falls back to the saved answer with a notice. Please regenerate the cache for the default view of each field (default sliders, `cap300` on irrigated fields, `dryland` on f2, no equipment) so the demo's first question needs no live call.
2. **Rounding.** Cached answers contain values like "75.43 out of 100". Round scores to whole numbers in the facts given to the model.
3. **"Why" rule (README §8.7).** The web lists a criterion under "Why it was suggested" only when the option scores higher than the current rotation on it (it used to list "Average income … −$222/ac" as a reason). Please confirm and add this to §8.7 and to the Python side if it builds the same bullets.

## D · data (`data-pipeline/`)

1. `neighbors.json`: `ndvi_drop_2012_pct` and `ndvi_drop_2022_pct` are null for every group. The web hides both columns and shows "Drought-year greenness (MODIS) is not available for these fields yet." Filling them brings the columns back with no web change.
2. `sources.json`: `used_for` and `what` are English only. The web shows Spanish from `web/lib/sourcesEs.ts` while the English text matches exactly. Please add Spanish to the file itself (e.g. `{ "en": …, "es": … }` objects) and tell F the shape, so new or edited sources are translated too.
