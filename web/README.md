# Field Shift web app

Next.js 15 frontend for Field Shift. It shows one field's conditions, ranks crop rotations against the farmer's current one, and explains the evidence behind each number. It reads only the JSON files described in the team README, sections 7 to 9.

## Run locally

Use Node.js 20 or later.

```bash
npm ci
npm run dev
```

Open `http://localhost:3000`. Checks:

```bash
npm test
npm run typecheck
npm run build
```

The map uses Esri World Imagery tiles and needs an internet connection.

## Data

The app fetches everything from `public/data/`. It calls no live NASA, USDA, soil or weather APIs.

| Files | Owner | Branch |
|---|---|---|
| `fields.json`, `sources.json`, `field/*/{water,observed,neighbors}.json` | D | `role/data` |
| `crops.json`, `rotations.json`, `field/*/{summary,calendar,replay,strategies,validation,assistant_context,assistant_cache}.json` | M | `role/model` |
| `assistant/prompt.json`, `tests/fixtures/number_check_cases.json` | M (assistant) | `role/model-assistant` |
| `content/{copy,card_text,glossary,assistant_questions}.json`, `styles/tokens.{css,json}` | U | `role/content` |

To pull the latest files from all four branches and check them:

```bash
git fetch origin
bash scripts/import_upstream.sh
node scripts/validate_data.mts
```

A file with `_meta.mock: true` is a placeholder. While any such file is loaded in the browser, a banner at the top of the page says so.

`lib/data.ts` validates each file with the zod schemas in `lib/schemas.ts`. A file that does not match the contract logs `[data] <path> does not match the contract` in the console and still renders. Optional files (`validation`, `water`, `observed`, `neighbors`, `glossary`, `assistant_questions`) show a "not available" note when missing.

`scripts/mocks/` holds the generators used before the other roles pushed. Running them overwrites real files, so use them only for offline work.

## Assistant

Suggested questions are answered from `field/{id}/assistant_cache.json` without calling a model. Free-text questions go to `POST /api/ask`, which sends only the selected scenario's facts to an OpenAI-compatible chat endpoint, waits up to 20 seconds, and checks every number in the answer against those facts. Unverified numbers are marked in the UI.

Copy `.env.example` to `.env.local` and fill it in. Never commit keys.

| Variable | Groq | Gemini |
|---|---|---|
| `LLM_PROVIDER` | `groq` | `gemini` |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | `https://generativelanguage.googleapis.com/v1beta/openai` |
| `LLM_MODEL` | model id from the Groq console | Gemini Flash model id |
| `LLM_API_KEY` | Groq key | AI Studio key |

Without a key the route returns 503 `llm_unavailable` and the drawer falls back to the suggested questions. The route also limits each IP to 20 questions a minute.

## Code map

- `lib/types.ts`, `lib/schemas.ts`: contract types and zod mirrors.
- `lib/data.ts`: loaders and the mock flag.
- `lib/score.ts`: slider weights, exclusion and the shown-rotation pick (README §8.7).
- `lib/i18n.ts`: `t`, template `fill` and per-variable number formatting (README §7.4).
- `lib/numberCheck.ts`: finds numbers in an answer and matches them to facts. `tests/numberCheck.test.ts` also runs M's shared cases when `model/assistant/number_check_cases.json` exists.
- `app/api/ask/route.ts`: the assistant route.

Copy keys the app uses beyond README §8.6 are listed in `COPY_KEYS_ADDED.md`.
