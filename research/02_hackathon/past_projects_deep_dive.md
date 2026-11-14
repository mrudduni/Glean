# Past agriculture projects: what teams actually built

This file goes one level below `past_winners.md`. For each past agriculture project I could find, it records what the code does, which NASA data the code really loads, and how the data reaches the user. I read source files through the GitHub API on 2026-11-14. I did not run any downloaded code.

Most 2024 and 2025 project tabs on spaceappschallenge.org still show "make sure you are logged in" without a login. The one exception is Zumorroda-X, whose 2025 project tab loads in full. For other teams I used CrafterWIKI, a third-party index whose curator read the project tabs on 2026-09-14 and quotes them with sources. I mark facts from CrafterWIKI as "per CrafterWIKI". Space Apps sites for 2019 to 2022 are public, so their project pages load without login.

A note on the word "result": I only state an award when an official page or news report ties the team to it. A repo is tied to a team only when its name, description, homepage or the project page links them. Where that link is weak, the row says "not confirmed".

## Summary table

| Project (team) | Year | Challenge | Result | Repo | Stack | NASA data truly used in code | Live vs static | ML / SI | UI |
|---|---|---|---|---|---|---|---|---|---|
| 2Plant or not 2Plant (NVS-knot) | 2024 | Agricultural Decision-Making | Global winner, Galactic Impact | yaroslav-prokipchyn/2plantORNOT2plant | Java Spring, Python Flask, React, AWS CDK, Postgres | Assimilated surface and root-zone soil moisture with uncertainty, read from NetCDF files that an outside pipeline makes (SMAP/AMSR2 per CrafterWIKI). No NASA API call in this repo | Pipeline output on S3, plus bundled sample NetCDF from December 2023 | Physics filter, no ML | Field map and charts, multi-tenant web app |
| WaterWise (GaamaRamma) | 2024 | Agricultural Decision-Making | Global winner, Best Use of Data | gabe-engineers/nasa-hackathon-2024 | Next.js, TypeScript, Leaflet, Vercel | OpenET SSEBop daily ET (Landsat-based, not a NASA archive) via live API. Rain comes from Open-Meteo, not NASA | Live API calls per request | GPT-3.5 assistant chatbot only | Draw a field, get a 7-day watering schedule |
| Gajini (가지니) | 2024 | Agricultural Decision-Making | Global finalist | nasa-gajini/gajini-api, gajini-ml, gajini-web | Python, h5py, pydap, OpenAI, Next.js, MUI | SMAP L3 enhanced (SPL3SMP_E), MODIS MOD13C1 NDVI, FLDAS ET from local files. GPM IMERG and MODIS LST through OPeNDAP in test scripts. ECOSTRESS loader is an empty stub | Mostly pre-downloaded files for 1 to 3 August 2024, Egypt only | GPT-4 prompt picks a crop and writes an irrigation plan | Stepper web app with a map rectangle |
| FarmVis (likely team FarmVis) | 2024 | Agricultural Decision-Making | Honorable mention (team); repo link not confirmed | sahusgupta/farmvis | Streamlit, pydeck, scikit-learn | None loaded by code. NASA soil moisture only as an embedded ArcGIS web map | Live Esri Living Atlas feeds (US Drought Monitor, NWS warnings) | DBSCAN clustering of warnings | Streamlit dashboard |
| Farmalytics | 2024 | Not confirmed | Not confirmed | ahmadkammonah/Farmalytics | Static HTML, Leaflet, Flask, XGBoost notebook | GLDAS Noah subsets (bundled .tif and .nc4) converted to GeoJSON | Static bundled files | XGBoost on a CSV named nasa.csv that holds soil-landscape fields, not NASA data | Leaflet map with one overlay and a chatbot |
| Henry's Farm Adventures (Zumorroda-X) | 2025 | Farm Navigators | Global winner, Art & Technology | esralsayed/Henry-s-Farming-Adventure-Game (fork of a deleted repo) | Phaser 3, vanilla JS, Python | One IMERG HDF5 file turned into a JSON rain grid, a bundled heat map GeoTIFF, Landsat before/after images, NDVI tiles from a third-party tile server | Mostly static assets. NDVI tiles fetched live | Random forest trained offline in Python. The game shows a simulated prediction instead | 2D pixel-art story game |
| FarmNavigators (org Nasa-FarmNavigators) | 2025 | Farm Navigators | Not confirmed | Nasa-FarmNavigators/* (6 repos) | FastAPI, NestJS, Next.js, React Native, Godot | NASA POWER daily point API only. README also lists AppEEARS, Crop-CASMA, GLAM and Giovanni, which the code does not call | Live POWER call, but farm coordinates are hardcoded to Luanda | "Farm Tinder" score from rules | Web, mobile and Godot game, all partial |
| CodeForSeedney (Code for Sydney) | 2025 | Farm Navigators | Not confirmed | Code-for-Sydney/CodeForSeedney | Godot 4, web export | SMAP top-layer values typed into a JSON file in 0.05 steps | Static, hand-entered | None | Tile-based farm game |
| Farm Quest | 2025 | Farm Navigators | Not confirmed | acciomo/nasa-spaceapps-hackathon | Next.js, NextAuth | None found. Farms are a hardcoded list of places | Static | None | Globe picker and farm view |
| Project L.L.O.C.U.S.T. | 2020 | Automated Detection of Hazards | Global winner, Galactic Impact | kvnyng/Project-L.O.C.U.S.T | Python, scikit-learn, Leaflet, Netlify | Worldview snapshot images of SMAP L4 soil moisture and soil temperature, MODIS Terra NDVI 8-day, ASTER GDEM | Static CSVs and model files | Random forest and SVM on pixel colours | Map with risk heat maps and wind flow |
| Tanom (Team Ookami) | 2022 | Earth Data Analysis Developers Wanted | No award found | None linked | Canva mock-up, matplotlib | NASA POWER single point, per the team | Not confirmed | None | Design mock-up only |

## Per-project notes

### 2Plant or not 2Plant (NVS-knot), 2024, Galactic Impact

- **Who.** NVS-knot was a joint team of Nave Analytics, VITech and Sparrow, competing from Kyiv ([nation.ge](https://nation.ge/?m=5&news_id=34213)). Nave Analytics is a Nebraska agtech startup that already sold satellite irrigation tools. The idea came from a farmer asking where his tractor would get stuck in wet spring fields ([Silicon Prairie News](https://siliconprairienews.com/2025/02/nebraska-startup-wins-nasas-galactic-impact-award-in-the-2024-space-apps-challenge)).
- **What it does.** It gives two weeks of daily planting windows. Each day gets a poor, fair, good or best rating from moisture sufficiency and saturation risk at 15 cm, with a "second opinion" tab that shows raw moisture and uncertainty. Per CrafterWIKI, the team fused SMAP/AMSR2 surface moisture, ET and forecast ensembles with an exponential filter, and reported about 0.03 m³/m³ root-zone error and 0.64 mm daily ET error against ground truth ([CrafterWIKI](https://crafterwiki.com/projects/2plant)). The NASA write-up says it used surface soil moisture and evapotranspiration ([NASA](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-international-space-apps-challenge-announces-2024-global-winners/)).
- **Repo tie.** The repo name matches the app name, and the Python package is `nave_analytics`, which matches the team's company. I treat the link as strong but the team did not link the repo from a public page I could read.
- **What the code shows.** The repo has one commit (6 October 2024) but holds a full product: a Spring backend with database migrations dated February to May 2024, Playwright end-to-end tests, AWS CDK stacks with Cognito, and a Flask analytics service. So most of the code predates the hackathon.
- **Data path.** `planting_conditions.py` and `soil_moisture_content.py` read NetCDF "blocks" (weather, bottom-layer, soils) per field and compute charts. Variables include `assim_sz_sm_est` and `assim_rz_sm_est` (assimilated seed-zone and root-zone moisture), their sigma, field capacity and wilting point. A Java `GranuleImporter` pulls new granules per organisation from S3. Sample NetCDF files dated December 2023 are committed in `data/`. No code in this repo calls Earthdata, so the satellite processing happens in a pipeline outside the repo.
- **Science in the UI.** The chart draws a target band between 55 and 80 percent of plant-available water, and shows plus or minus one sigma around the estimate. This is a real uncertainty display.
- **Quality.** Strong engineering. Weak hygiene: a committed `venv/` folder and seeded test users.
- **Licence.** None.
- **Demo.** The demo link `https://nasa.nave-app.com/list-view` (per CrafterWIKI) failed to load for me.

### WaterWise (GaamaRamma), 2024, Best Use of Data

- **What it does.** A farmer draws a field on a Leaflet map, picks a crop, a growth stage and a pump flow rate, and gets daily water needs and a time to stop irrigating each night ([CrafterWIKI](https://crafterwiki.com/projects/waterwise/)). The live demo at https://nasa-hackathon-2024-nine.vercel.app/ still loads.
- **Repo tie.** The repo's homepage is that demo URL and its description says it won the Data Award ([repo](https://github.com/gabe-engineers/nasa-hackathon-2024)). 78 commits from 5 to 7 October 2024, 4 contributors, no licence.
- **Data path.** `getET.ts` POSTs the polygon to `openet-api.org/raster/timeseries/polygon` with model SSEBop and an API key kept in an environment variable. `precipitation.ts` calls the Open-Meteo forecast API. All data is live per request.
- **Method.** Daily water = (Kc × ET − rain) × area. Kc values come from a 35-crop table with three stages (Seedling, Adult, Elderly).
- **Flaws I found by reading the code (not tested).**
  - SSEBop ET is already actual crop ET. Multiplying it by a crop coefficient applies the crop factor twice. The FAO-56 method multiplies Kc by reference ET instead.
  - ET covers the past seven days, while rain covers the next seven days. The code pairs day i of one with day i of the other.
  - `calculateArea` converts degrees to radians, then multiplies by (π/180)² again, and skips the cosine of latitude. That seems to shrink the area by a factor of about 3,300.
- **Lesson.** The judges rewarded one clear, recurring farmer decision with a visible formula, even with these errors in the code. Judges probably do not read the code, but a careful reviewer could find these errors in minutes.

### Gajini (가지니), 2024, Global finalist

- **Repo tie.** All three repos describe themselves as "Gajini - 2024 NASA Space Apps Challenge - Leveraging Earth Observation Data for Informed Agricultural Decision-Making" ([gajini-api](https://github.com/nasa-gajini/gajini-api), [gajini-ml](https://github.com/nasa-gajini/gajini-ml), [gajini-web](https://github.com/nasa-gajini/gajini-web)). Commits: 3, 25 and 53, from 28 September to 6 October 2024. No licences.
- **Data path.** `all_data.py` loads three SMAP L3 enhanced files for 1 to 3 August 2024 and one MODIS MOD13C1 file from disk, then merges the days. `ET.py` reads an FLDAS Noah monthly file for August 2024. `gpmL3.py` and `modis.py` open IMERG and MOD11A1 LST through OPeNDAP with an Earthdata bearer token. `test_earth_access.py` shows a working `earthaccess` search for SPL3SMP_E. `ecostress.py` defines a class and loads nothing.
- **Earthdata auth.** Two scripts hardcode a full Earthdata Login JWT in source. This is the clearest secret-handling failure I found.
- **Scientific handling.** `remove_outlier` turns fill values (−9999) into 0.0, so missing soil moisture becomes "bone dry".
- **Recommendation.** `open_ai_core.py` puts ten pixel values (ET, soil moisture, vegetation water content, clay fraction, NDVI and others) into a GPT-4 prompt. It asks the model to "recommend one crop" and to write an irrigation plan. The crop list in that prompt (wheat, rice, corn, barley, oats, banana) differs from the list in the web app (wheat, cotton, corn, chickpeas, barley, date palms).
- **Framing.** The team page describes Korean farm drought, but the code and boundary file cover Egypt only (`geoBoundaries-EGY-ADM0.geojson`).
- **Takeaway.** This is the only past entry I found that recommends a crop. It used an LLM to choose, with no agronomic rules, no evidence and no stated uncertainty.

### FarmVis, 2024, Honorable mention (repo link not confirmed)

- **Repo tie.** The team was from Tompkins High School ([team page](https://www.spaceappschallenge.org/nasa-space-apps-2024/find-a-team/farmvis/)). The repo `sahusgupta/farmvis` was created 5 October 2024 by a user in Katy, Texas, where Tompkins High School is. Nothing in the repo names the team, so the link is "not confirmed".
- **What the code does.** 21 commits from 5 to 7 October 2024. `droughtData.py` and `warningsData.py` query live Esri Living Atlas feature services for the US Drought Monitor and NWS flood warnings, and `warningsData.py` clusters the warnings with DBSCAN. `soilMoistureMap.py` embeds an ArcGIS web map titled "NASA soil moisture" in an iframe. No code reads a NASA file or API. The Streamlit app (https://farmvis1.streamlit.app/) timed out when I tried it.

### Farmalytics, 2024 (result not confirmed)

- **What the code does.** 22 commits, MIT licence ([repo](https://github.com/ahmadkammonah/Farmalytics)). Small GLDAS subsets are bundled and converted to GeoJSON by `dataConverter_tiff.py`. The map loads one static file labelled "Groundwater runoff".
- **ML.** The notebook trains XGBoost on `nasa.csv`. Its columns (`SOIL_LANDSCPE_ID`, `RSN_CLASS`) look like a soil-landscape dataset, not NASA data.
- **Secret.** A `.env` file with an `OPEN_AI_KEY` line is committed. I did not check whether the value was a real key.
- **Takeaway.** This shows two common failure modes: a dataset given a NASA-sounding name, and secrets in the repo.

### Henry's Farm Adventures (Zumorroda-X), 2025, Art & Technology

- **What it is.** A story game. Henry visits farmers facing the 2021 India heat, the 2022 Pakistan floods, salinisation in Egypt, drought in the US, and CO₂ and crop management in Brazil. Each stop has a mini-game ([project page](https://www.spaceappschallenge.org/2025/find-a-team/zumorroda-x/?tab=project)). The project page names Landsat before/after imagery, NDVI through APIs, the US Drought Monitor, NASA Harvest GLAM, and SEDAC data. The live game at https://henrysfarmadventures.vercel.app/ loads.
- **Repo.** The project page links `esralsayed/test_farmy`, which redirects to `esralsayed/Henry-s-Farming-Adventure-Game`. It is a fork of `AlaaAbdelnase/test_farmy`, which now returns 404. 10 commits, all on 5 October 2025. No licence.
- **Data path.**
  - `imerg_to_game_json.py` reads one bundled IMERG HDF5 file, downsamples it by 10 and normalises it into `raingrid.json`, which the flood level loads.
  - A heat map GeoTIFF and a drought map JPEG are bundled as assets.
  - `NDVImap.js` searches back up to 30 days for a daily VIIRS VNP09H1 NDVI preview tile on an AWS App Runner host. The host is not a NASA server, and its base path returned 404 for me.
- **ML gap.** `ai.py` trains a random forest on `the_excel.xlsx`, which looks like the SEDAC GISS crop-climate table (wheat, rice, coarse grains and protein feed by region, CO₂ effect and adaptation level). The game never calls that model. In `waterScene.js`, `getAIPrediction()` waits two seconds and then calls `generateRealisticPredictions()`, which adds hardcoded per-country offsets. A comment says the real AI server can be set up later. `calculateAccuracy()` is computed the same way. The "AI Crop Prediction Model" that players see is simulated.
- **Takeaway.** Story, place and design won this award. The data and ML depth were thinner than the project page suggests.

### FarmNavigators (organisation Nasa-FarmNavigators), 2025 (result not confirmed)

- **What exists.** Six repos (backend, data, docs, web, mobile, Godot game) with Portuguese docs. The data service has 21 commits from 2 to 4 October 2025 and a CI workflow.
- **Data path.** `nasa_service.py` calls the NASA POWER daily point API (`community=AG`) and computes PET and a bucket soil-moisture model. The docstring says it "supports future dates by extrapolating the last available data", so it invents forecasts.
- **Hardcoded farm.** `recommendation_service.py` uses fixed coordinates for Luanda, Angola, with a comment marking them as a mock.
- **Mentioned but unused.** The README lists AppEEARS, Crop-CASMA, GLAM and Giovanni. None of them appears in the service code.
- **Link to Agro Quest.** The honorable mention Agro Quest was from Aracaju, Brazil. I could not tie these repos to it, so that link is not confirmed. A repo named `denolog21/AgroQuest-Games`, created 5 October 2025, is empty.

### Other 2025 Farm Navigators repos (results not confirmed)

- **CodeForSeedney** ([repo](https://github.com/Code-for-Sydney/CodeForSeedney)). 77 commits. A Godot game with a web build in `docs/`. Its `SoilMoisture.json` holds "SMAPTop" values for each day of the month, rounded to 0.05, and an empty "SMAPSub" field. The values look typed by hand, and the source product is not stated.
- **Farm Quest** ([repo](https://github.com/acciomo/nasa-spaceapps-hackathon)). The README promises "real-world satellite data". The code holds a hardcoded list of farm locations and adds Google OAuth, with no data calls that I found.
- **Empty or near-empty repos.** `K-NataliaConde/AgroGuardian` and `denolog21/AgroQuest-Games` are empty. `AmmarOsamaAli/Farm-Navigators` has only a README.

### Project L.L.O.C.U.S.T., 2020, Galactic Impact

- **What it does.** It predicts locust swarm risk and movement in Kenya for farmers and officials ([project page](https://2020.spaceappschallenge.org/challenges/inform/automated-detection-hazards/teams/project-llocust-1/project), [Earthdata](https://www.earthdata.nasa.gov/news/2020-space-apss-challenge-winners)).
- **Data path.** The team pulled Worldview snapshot images of four layers: SMAP L4 surface soil moisture, SMAP L4 soil temperature, MODIS Terra NDVI 8-day and ASTER GDEM. They sampled pixel colours at FAO swarm points and random non-swarm points, then trained a random forest and an SVM on the RGB values.
- **Validity.** Colours from a rendered map are not physical values. The team reports 100 percent test accuracy on about 200 samples and says the small sample is the likely cause. An economic-cost feature used mock data.
- **Repo.** [kvnyng/Project-L.O.C.U.S.T](https://github.com/kvnyng/Project-L.O.C.U.S.T): 32 commits from October 2020 to March 2021, no licence. All data are bundled CSVs, JSON and a 23 MB population GeoTIFF.
- **Demo.** The Netlify site still loads, and a YouTube demo is linked from the project page.
- **Takeaway.** The judges rewarded a vivid food-security story with an interactive map, even with a weak method that the team disclosed.

### Other 2019 to 2023 checks

- **2021.** The Galactic Impact winner 4 Seeds built InfiniPod, a crop pod for a Mars transit mission ([2021 team page](https://2021.spaceappschallenge.org/challenges/statements/have-seeds-will-travel/teams/4-seeds)). It is space farming, not Earth agriculture, and uses no Earth observation. No other 2021 winner is agricultural, going by the names in the [2021 list](https://earthdata.nasa.gov/news/nasa-announces-2021-international-space-apps-challenge-global-award-winners). I did not open every winner's page.
- **2022.** No winner name suggests agriculture ([2022 list](https://www.earthdata.nasa.gov/news/nasa-announces-winners-2022-global-space-apps-challenge)). Team Ookami's "Tanom" proposed planting-time advice from NASA POWER soil moisture and skin temperature, but it was a Canva mock-up with no award ([page](https://2022.spaceappschallenge.org/challenges/2022-challenges/earth-data-analysis-developers-wanted/teams/team-ookami-3)).
- **2020.** Apart from L.L.O.C.U.S.T., the winner Monsoon Overflow (Anand, India) may relate to floods. I did not inspect it, so its relevance is not confirmed.
- **2019.** The awards page text loaded without winner names ([2019 awards](https://2019.spaceappschallenge.org/awards/)). The Best Use of Data winner was AEDES, a dengue tool ([VERA Files](https://verafiles.org/articles/isdapp-filipino-it-experts-wins-nasa-space-challenge)). I found no 2019 agriculture winner, but this is not confirmed.
- **2023.** No agriculture challenge ran in 2023 (see `past_winners.md`).

## Lessons for Field Shift

### What winners did that others did not

1. **They answered one farmer question in farmer words.** 2Plant asks "can I plant today, and will the tractor get stuck?" WaterWise asks "how long do I run the pump tonight?" ([CrafterWIKI 2Plant](https://crafterwiki.com/projects/2plant), [CrafterWIKI WaterWise](https://crafterwiki.com/projects/waterwise/)). Non-winners often showed dashboards of raw layers (FarmVis, Farmalytics).
2. **They showed the method and its error.** 2Plant published error against ground truth and drew uncertainty bands. WaterWise wrote its formula on the project page. Both answer the Validity criterion before a judge asks.
3. **Their pipelines ran on live or real data.** WaterWise calls OpenET and Open-Meteo for every request. 2Plant runs on a production granule pipeline. Most non-winners used one or three days of pre-downloaded files.
4. **They had a real person and place behind the story.** That includes the Minnesota farmer's question, the Pakistan 2022 floods and Kenya's locusts ([Silicon Prairie News](https://siliconprairienews.com/2025/02/nebraska-startup-wins-nasas-galactic-impact-award-in-the-2024-space-apps-challenge), [Zumorroda-X page](https://www.spaceappschallenge.org/2025/find-a-team/zumorroda-x/?tab=project)).
5. **They had a clickable demo that still works.** WaterWise, Henry's and L.L.O.C.U.S.T. demos still load one to six years later.

### Common failure modes

- **Fake or simulated outputs presented as AI.** Henry's "AI Crop Prediction" is a timer plus hardcoded offsets. FarmNavigators "extrapolates" future weather from the last data point.
- **Datasets mentioned but not used.** The FarmNavigators README lists four NASA tools, and the code calls only POWER. Gajini has an empty ECOSTRESS loader. FarmVis has an iframe instead of data.
- **Static snapshots shown as if they were live.** Gajini uses three days in August 2024. CodeForSeedney uses SMAP values typed by hand. Farmalytics uses bundled GLDAS tiles.
- **Unit and method errors.** WaterWise applies Kc to actual ET and appears to have an area bug. Gajini turns fill values into zero moisture. L.L.O.C.U.S.T. trains on map colours.
- **LLM as the agronomist.** Gajini's crop choice is a GPT-4 prompt with no rules or evidence.
- **Secret leaks.** Gajini hardcoded an Earthdata token, and Farmalytics committed `.env`.
- **No licence.** Most repos have no licence, even though Space Apps asks for open source (see `rules_judging.md`).
- **Empty or one-commit repos, and broken links.** The original Henry's repo is deleted, and the 2Plant demo link does not resolve.

### What would make Field Shift stand out

1. **Be the first real rotation comparison.** No past entry compared crop sequences over several years. The only crop recommender (Gajini) used an LLM. Field Shift should compare the farmer's current rotation with at least two alternatives, using transparent rules and models that a judge can read.
2. **Show uncertainty and data gaps the way 2Plant did.** Give each strategy a range, not a single number. Add a "where data is missing" panel and a "check locally" list. This answers Validity and the challenge's demand for honesty about limits.
3. **Use NASA data live, with honest scope.** Pull at least two NASA sources through `earthaccess` or the POWER API at request time. Cache outside the repo, never hardcode tokens, and show the data date on screen. List every source and licence.
4. **Get the agronomy right and cite it.** Use FAO-56 Kc × reference ET for water use. Cite each coefficient. Add unit tests for area, units and fill values, the exact places where past winners slipped.
5. **Keep any SI honest.** If we use ML or an LLM, use it to explain results or rank options with evidence attached, and never show simulated results as predictions.
6. **Lead with one farmer and one decision.** Frame the 30-second video around a named place and one real rotation choice, as the winners did.
7. **Treat the repo as a deliverable.** Use an Apache 2.0 licence, a README with the method and its limits, steady commit history, and a demo link that keeps working after judging.

## Sources

Official pages and news:

- https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-international-space-apps-challenge-announces-2024-global-winners/
- https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-announces-2025-international-space-apps-challenge-global-winners/
- https://www.spaceappschallenge.org/2025/find-a-team/zumorroda-x/?tab=project
- https://www.spaceappschallenge.org/nasa-space-apps-2024/find-a-team/farmvis/
- https://2020.spaceappschallenge.org/challenges/inform/automated-detection-hazards/teams/project-llocust-1/project
- https://2021.spaceappschallenge.org/challenges/statements/have-seeds-will-travel/teams/4-seeds
- https://2022.spaceappschallenge.org/challenges/2022-challenges/earth-data-analysis-developers-wanted/teams/team-ookami-3
- https://2019.spaceappschallenge.org/awards/
- https://www.earthdata.nasa.gov/news/2020-space-apss-challenge-winners
- https://earthdata.nasa.gov/news/nasa-announces-2021-international-space-apps-challenge-global-award-winners
- https://www.earthdata.nasa.gov/news/nasa-announces-winners-2022-global-space-apps-challenge
- https://siliconprairienews.com/2025/02/nebraska-startup-wins-nasas-galactic-impact-award-in-the-2024-space-apps-challenge
- https://nation.ge/?m=5&news_id=34213
- https://techukraine.org/2025/01/18/ukrainian-ingenuity-shines-bright-kyiv-teams-nvs-knot-takes-top-honors-at-nasa-space-apps-challenge/
- https://verafiles.org/articles/isdapp-filipino-it-experts-wins-nasa-space-challenge

Third-party index:

- https://crafterwiki.com/projects/2plant
- https://crafterwiki.com/api/v0/projects/2plant.json
- https://crafterwiki.com/projects/waterwise/
- https://crafterwiki.com/api/v0/projects/waterwise.json
- https://crafterwiki.com/api/v0/projects/zumorroda-x.json
- https://crafterwiki.com/hackathons/nasa-space-apps-2024/

Repos (read through the GitHub API):

- https://github.com/yaroslav-prokipchyn/2plantORNOT2plant
- https://github.com/gabe-engineers/nasa-hackathon-2024
- https://github.com/nasa-gajini/gajini-api
- https://github.com/nasa-gajini/gajini-ml
- https://github.com/nasa-gajini/gajini-web
- https://github.com/sahusgupta/farmvis
- https://github.com/ahmadkammonah/Farmalytics
- https://github.com/esralsayed/Henry-s-Farming-Adventure-Game
- https://github.com/Nasa-FarmNavigators/FarmNavigators-Data
- https://github.com/Nasa-FarmNavigators/FarmNavigators-Game
- https://github.com/Code-for-Sydney/CodeForSeedney
- https://github.com/acciomo/nasa-spaceapps-hackathon
- https://github.com/kvnyng/Project-L.O.C.U.S.T
- https://github.com/K-NataliaConde/AgroGuardian (empty)
- https://github.com/denolog21/AgroQuest-Games (empty)
- https://github.com/AmmarOsamaAli/Farm-Navigators (README only)

Live demos checked:

- https://nasa-hackathon-2024-nine.vercel.app/ (loads)
- https://henrysfarmadventures.vercel.app/ (loads)
- https://determined-keller-5cbae8.netlify.app/ (loads)

Failed or blocked URLs:

- https://www.spaceappschallenge.org/nasa-space-apps-2024/find-a-team/nvs-knot/?tab=project (login message)
- https://www.spaceappschallenge.org/nasa-space-apps-2024/find-a-team/gaamaramma/?tab=project (login message)
- https://www.spaceappschallenge.org/nasa-space-apps-2024/find-a-team/gajini/?tab=project (login message)
- https://www.spaceappschallenge.org/nasa-space-apps-2024/find-a-team/farmvis/?tab=project (login message)
- https://www.spaceappschallenge.org/2025/find-a-team/agroquest/?tab=project (login message)
- https://nasa.nave-app.com/list-view (did not resolve)
- https://farmvis1.streamlit.app/ (timed out)
- https://98e2zjiicz.us-west-2.awsapprunner.com/tiles/vnp09h1-ndvi/ (404 at base path)
- https://github.com/AlaaAbdelnase/test_farmy (404, original Henry's repo)
- https://www.youtube.com/watch?v=Wg-gE3kYaas (WaterWise video; page loaded but content could not be read)
- https://meteomatics.com/en/news/ometeotl-crop-connect (404)
- Direct curl to spaceappschallenge.org failed with a TLS certificate error in this environment, so I could not read `__NEXT_DATA__`. I used a rendering fetcher instead.
