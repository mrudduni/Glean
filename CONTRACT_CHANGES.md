# Contract changes, 2026-11-15

The web (F) session made these changes at the user's request, to fix mismatches between the README data contract and what each role publishes. Read this after you pull. Each entry says what changed, where, and why.

README sections are cited as in the team README (`README.md` on main, same as `~/.fieldshift/README.md`).

## Changes to the contract (README text)

The main session applies these to `README.md` on main. Until then, treat this file as the source of truth for these points.

| # | README section | Change | Why |
|---|---|---|---|
| C1 | 8.4 `Fact` | `value: number \| null`. A fact with `value: null` is text only (for example "The field is irrigated."). The number check ignores it. | M's real `assistant_context.json` has text-only facts. Without this rule, `Math.abs(null)` is 0 and an answer saying "0 mm" would be marked verified. |
| C2 | 8.5 `CropTraits` | `family: string \| null`, `root_type: ... \| null`. "None" for `plant_window`, `harvest_window` and `heat` is written as `null`, not as an object of nulls. | Fallow has no family or root type. crops.yaml wrote `{ stage: null, tmax_c: null }`, which fails the type `{...} \| null`. |
| C3 | 8.6 `headline.well_trend` | `m_per_yr` is the trend of depth to water, as in `water.json` wells. Positive means the water table is falling. Templates must read correctly for either sign. | The old template said "the water level changing by 1.8 m", which reads as a rise. |
| C4 | 8.7 tie-break | "ties → lower irrigation_mm_mean" uses `replay.scenarios[scenario][rotation].summary.irrigation_mm_mean`. | `irrigation_mm_mean` is not in `StrategyEntry`. |
| C5 | 8.7 shown | An alternative whose steps equal R0's steps, allowing a different starting year, is dropped. It is not shown and not counted as hidden. See C13 for filling the row to R0 + 3. | f2's R0 equals R2 and f3's R0 equals R1 (from model-core). Showing them as alternatives compares a rotation with itself. |
| C6 | 8.6 `card.hidden_count` | `{n}` counts excluded alternatives plus feasible ones ranked below the top 3. Duplicates of R0 (C5) are not counted. | The README did not say which set `n` counts. |
| C7 | 8.6 copy keys | The 94 keys in `web/COPY_KEYS_ADDED.md` are part of the catalog. `calendar.odds` takes `{risk}` and `{count}`. | The web app uses them. Spanish users saw English for all of them. |
| C8 | 9 number check | The rules in `REFINEMENTS` in `model/assistant/number_check.py` are part of the contract, plus one new rule: digits glued to a letter, digit, underscore, dot or `$` are part of an identifier (R2, cap300), not a number. `number_check_cases.json` is the shared test. | The README regex alone splits "2016" into "201" and "6" and reads "R2" as the number 2. |
| C8b | 9 number check | Web adds three stricter rules (not yet in the Python port): an inch mark right after a number (`11.8"`, `11.8″`) is inches; a number with no unit and no `$` matches only facts whose unit is null, `days` or `years`; a number with decimals never matches a whole-number fact with a null unit (a count). | Live: a bare "11.8" from a cut-off answer verified against `neighbors.continuous_corn.n` (12). M: port these to `number_check.py` and add the cases. |
| C9 | 9 provider call | `POST /api/ask` may return `429 { error: "rate_limited", message }` after 20 requests a minute from one IP. For model ids starting `openai/gpt-oss` and for Gemini (both reasoning models) the route sends `reasoning_effort: "low"` and `max_tokens: max(prompt.max_tokens, 1500)`, because reasoning tokens count against `max_tokens` and left `content` empty. An empty answer, or one with `finish_reason: "length"` (cut off), is never shown: it is retried once with `max_tokens: 3000`, then the fallback provider is tried. A provider 429 with `Retry-After` of 8 s or less is retried once. | Groq free tier: about 8k tokens a minute for gpt-oss-120b, and empty answers seen live. |
| C10 | 9 `notice` and fallback | When the provider is still rate-limited, the route answers `200` with a short "assistant is busy, use a suggested question" text (`copy.assistant.busy` if present), `cached: true`, `provider: "cache"`, `model: "none"`, no numbers. `using_cache` is not sent. `scenario_mismatch` is sent when a cached answer is served for a scenario other than `cap300\|actual`. This also covers server errors, empty answers, timeouts and 4xx from the server providers, after the fallback was tried. Only a user's own key gets `503 llm_unavailable` with the reason. | The user sees a reason and the chips, not an error. |
| C16 | 9 step 2 facts | Facts sent to the model: those with no scenario or the request's scenario, and, when `top_rotations` is given, rotation facts only for R0 and those rotations. | Keeps the facts block near 1.7k tokens (f2), well under the free-tier limit. |
| C11 | 8.3 `neighbors.json` | `groups` may have no entry with `is_current: true` when no nearby field matches the field's rotation class. The UI then marks no row "Like yours". | f3 (corn, wheat, sorghum) has no matched neighbours in that class. |
| C13 | 8.7 shown | The card row always shows R0 + 3. When fewer than 3 alternatives fit, the best-scoring excluded ones fill the row (ties: lower irrigation). Each filled card shows its `card_text.infeasible` reason as a badge, plus what would include it (`card.unlock_tick` with the equipment or forage-buyer option, or `card.unlock_cap` with the lowest water limit that fits). Filled cards are not counted in `card.hidden_count`. | Rule from main: every field shows at least 3 strategies. f2 had only R0 after C5. |
| C14 | 8.7 why bullets, 8.6 benefits | `why.water_use` is never a why bullet when its `saved_mm` < 0 (the next criterion is used). `benefits.water_saved` is not shown when `saved_mm` < 0. | The templates say "saved"; a negative value would read as a saving. Rule from the content session. |
| C15 | 8.6 copy | `neighbors.n_fields` (`{n} fields`) is rendered per row with `{n}`. The column header uses a new key, `neighbors.fields_header`. `card.hidden_count` is rendered with `{n}`. | Both keys contain `{n}`; as a header the placeholder showed raw. |
| C17 | 9 providers | `AskResponse.provider` may also be `"custom"` (a user's own endpoint). Server env may add `LLM_FALLBACK_*`, tried once after a 429, 5xx, empty answer or timeout from the primary. Production: Gemini `gemini-3.5-flash` primary, Groq `openai/gpt-oss-120b` fallback. `provider` names the one that answered. A request may carry the user's own key in headers `x-user-llm-key`, `x-user-llm-base-url`, `x-user-llm-model`: used for free text only, https only, hosts api.groq.com and generativelanguage.googleapis.com unless the server sets `ALLOW_CUSTOM_LLM_URL=1`, never logged or echoed, no fallback to the server key (user failures return 503 with the reason). | User asked for bring-your-own-key and a Gemini backup while Groq is at its daily cap. |
| C12 | 8.3 `sources.json` | Lists only sources whose data reached `out/`. A tag cited elsewhere but absent from `sources.json` renders as a plain chip with no link. | D's design: MODIS, SMAP and IMERG are listed once data-earthdata lands them. |

## Changes made in each role's branch

| Branch | Commit | Files | Change |
|---|---|---|---|
| role/content | 3c740c7 | `content/copy.json` | Added the 94 keys from `web/COPY_KEYS_ADDED.md` with `en` and `es`. |
| role/content | 3c740c7 | `content/crops.yaml` | `heat`, `plant_window`, `harvest_window` written as `null` when absent (C2). U had already fixed the `well_trend` wording (C3) in 846e3b5. |
| role/content | 3c740c7 | `content/validate.py` | `calendar.odds` may use `{risk}` and `{count}`. |
| role/model-assistant | 0286397 | `model/assistant/number_check.py`, `number_check_cases.json` | Identifier lookbehind (C8) and two shared cases. All 38 tests pass. |
| role/model | 0cf12fa | `model/calendar/build.py`, `model/replay/economics.py` | Read `c["heat"]` as possibly `null` (C2). Without this, M's next run would crash on the new crops.yaml. |
| role/web | this commit | `web/**` | Schema accepts C1 and C2. Number check skips text-only facts. R0 duplicates dropped (C5). Route retries once on a short provider 429 (C9). Copy fallbacks match copy.json. |

## What each role does on pull

- **D (data):** nothing required. When MODIS, SMAP or IMERG data lands, `build_sources.py` lists them and the chips get links.
- **M (model-core):** pull role/model, then re-run `python model/run_all.py` so `crops.json` has `null` for absent heat and windows. Keep the null-safe `heat` reads.
- **M (model-assistant):** pull role/model-assistant, then rebuild `assistant_context.json` on role/model 0cf12fa so fact values match the new outputs. When adding number-check rules, add a shared case and run `npm test` in `web/` too.
- **U (content):** pull role/content. Add new UI keys to `copy.json` and `web/COPY_KEYS_ADDED.md` together. Keep crops.yaml "none" values as `null`.
- **Main:** apply the C1 to C17 and C8b rows to `README.md`, then merge role/web.

## Data gaps left open

These need new data, not a contract change. They belong to data-earthdata.

- `observed.json`: `ndvi` and `ecostress` arrays are empty, and `precip_check` IMERG values are null. The neighbour drought columns show "—" until they arrive.
