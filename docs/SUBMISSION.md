# Field Shift: Space Apps 2026 submission draft

Paste each block into the matching field of the project page. Anything marked `TODO` needs a final value from the deployed app or from the other roles' docs (`docs/DATA_SOURCES.md` from D, `docs/AI_USE.md` and `docs/METHODS.md` from M). Check the 2026 rules before you submit, because field names and limits can change.

## Project name

Field Shift

## Challenge

Field Shift: Adapting Farms with NASA Data

## Team

Team Brackets. TODO: member names and roles (D data, M model and AI, F frontend, U design and content).

## High-level summary (about 200 words)

Field Shift helps a farmer in western Kansas compare their current crop rotation with three other options. It starts from a real field. It reads the field's crop history from USDA maps and its soil from SSURGO, then shows a calendar of what is in the ground each month and when heat, frost, dry spells and wind are most likely.

The farmer sets priorities (save water, steady income, soil health, erosion control) and limits (such as the most irrigation water they can use in a season). Field Shift then shows their current rotation and the three closest-matching options. Each card explains why it was suggested, the evidence, the possible benefits, the information we are missing, and the risks to check locally.

The evidence comes from Rotation Replay, which runs each rotation on the field's own daily weather from 2000 to 2025 using the FAO-56 water balance, and from Farms Like Yours, which compares nearby fields on similar soil that already use other rotations, using OpenET and MODIS. A plain-language assistant answers questions in English and Spanish. It only sees the field's computed facts, and it marks every number as verified or unverified.

Field Shift supports a farmer's judgement. It does not replace it or local expert advice.

## Detailed description

### What it does

- **Pick a field.** Three example fields in Finney County, Kansas: an irrigated pivot on clay loam, a dryland wheat, sorghum and fallow field, and a pivot on sandy soil that is prone to blowing.
- **Overview.** Current rotation, soil, how the climate has shifted since 1991 to 2020, and the groundwater outlook from GRACE satellites and nearby wells.
- **Field Calendar.** Twelve months by rotation year, coloured by crop or bare ground, with the 25-year odds of heat, frost, dry spells, storms and wind laid on top.
- **Plan.** Five priority sliders, a seasonal irrigation limit, a hotter and drier weather test, and equipment and forage-buyer checks. Four strategy cards respond at once.
- **Rotation Replay.** Irrigation need, crop stress days, income before costs and bare-ground days for each rotation, year by year, with dry years marked.
- **Farms Like Yours.** Nearby fields on the same soil and irrigation setup, grouped by rotation, with their satellite-measured water use and greenness in dry years. We show the number of fields and say the comparison is observational.
- **Assistant.** Ask in English or Spanish. Six suggested questions have saved answers so the app still works if the language model is down.
- **How we know.** Data sources, satellite-versus-ground agreement badges, and a plain-language glossary.

### How it works

1. Python scripts download and clean NASA, USDA and other data for each field outline.
2. A daily soil water model (FAO-56) runs each rotation on 25 years of weather and produces the numbers for the cards.
3. All results are written as static JSON files. The app reads them in the browser, so scoring responds instantly and nothing is fetched live during a demo, except the assistant.
4. The assistant prompt is built from the field's computed facts. A number check compares each number in a reply with those facts.
5. Crop settings come from FAO-56 and FAO-33 tables and K-State Research and Extension planting guides. Every farmer-facing sentence is a template with placeholders, so no number is typed by hand into text.

### Benefits

- Gives farmers a side-by-side view of water, income, soil and risk instead of one verdict.
- Shows what is unknown (gaps) and what to check locally (risks) on every card.
- Works in English and Spanish, with a glossary that explains satellite terms in plain words.
- Uses open data and open methods, so an extension agent can check the work.

### Intended impact

Water saved is shown per field in mm and inches. The tool is meant to start a better conversation between a farmer and an extension agent about adapting to a declining aquifer, hotter summers and wind-blown soils. The method can move beyond Kansas with global datasets such as ERA5 and GLDAS. TODO: add the final water-saving figure for each demo field once the real model run is in.

