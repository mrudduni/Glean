# Glean web app

Next.js 15 frontend for Glean. It shows one field's conditions, ranks crop rotations against the farmer's current one, and explains the evidence behind each number. It reads only the JSON files described in the team README, sections 7 to 9.

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

| Variable | Use |
|---|---|
| `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY` | Primary provider (Groq: `https://api.groq.com/openai/v1`). |
| `LLM_FALLBACK_PROVIDER`, `LLM_FALLBACK_BASE_URL`, `LLM_FALLBACK_MODEL`, `LLM_FALLBACK_API_KEY` | Optional second provider (Gemini: `https://generativelanguage.googleapis.com/v1beta/openai`). Tried once when the primary returns 429 or 5xx, or times out. |
| `ALLOW_CUSTOM_LLM_URL` | `1` lets users' own keys go to any https base URL. Off by default (SSRF guard). |

For `openai/gpt-oss` and Gemini models the route sends `reasoning_effort: "low"` and at least 1500 `max_tokens`. When no server provider answers (rate limit, error, empty answer or timeout), the drawer shows a short "busy" answer pointing to the suggested questions. Each IP may ask 20 questions a minute.

### Use my own key

The assistant drawer has a "Use my own key" panel (Groq, Gemini, or another base URL if the server allows it). The key stays in the browser tab (sessionStorage) and goes to `/api/ask` in the `x-user-llm-key`, `x-user-llm-base-url` and `x-user-llm-model` headers, never in the URL or body. The server uses it only for free-text questions, with the same prompt, facts and number check. It never logs or returns the key, and never falls back to the server key: if the user's provider rejects the key or is rate-limited, the drawer shows why.

## Code map

- `lib/types.ts`, `lib/schemas.ts`: contract types and zod mirrors.
- `lib/data.ts`: loaders and the mock flag.
- `lib/score.ts`: slider weights, exclusion and the shown-rotation pick (README §8.7).
- `lib/i18n.ts`: `t`, template `fill` and per-variable number formatting (README §7.4).
- `lib/numberCheck.ts`: finds numbers in an answer and matches them to facts. `tests/numberCheck.test.ts` also runs M's shared cases when `model/assistant/number_check_cases.json` exists.
- `app/api/ask/route.ts`: the assistant route.

Copy keys the app uses beyond README §8.6 are listed in `COPY_KEYS_ADDED.md`.
