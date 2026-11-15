# Field Shift: Space Apps 2026 submission draft

Paste each block into the matching field of the project page. Anything marked `TODO` needs a final value from the deployed app or from the other roles' docs (`docs/DATA_SOURCES.md` from D, `docs/AI_USE.md` and `docs/METHODS.md` from M). Check the 2026 rules before you submit, because field names and limits can change.

## Project name

Field Shift

## Challenge

Field Shift: Adapting Farms with NASA Data

## Team

Team Brackets. TODO: member names and roles (D data, M model and AI, F frontend, U design and content).

## High-level summary

Western Kansas farms depend on the Ogallala aquifer, one of the largest underground water reserves in the world, and in many places it is running down. In southwest Kansas, water levels drop by more than 1.5 feet a year in some areas (TODO: cite KGS or USGS source). Many farmers keep the same irrigated rotations because they lack field-specific evidence for alternatives.

Field Shift is a decision-support web tool that replays several crop rotations on 25 years of real daily weather for a farmer's actual field in Finney County, Kansas. It combines NASA POWER climate data, SMAP soil moisture, MODIS vegetation health, GPM IMERG rainfall, GRACE aquifer trends and USDA soil surveys into a side-by-side comparison. For each rotation it shows irrigation demand, stress days, income stability and wind-erosion exposure, including what happened in the 2012 and 2022 droughts.

A "Farms Like Yours" panel uses satellite observations from neighbouring fields that already farm differently. An AI assistant answers questions in plain English or Spanish, and every number it gives is checked against the source facts.

Field Shift does not tell farmers what to plant. It shows what the data says and lets them decide.

## Detailed description

### What does it do?

Field Shift helps a western Kansas farmer compare their current crop rotation with three other options. The farmer picks a field on a map, sets priorities (save water, steady income, soil health, erosion control) and limits (for example, a seasonal pumping limit), and sees four strategy cards. Each card explains why it was suggested, what evidence supports it, its possible benefits, where information is missing, and the risks to check locally. No card is called a winner. Each one says here is the trade-off, you decide.

Screens: pick a field, overview, Field Calendar, plan (priorities and cards), Rotation Replay, Farms Like Yours, assistant, and a "How we know" page with sources, trust badges and a glossary.

### How does it work?

- **Data pipeline (Python).** Scripts fetch and clean more than 10 datasets for three demo fields in Finney County: an irrigated center pivot, a dryland field and a sandy, wind-prone field. NASA POWER gives daily weather. SMAP gives root-zone soil moisture. MODIS tracks vegetation every 16 days. GPM IMERG gives rainfall. GRACE and GRACE-FO show aquifer storage change. SSURGO gives soil texture, water-holding capacity and wind erodibility. USDA Crop Sequence Boundaries show what each field and its neighbours have grown.
- **Model layer (Python).** The Rotation Replay engine runs each option on the field's daily weather from 2000 to 2025 with an FAO-56 daily water budget. Each year it estimates irrigation needed, crop stress days, yield and income, and bare-soil exposure. A wind-erosion index combines bare days, strong-wind days and soil erodibility. The model is checked against OpenET and SMAP.
- **Crop settings.** Values come from FAO-56 and FAO-33 tables and K-State Research and Extension planting guides, each cited in `content/crops.yaml`.
- **Frontend (Next.js on Vercel).** The app reads precomputed JSON and scores in the browser, so the sliders respond at once. Every farmer-facing sentence is a template with placeholders, so no number is typed by hand into the text.
- **Farms Like Yours.** The tool finds about 100 to 150 nearby fields with similar soil and irrigation that run a different rotation, then compares their OpenET water use and MODIS greenness in dry years. It always shows the number of fields and says the comparison is observational, not proof of cause.
- **AI Field Assistant.** A plain-language chat in English and Spanish (TODO: confirm provider) that uses only the field's computed facts. Each number is checked against those facts. Verified numbers show their source, and unverified numbers are flagged. Six common questions have saved answers.

### What benefits does it have?

- **Water savings in view.** Each card shows estimated irrigation change per season in mm and inches, which relates to water-right limits.
- **Drought stress test.** Farmers see how each rotation did in dry years such as 2012 and 2022.
- **Wind erosion in view.** Bare-soil exposure to wind is often missing from crop tools but matters on sandy Finney County soils.
- **Neighbour evidence.** Satellite observations of nearby fields add real-world context beyond model output.
- **Honest uncertainty.** Every card has a gaps section and a local-risks section. The wording is cautious, for example "may" rather than a promise.

### What is the intended impact?

The Sheridan 6 Local Enhanced Management Area in Kansas reported that modest crop switching plus efficiency gains cut water use and slowed depletion (TODO: add the exact figures only after checking them against the Kansas Division of Water Resources or K-State source; do not quote numbers from memory). Farmers still need field-specific evidence to make a switch with confidence. Field Shift offers that evidence as a transparent comparison grounded in the farmer's own soil and weather, not as a mandate. TODO: add the final water-saving figure for each demo field once the real model run is in.

### How is it creative?

1. **Wind-erosion lens.** Most rotation tools ignore wind erosion. In sandy southwest Kansas it is a major risk, so we estimate it from bare days, wind days and soil erodibility.
2. **Replay on real weather.** Instead of using average climate, we replay each rotation on 25 years of actual daily weather. Farmers see the worst years, not only the averages.
3. **Satellite neighbour comparison.** We show what is happening on similar nearby fields, not only what a model estimates.
4. **Visible honesty.** Every assistant answer has number checks and source tags, and uncertainty is part of the design.

### What factors did your team consider?

- **Farmer trust.** Plain language at about an 8th-grade level, no overclaiming, and every number traced to a source.
- **Bilingual access.** All farmer-facing text is in English and Spanish, since many farm workers in western Kansas speak Spanish. The Spanish was written with AI help (TODO: native-speaker check).
- **Phones and sunlight.** Large type, high contrast, and colours checked for common colour blindness.
- **Scientific validity.** FAO-56 is the international standard for crop water budgets, and we compare the model with OpenET and SMAP.
- **Honest limits.** We list what we lack (pest counts, full costs, herbicide carryover, crop insurance details) as clearly as what we have.

## Tools, languages and libraries

- Python 3.11 (pandas, numpy, geopandas, shapely, xarray, rasterio, pyet) for the data and model.
- Next.js (App Router), React, TypeScript, Tailwind, shadcn/ui, react-leaflet and Recharts for the web app, hosted on Vercel.
- Gemini Flash through an OpenAI-compatible endpoint, with Groq as a fallback, for the assistant. TODO: confirm which one is live.
- GitHub for version control. TODO: confirm the repo licence before stating one.
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