## Tools, languages and libraries

- Python 3.11 (pandas, numpy, geopandas, shapely, xarray, rasterio, pyet) for the data and model.
- Next.js, TypeScript, Tailwind, react-leaflet and Recharts for the web app, hosted on Vercel.
- Google Gemini or Groq through an OpenAI-compatible endpoint for the assistant. TODO: confirm which one is live.
- Fonts: Fraunces, Source Sans 3 and IBM Plex Mono from Google Fonts.
- Design checks: WCAG contrast check and a colour-blind simulation script (`design/check_cvd.py`).

## NASA data used

Fill the final list from D's `docs/DATA_SOURCES.md`. Planned list:

| Dataset | What we use it for | Link |
|---|---|---|
| NASA POWER daily weather | Replay weather, reference ET, heat, frost and wind days | https://power.larc.nasa.gov/ |
| MODIS NDVI (MOD13Q1) via AppEEARS | Crop greenness, bare windows, dry-year greenness | https://appeears.earthdatacloud.nasa.gov/ |
| SMAP L4 root-zone soil moisture | Check on modelled soil water | https://nsidc.org/data/spl4smgp |
| GPM IMERG | Storm days and a rainfall cross-check | https://gpm.nasa.gov/data/imerg |
| GRACE and GRACE-FO | Groundwater storage trend | https://grace.jpl.nasa.gov/ |
| ECOSTRESS | Plant water stress snapshots (if used) | https://ecostress.jpl.nasa.gov/ |
| SRTM | Slope and low spots | https://www.earthdata.nasa.gov/data/instruments/srtm |
| HLS (Landsat and Sentinel-2) | Sharper greenness (if used) TODO | https://hls.gsfc.nasa.gov/ |
| OpenET (built on Landsat) | Check on modelled water use, neighbour water use | https://openetdata.org/ |

## Space agency partner data

TODO: list Sentinel-2 (ESA) only if it is used, for example through HLS or as a basemap. Otherwise write "None".

## Other data

- USDA NASS Quick Stats (yields, prices, acres): https://quickstats.nass.usda.gov/
- USDA Crop Sequence Boundaries and Cropland Data Layer: https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/
- USDA NRCS SSURGO via Soil Data Access: https://sdmdataaccess.nrcs.usda.gov/
- USGS groundwater levels: https://waterdata.usgs.gov/
- PRISM climate data, if used: https://prism.oregonstate.edu/
- FAO Irrigation and Drainage Paper 56 and 33: https://www.fao.org/4/x0490e/x0490e00.htm and https://www.fao.org/4/i2800e/i2800e.pdf
- K-State Research and Extension, Kansas Crop Planting Guide: https://bookstore.ksre.ksu.edu/pubs/kansas-crop-planting-guide_L818.pdf

## Use of AI

Fill from M's `docs/AI_USE.md`. Draft:

- **In the app.** A large language model (TODO: model name and provider) answers questions in plain language. It receives only the field's computed facts, each with a source tag. A number check marks each number in a reply as verified (matches a fact) or unverified. Suggested questions use saved answers. The assistant does not make decisions and always points to the extension agent.
- **In building the app.** TODO: list the AI tools used for planning, coding, writing and translation. Say which parts a person reviewed. The Spanish text was written with AI help and should be checked by a native speaker. TODO: record who checked it.
- **Not used for.** Data values, model results and crop settings. These come from the datasets and published tables above.

## Links

- Live app: TODO https://...vercel.app
- GitHub repo: https://github.com/mrudduni/Team-Brackets
- Video or slides: TODO
- Methods: `docs/METHODS.md` in the repo

## Final checks before submitting

- [ ] Format matches the 2026 rules (video length or slide count).
- [ ] No NASA logos or insignia in the app, video or slides.
- [ ] Repo is public, no API keys committed, and `scripts/check_contract.py` passes with no mock files.
- [ ] The app shows no "Showing sample data" banner.
- [ ] Every number quoted in this text matches the deployed app.
