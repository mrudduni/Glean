# Field Shift web app

This is the Next.js frontend for the Field Shift crop-rotation decision-support demo. It compares a farmer's current rotation with alternatives and makes the evidence gaps and local checks visible.

## Run locally

Use Node.js 20 LTS or later.

```bash
npm install
npm run dev
```

Open `http://localhost:3000`. To run the checks:

```bash
npm test
npm run typecheck
npm run build
```

The Leaflet basemap uses Esri World Imagery tiles and includes the required Esri attribution. It needs an internet connection.

## Sample data

The app loads data from `public/data/` only. It does not call live NASA, USDA, soil or weather APIs. Every included field boundary, observation, score, chart series and neighbor comparison is illustrative mock data. The banner stays visible while mock data is loaded. Do not use the sample values to make farm decisions.

Replace the mock files with schema-compatible outputs from the data pipeline when they are ready. Keep `_meta.mock` set to `true` until a file contains real, checked data. The Zod schemas in `lib/schemas.ts` validate fetched JSON in development. Data loading errors are surfaced in the relevant screen rather than treated as valid values.

## Assistant

The suggested questions use static responses from `public/data/field/{f1,f2,f3}/assistant_cache.json`. Free-text questions go through the only server route, `/api/ask`. Configure an OpenAI-compatible provider in a private environment file:

```dotenv
LLM_PROVIDER=openai-compatible
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=your-model-name
LLM_API_KEY=your-secret-key
```

Keep the key server-side. Never use a `NEXT_PUBLIC_` prefix. Without a configured provider, the route returns `503` and the field comparison remains available.

## Main paths

- `/` selects one of three demo fields.
- `/field/f1`, `/field/f2` and `/field/f3` open the field workspace.
- `/how-we-know` explains sources, evidence confidence and limitations.
- `/api/ask` validates assistant requests and serves cached or provider-backed answers.

The query string stores the field, water cap, climate scenario, five priority weights, equipment and market choices, and language. This makes a configuration shareable.

## Data sources in the demo

The source register is in `public/data/sources.json`. It links to NASA POWER, SMAP, GPM IMERG, MODIS/VIIRS, USDA Soil Data Access, USDA's Cropland Data Layer and USDA NRCS references. Links describe intended data roles; they do not imply that this demo has downloaded or validated those datasets.

The root `README.md` in this checkout does not contain the §7–9 data and assistant contract referenced by `3_FRONTEND.md`. This frontend therefore defines a local typed contract in `lib/types.ts` and `lib/schemas.ts`. Align these types with the shared contract when it is added. Do not change data-pipeline files from this frontend.
