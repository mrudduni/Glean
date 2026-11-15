# Frontend copy keys

The root README in this checkout does not include the §8.6 copy-key registry referenced by `3_FRONTEND.md`. This frontend uses the local EN/ES string catalogue in `public/data/content/copy.json` as its source of truth. It currently contains all app-owned UI copy, including the additional homepage, risk tooltip, mock-data and transparency strings introduced here.

| Key family | Where it is used | English text |
|---|---|---|
| `app.*`, `pick.*`, `home.*`, `map.*` | Site header, mock banner, field picker and map | See the corresponding English value in `public/data/content/copy.json`. |
| `field.*`, `nav.*` | Field selection, field workspace and section navigation | See the corresponding English value in `public/data/content/copy.json`. |
| `overview.*`, `headline.*` | Field overview, soil and climate panels | See the corresponding English value in `public/data/content/copy.json`. |
| `calendar.*` | Field calendar, climate-risk strip, cell tooltips and legend | See the corresponding English value in `public/data/content/copy.json`. |
| `priority.*` | Priority sliders, cap, climate scenario and equipment controls | See the corresponding English value in `public/data/content/copy.json`. |
| `strategy.*`, `why.*`, `evidence.*`, `benefit.*`, `gap.*`, `risk.*`, `confidence.*` | Strategy cards, scoring explanations and hidden reasons | See the corresponding English value in `public/data/content/copy.json`; templated values are filled from static data. |
| `replay.*` | Rotation replay chart and metric summaries | See the corresponding English value in `public/data/content/copy.json`. |
| `neighbors.*` | Farms Like Yours table and observational disclaimer | See the corresponding English value in `public/data/content/copy.json`. |
| `assistant.*` | Assistant drawer, chat controls and error states | See the corresponding English value in `public/data/content/copy.json`. |
| `trust.*`, `disclaimer.*`, `data.*`, `error.*`, `loading`, `not_available`, `units.*`, `lang.*` | Trust page, limitations, loading and shared UI | See the corresponding English value in `public/data/content/copy.json`. |

When the shared README key registry is available, reconcile these names and transfer the local strings to U's content files. Keep English fallbacks and Spanish translations together.
