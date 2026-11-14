# Competition scan for Field Shift 2026

Scan date: 14 November 2026, morning (UTC). The hackathon had started in Asia and was about to start in Europe and the Americas. Nothing has been judged yet.

## Summary

- GitHub holds about 260 public repos created since 1 September 2026 whose name or description points at Field Shift, crop rotation with NASA data, or farm decision support with NASA data. About 150 of them name "Field Shift", "FieldShift" or "Adapting Farms" directly. Not every match is a Field Shift entry, and many entries will be private, so this is a floor, not a count.
- Most repos are thin. About 186 of the 263 kept repos have fewer than 10 commits. About 15 have 50 or more commits, and those are polished, deployed and well documented.
- Bangladesh dominates the strong repos. Of the 22 repos read in detail, 10 are Bangladeshi teams, and most of them are bilingual (Bangla and English) and work offline.
- NASA POWER is in every repo read. SMAP, GPM IMERG and MODIS come next. ECOSTRESS, GRACE, SRTM, GEDI and OpenET are rare.
- The leading pattern is a rule-based or multi-criteria rotation engine on NASA POWER climate history and SoilGrids soil, with a chat assistant (often Gemini) bolted on for explanations. Several teams say outright that the language model does not compute the scores.
- About 186 of the kept repos were created before 14 November, and 72 before 1 November. The FAQ says teams "are not allowed to begin working on the challenges prior to the hackathon" (https://www.spaceappschallenge.org/resources/participant-faqs/). How judges treat this is not confirmed. One team publishes a prior-work disclosure.
- The challenge page Details and Resources tabs have not changed since the 13 November scrape. The Teams tab now shows 1,805 teams, up from 1,605.

## Method

- GitHub search ran through `gh search repos` and `gh search code` on 14 November 2026. Queries: "field shift", fieldshift, field-shift, "adapting farms", "space apps 2026", spaceapps2026, space-apps-2026, nasa-space-apps-2026, "spaceapps crop", "crop rotation nasa", "space apps" farm, "crop rotation" and crop-rotation created after 1 September, nasa "crop rotation" sorted by update, farm/crop/agro with nasa created after September or October, "rotation spaceapps", "nasa space apps" agriculture, and the topics spaceapps, spaceapps2026, nasa-space-apps-2026, nasa-space-apps-challenge and space-apps-challenge. Code search ran for "Adapting Farms with NASA Data" (7 repos) and two other phrases (0 hits).
- GitHub search returns at most 100 results per query. Eight queries hit that cap, so some repos are missing.
- I filtered 633 unique results down to 263 by creation date (on or after 1 September 2026) and keywords, then removed obvious unrelated repos (fire hotspot classifiers, a game, a raster tool and similar).
- For every kept repo I counted commits through the GitHub API. For 22 repos I read the README, root file list, licence and commit date range.
- The dataset columns below come from a keyword match on each README. A mention does not prove the repo uses the dataset.
- Web search ran through TinyFish for LinkedIn, Medium, dev.to, YouTube and Reddit.

## Repos with the most work

Commit counts and dates are from the GitHub API on 14 November 2026. "Created" is the repo creation date in UTC.

| Repo | Team and place | Created | Commits | Stack | Approach | NASA data named | Live link |
|---|---|---|---|---|---|---|---|
| AdribMahmud101/seedwise | Team Kothinn, Rangpur, Bangladesh | 8 Nov | 543 | Next.js, Cloudflare worker | "SeedWise": one decision for one field. 3D field studio, rotation plans with sliders for water, income, risk and labour, flood and drought briefs, season calendar. Bangla and English, offline, three pilot fields | POWER, SMAP, IMERG, Landsat, HLS, GRACE, Sentinel | https://seedwise.onefusionlab.systems |
| danial-hossain/FieldShift | Team Azoic, Dhaka | 1 Oct | 412 | Python, JavaScript, Docker | Compares the current rotation with four strategies (balanced, profit, water saving, soil building) over six seasons. Each gets a five-part card that mirrors the challenge text (why, evidence, benefits, gaps, local risks). Cross-checks a POWER rainfall-onset trend against IMERG and reports that IMERG does not confirm it. Has prior-work and AI-use disclosures | IMERG, POWER, GRACE/GRACE-FO, SRTM (SMAP and MODIS planned) | not found |
| moshiour0/FieldShift0 | not stated, Bangladesh | 8 Oct | 367 | Python API, Supabase, Vercel | "KrishiNexus" decision support with AppEEARS and Earth Engine providers, evidence cards and a school game | POWER, SMAP, IMERG, HLS, MODIS | https://field-shift0.vercel.app |
| razibr246/fieldshift360 | BRM AstraX, Barisal | 24 Oct | 217 | Vite, React, in-browser compute | Runs hundreds of one- and two-year rotations for ten years on 25 seasons of POWER weather, replays the leaders in the 2040s with NEX-GDDP-CMIP6, and answers "keep, adjust or shift" for this season. Has a farmer side, an extension officer side, games and a data register. Claims 1,007 passing tests | POWER, SMAP, IMERG, Landsat, MODIS, GRACE, SRTM, Sentinel-1 and -2 | https://fieldshift360.vercel.app |
| Ridwanulkarim/field-shift | not stated, Bangladesh | 26 Sep | 148 | Node backend, PostgreSQL/PostGIS | Planting-window advice that compares rain onset in 2001 to 2012 with 2013 onwards, plus a rule-based rotation comparison, with Bangla text and SMS summaries. States that it predicts neither yield nor profit | POWER, IMERG | not found |
| Davidelksfam/FieldShift | not stated | 13 Nov | 103 | JavaScript | README not read | not read | not read |
| G-Sadi/Nasa-Space-Apps-Challenge-website | ASL_Spectra, Mymensingh, Bangladesh | 7 Oct | 72 | Three.js, Leaflet, Python backend | 3D farm "digital twin" with a Gemini chatbot in Bangla and English. No licence file | SMAP, MODIS, POWER, MERRA-2, ECOSTRESS (badges) | https://g-sadi.github.io/Nasa-Space-Apps-Challenge-website/ |
| Zul-Qarnain/field-shift | Team Orion, Barishal, Bangladesh | 27 Sep | 55 | Next.js 16, Python 3.13, Android | Three ranked plans from three choices on one screen, with a "see why" panel showing the arithmetic. A fictional farmer, Karim, carries the story. README has a judges' checklist and a scorecard against the criteria | POWER, IMERG, MERRA-2, GIBS | https://field-shift-tan.vercel.app |
| Owasiul/Chash_Orbit | not stated, Bangladesh | 7 Oct | 50 | Next.js, Prisma | Rule-based crop scoring, heat, drought and flood risk, a four-year rotation plan and what-if climate scenarios. A Gemini advisor explains, but scores come only from the rule engine | POWER, MODIS (others mentioned) | https://chash-orbit.vercel.app |
| quocbao271207/astrovivu-field-shift | Team Astrovivu, Vietnam | 13 Nov | 40 | Vite, TypeScript, Node server | One parcel on one timeline on a 3D globe. Eight metrics drawn inside the field at 10 to 30 m where imagery allows, farmer ground corrections, and at least three rotations with evidence, gaps and risks. English and Vietnamese, no account or key | Mentions almost every resource on the challenge page | not found |
| sagar25446-prog/FieldShift-NASA | not stated | 13 Oct | 36 | Streamlit | Globe, POWER climate summaries and CSV download, rule-based rotations for four pilot regions (Punjab, US Corn Belt, Andalusia, semi-arid India). Leaves unknown soil values blank | POWER, MODIS (optional) | not found |
| RavenEibu/field-shift | not stated, Argentina | 29 Oct | 36 | Python, uv | Spanish README. Verification first: POWER 1991 to 2025 and SMAP L4 checked, FAO-56 crop coefficients cited, and no ranking yet because independent validation is still open | POWER, SMAP L4 | not found |
| SetarehAlamdar/FieldSense | not stated, Canada | 29 Oct | 14 | Python, GitHub Pages | Reads a "field barcode" of what grew and when soil was bare from HLS since 2015. Builds 1,000 possible next seasons from 30 years of POWER weather corrected against Environment Canada stations. Compares rotations as a trade-off table and tests the choice across 2,000 weightings. Labels each number as measured, validated, modelled and so on | HLS, POWER, SMAP | https://setarehalamdar.github.io/FieldSense/ |
| chuijialee-crypto/NASA-Hackathon-ClimateTwin | Team 103, Kuala Lumpur | 13 Nov | 36 | FastAPI, JavaScript | Finds a place whose climate today matches the field's projected 2045 climate, then shows what farmers grow there. Built on 40 years of POWER | POWER | not found |
| ZisanUlHaque/AgroNova | Team AgroNova, Bangladesh | 30 Sep | 17 | Next.js monorepo, Prisma | "TerraShift" offline bilingual app with documented scoring equations and a 60-second judge walkthrough | SMAP L4, Landsat 9 SSEBop ET, POWER | https://agronova-five-theta.vercel.app |
| JosephWalusimbi-eng/ARAPAI-FARM-TWIN | not stated, Soroti, Uganda | 14 Nov | 9 | FastAPI, Docker, Render | Ranks 357 three-season rotations for a 2 ha rain-fed farm and explains them in English, Luganda and Kiswahili. Offline data snapshot | POWER, IMERG, SMAP, SoilGrids | https://farm-twin-5n9n.onrender.com |
| Ichya20/FieldShift | not stated | 8 Nov | 2 | FastAPI, React 19, three.js | Compares rotation options from POWER climate, MODIS vegetation, soil, terrain and FAO GAEZ suitability | POWER, MODIS, GAEZ, SoilGrids | not found |
| oscadoc77/Field-Shift | Picateclas Systems, Guadalajara, Mexico | 11 Nov | 11 | Static HTML, Leaflet, Chart.js | Current rotation plus two alternatives, each with a fit score, reasons, goal ratings, benefits, gaps and local risks. English and Spanish | POWER climatology including root-zone wetness | not yet |
| tejaswi-raghav/field-shift | not stated | 19 Sep | 2 | Next.js, FastAPI | Deterministic three-year rotations with hard filters and a multi-criteria model, five demo farms, scenario sliders. Marks SMAP as unavailable rather than inventing it | POWER, SoilGrids, SMAP adapter only | not found |
| ferrosasfp/field-shift | Team1 Avalanche, Moquegua, Peru | 12 Nov | 2 | Next.js, Supabase | Spanish workshop base. Explainable rotation plus a backtest of a parametric insurance policy, with an optional test-network smart contract | POWER | not found |
| teamatlaslive/Field-Shift | Team Atlas, Bangladesh | 13 Nov | 1 | Static JavaScript, hardware | Compares crop sequences for one plot and imports CSV logs from a soil-probe rover. Labels the probe's limits | POWER | not found |
| umar-essayed/BlinkFarms-NASA-SpaceApps | not stated | 8 Nov | 20 | Next.js, Python engine | Flash-drought early warning from ECOSTRESS canopy temperature and an evaporative stress index, plus rotation advice | ECOSTRESS, SMAP, IMERG, Landsat | not found |

Other repos worth a look later: Krin8/CropSwarm (offline rotation support), LunarOblivion/Up-to-Par-Adeptus-Volterra (a "fallow audit" that replays 20 years of weather and vegetation for one field; README only so far), nmtaief/FarmScale (groundwater on the Barind Tract), kmcodes/space-apps (Vidarbha, India), Stalker-a/field-shift-kz (Kazakhstan), siengphalsithykun-ctrl/field-shift-kh (Khmer rice planting map), shahkhalid030056-prog/space2earth-field-shift (Urdu), mona159753z-lab/zar3a (Egypt), VanshikaVermaJK/PathogenBreak (disease-aware rotation, Indore), chris-nofi/nofi-space (ECOSTRESS water use, Moquegua) and spacefarmgov/space-farm (three-year rotation).

## Patterns across competitors

These are my reading of the READMEs.

- **The challenge text is the template.** Many READMEs copy the five outputs the challenge asks for (why, evidence, benefits, gaps, local risks) into per-strategy cards. Doing this alone will not stand out.
- **Deterministic engine, language model for words.** Chash Orbit, Field Shift by tejaswi-raghav and FieldShift by danial-hossain state that scores come from rules or multi-criteria maths, not from a model. Judges may now expect this.
- **Honesty about data limits is common.** RavenEibu, FieldSense, tejaswi-raghav, Team Atlas and danial-hossain all label modelled values, unavailable data or failed validations. danial-hossain reports a negative result (IMERG does not confirm a POWER trend).
- **Bangladesh, bilingual and offline.** Several Bangladeshi teams build Bangla-first, offline apps for the same Boro rice and groundwater story. Local judges in Bangladesh will see many similar entries.
- **Spectacle.** At least four teams use 3D (SeedWise, ASL_Spectra, Astrovivu, Ichya20). FieldShift 360 adds games and an officer dashboard.
- **Judge-facing READMEs.** Team Orion, FieldShift 360 and AgroNova include judges' checklists, five-minute tours or 60-second walkthroughs.
- **Rare data.** Few teams mention GRACE, ECOSTRESS, SRTM, GEDI, OpenET, CDL or SSURGO. Only Ichya20 and Astrovivu mention GAEZ, and only FieldShift 360 mentions climate projections (CMIP6).
- **Rare ideas.** Climate analogs (Climate Twin), robustness across thousands of weightings (FieldSense), a field "barcode" of past crops and bare soil (FieldSense), a fallow audit (Up-to-Par), and an insurance backtest (ferrosasfp) are the most original framings found.

## What this means for our build

- Matching the challenge's five outputs is the entry ticket, not an edge.
- Quantified validation could be an edge. FieldSense and danial-hossain are the only repos read that compare a NASA product against independent ground data and report the result. A clear validation chart (for example IMERG against station rainfall, or SMAP against in-situ probes) answers the Validity criterion directly.
- Robustness to farmer priorities is a strong idea already in use (FieldSense). Showing how the ranking changes as the farmer moves priority sliders would match the challenge's "farmer priorities" text.
- Underused data with a clear farm meaning (GRACE groundwater trend, SRTM slope for erosion, ECOSTRESS evaporative stress, CDL rotation history in the US) could lift Relevance, which scores how core NASA data is.
- Most strong competitors target South Asia. A different place, told well, may stand out at global judging. This is not confirmed.

## Web posts about this year's challenge

- YouTube already has team videos: "Project Demo FIELD SHIFT: Adapting Farms With NASA Data | Team Zero_X" (https://www.youtube.com/watch?v=fh4mQWhnGJU, posted on 14 November) and "FIELD-IQ (Field Shift: Adapting Farms with NASA Data)" (https://www.youtube.com/watch?v=IDdhkO3DcBE, listed as three weeks old, so posted before the hackathon). I could not read the video content.
- The official challenge video features the challenge author, an engineer at NASA Johnson Space Center (https://youtube.com/watch?v=cF0U2WXsM7o). I could not read the full transcript.
- LinkedIn and Instagram posts from Local Events (Faisalabad, Karachi, Lahore) only restate the challenge (https://www.linkedin.com/posts/nasa-international-space-apps-challenge-faisalabad_nasa-space-apps-challenge-2026-challenge-activity-7524123517714526210-jYZn, https://instagram.com/p/DfWgb3RuSq4).
- Event sites mention Field Shift in passing: HackAthlone (https://hackathlone.com/blogs/how-to-choose-a-space-apps-challenge), Sonoma State (https://edeon.sonoma.edu/nasaspaceapps-26), Seoul (https://nasaspaceappskr.org/2026/en/), Hanoi (https://sepa.org.vn/en/spaceapps-hanoi-2026) and The Recursive for Central and Eastern Europe (https://therecursive.com/nasa-space-apps-challenge-2026-where-to-join-it-in-cee).
- I found no Medium, dev.to or Reddit posts describing a Field Shift 2026 project. Reddit only has general event posts (https://reddit.com/r/hackathon/comments/1wegw5s/nasa_space_apps_challenge_singapore_2026_virtual).

## Challenge page re-check

Fetched on 14 November 2026 with TinyFish, since curl failed a TLS certificate check on this machine.

- **Details tab:** the text matches `research/00_challenge/details.md` word for word. The tab still ends with "More resources may be added before the hackathon begins". It has no FAQ section and no clarifications.
- **Resources tab:** the same 23 NASA and USDA-style resources and 2 ESA resources, with the same links and descriptions as `research/00_challenge/resources.md`. GRACE and GRACE-FO are still named on the Details tab but not linked on the Resources tab. Nothing was added.
- **Teams tab:** "Currently returning 1805 teams", up 200 from 1,605 on 13 November (see `teams_tab.md`).
- **Related site changes:** the Judging and Awards Guide and the Participant FAQs are now dated 13 November 2026. Both say Global Winners get a virtual Winner's Celebration in early 2027. `event.md` describes an invitation to a NASA center, which comes from older terms and a Romanian press release, so treat the in-person visit as not confirmed for 2026. See `judging_insights.md`.

## Sources

- https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/?tab=details
- https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/?tab=resources
- https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/?tab=teams
- https://www.spaceappschallenge.org/resources/participant-faqs/
- https://www.spaceappschallenge.org/resources/judging-awards-guide/
- GitHub repos, each at https://github.com/ followed by the repo name in the table above
- GitHub search and REST API (`gh search repos`, `gh search code`, `gh api repos/.../commits`, `gh api repos/.../readme`), run 14 November 2026
- https://seedwise.onefusionlab.systems
- https://fieldshift360.vercel.app
- https://field-shift-tan.vercel.app
- https://field-shift0.vercel.app
- https://chash-orbit.vercel.app
- https://agronova-five-theta.vercel.app
- https://setarehalamdar.github.io/FieldSense/
- https://g-sadi.github.io/Nasa-Space-Apps-Challenge-website/
- https://farm-twin-5n9n.onrender.com
- https://www.youtube.com/watch?v=fh4mQWhnGJU
- https://www.youtube.com/watch?v=IDdhkO3DcBE
- https://youtube.com/watch?v=cF0U2WXsM7o
- https://www.linkedin.com/posts/nasa-international-space-apps-challenge-faisalabad_nasa-space-apps-challenge-2026-challenge-activity-7524123517714526210-jYZn
- https://instagram.com/p/DfWgb3RuSq4
- https://hackathlone.com/blogs/how-to-choose-a-space-apps-challenge
- https://edeon.sonoma.edu/nasaspaceapps-26
- https://nasaspaceappskr.org/2026/en/
- https://sepa.org.vn/en/spaceapps-hanoi-2026
- https://therecursive.com/nasa-space-apps-challenge-2026-where-to-join-it-in-cee
- https://reddit.com/r/hackathon/comments/1wegw5s/nasa_space_apps_challenge_singapore_2026_virtual
- Failed: curl of the challenge page (TLS error SEC_E_UNTRUSTED_ROOT). The first batch of `gh search` calls hit the search rate limit (HTTP 403) and was rerun with pauses. Live links were not opened or tested. The YouTube video pages returned no readable content.
