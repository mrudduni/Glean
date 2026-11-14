# Other global challenges on farms and Earth observation

Phase 2 research, gathered 2026-11-14. This file covers challenges outside NASA Space Apps and outside India's government hackathons. Past Space Apps winners are in `past_winners.md` and `past_projects_deep_dive.md`. Facts we could not check carry the label "not confirmed".

## Summary for Field Shift

- Competitions with public code are mostly Zindi machine-learning contests run with Radiant Earth, NASA Harvest or CGIAR. They target crop type, field boundaries, yield or damage, not rotation choice.
- Two India-specific contests (AgriFieldNet and the Digital Green yield challenge) show that tiny fields and local farming knowledge decide results more than model choice.
- Grant-style prizes (CGIAR Inspire, XPRIZE, FAO youth hackathons) reward delivery to farmers: hotlines, photo apps, and services that already have users.
- We found no competition anywhere that asks teams to compare whole crop rotations for one field. That gap matches `../03_domain/existing_tools.md`.

## Zindi and Radiant Earth competitions

| Challenge | Years | Problem | Data | Winning approach and code |
|---|---|---|---|---|
| AgriFieldNet India Challenge | Closed 31 October 2022 | Classify crop type per field in Uttar Pradesh, Rajasthan, Odisha and Bihar. Prize $10k. Run by Radiant Earth, IDinsight and Zindi under the Gates-funded ECAAS programme | Sentinel-2 with field labels, CC BY 4.0 | Winner Team Starlink put most effort into data engineering. Fields were very small with little variation inside each field. Code: https://github.com/radiantearth/model_ecaas_agrifieldnet_gold (also `_silver`, `_bronze`), https://github.com/Iheb-ch/AgriFieldNet-India-Challenge-Top-4-Solution |
| Digital Green Crop Yield Estimate Challenge | 4 September to 3 December 2023 | Predict yield from farmer survey data in Bihar. Prize €9,400 | Digital Green survey data | Third place used an XGBoost, CatBoost and LightGBM ensemble. The team said most of the gain came from cleaning data and from local knowledge: North versus South Bihar, the Ahar Pyne irrigation system, and kharif and rabi timing. Source: https://zindi.world/competitions/digital-green-crop-yield-estimate-challenge/discussions/19696 |
| NASA Harvest Field Boundary Detection Challenge | 17 November 2022 to February 2023 | Draw field boundaries for smallholder farms in Rwanda. Prize $5k. Run with Radiant Earth and USDA FAS | PlanetScope time series (not confirmed) | Fourth place code: https://github.com/geoaigroup/nasa_harvest_boundary_detection_challenge. Starter: https://github.com/radiantearth/Nasa_harvest_field_boundary_competition |
| CGIAR Crop Damage Classification Challenge | 27 October 2023 to 28 January 2024 | Classify crop damage type from farmer smartphone photos, for picture-based insurance. Prize $10k. Partners: ACRE Africa, KALRO, IFPRI, Lacuna Fund | Smartphone photos from Kenya | Rules capped compute at one GPU and under 8 hours of training, with deployment on a 4-core, 16 GB VM. The related CGIAR Eyes on the Ground Challenge used the same photo data. Source: https://zindi.world/competitions/cgiar-crop-damage-classification-challenge |

Sources: https://zindi.world/competitions/agrifieldnet-india-challenge, https://radiant.earth/blog/2023/04/behind-the-agrifieldnet-model, https://zindi.world/competitions/nasa-harvest-field-boundary-detection-challenge

## Space agency challenges

| Challenge | Year | Farm problem | Result |
|---|---|---|---|
| EO Dashboard Hackathon (NASA, ESA and JAXA) | 23 to 29 June 2021 | One track asked for the agricultural impacts of COVID-19 using the joint EO Dashboard. Team projects included "Feed the World" and AGREENTERRA (rice in the lower Mekong) | More than 4,300 people took part and eight projects became Global Winners. Which farm projects won is not confirmed. Sources: https://www.earthdata.nasa.gov/news/feature-articles/announcing-eo-dashboard-hackathon-winners, https://eodashboardhackathon.org/challenges/agricultural-impact/agricultural-impacts-of-covid-19/teams/agreenterra/project, http://eodashboardhackathon.org/awards |
| Copernicus Masters | Yearly since 2011 | Business ideas built on Copernicus data | SmartIrrigation came third in the 2013 Best Service Challenge. Source: https://esa.int/Applications/Observing_the_Earth/Copernicus/Harmful_algal_bloom_forecasting_service_wins_prize. Current calls: https://copernicus.eu/en/opportunities/calls-competitions-and-prizes |
| ESA Phi-Lab and Space App Camps | Various | Not checked in this pass | Not confirmed |
| UK Space Agency "Unlocking Space for Agriculture" | 2026 | Pilot projects that bring satellite data to UK farms | Source: https://space.blog.gov.uk/2026/01/20/unlocking-space-for-agriculture/ |

The EO Dashboard awards page lists data awards by agency, including a JAXA ALOS-2 Data Award. Space Apps judges from partner agencies may value the same thing: clear use of their own mission data.

## CGIAR, FAO and other development prizes

- CGIAR Inspire Challenge (2017 to 2020) gave 21 projects USD 3.225 million in total. Winners included the CubicA advisory hotline, picture-based insurance, MARPLE (field diagnosis of wheat rust), Croppie (yield from photos), N-ALLyzer, the TALIA hotline, an IVR market price service, and smart seed selection. Source: https://bigdata.cgiar.org/inspire/inspire-winners/
- FAO Reboot the Earth, Rome 2025: winner Hackriculture built AgriSnapp, a photo app that diagnoses pests and sends geo-tagged alerts. Other editions ran in India and in Morocco (Terra-Optima). Source: https://fao.org/e-agriculture/news/reboot-earth-rome-science-and-innovation-forum-2025-youth-led-innovation-driving-open-source-0
- XPRIZE Carbon Removal grand prize (April 2025) went to Mati Carbon, which spreads crushed basalt on smallholder fields in India and worked with more than 30,000 farmers in 2025. Sources: https://time.com/7279701/xprize-winner-mati-carbon-interview, https://xprize.org/news/impactreport2026
- XPRIZE Feed the Next Billion is about meat and protein alternatives, not land use. Finalists learned there would be no $10M grand prize. Source: https://agfundernews.com/xprize-feed-the-next-billion-finalists-learn-there-is-no-10m-grand-prize-it-feels-dishonest
- World Bank and GEOGLAM challenge programmes: not checked in this pass (not confirmed).
- USDA prize challenges: not checked in this pass (not confirmed).

## Computer vision and Kaggle

- Agriculture-Vision Prize Challenge 2024 (CVPR workshop): segmentation of field patterns in aerial farm images. Source: https://www.agriculture-vision.com/agriculture-vision-2024/prize-challenge-2024
- Kaggle farm competitions: not checked in this pass (not confirmed).

## Platforms and programmes that are not competitions

These came up while searching. They are tools or research groups, but each offers parts Field Shift could reuse.

| Name | What it is | Relevance | Source |
|---|---|---|---|
| Microsoft FarmVibes.AI | Open-source local cluster with workflows that fuse satellite, weather and drone data. Includes notebooks for crop segmentation and nutrient heatmaps (carbon, nitrogen, phosphorus) | Ready-made workflows, though heavy to run in a weekend | https://github.com/microsoft/farmvibes-ai, https://microsoft.github.io/farmvibes-ai/docfiles/markdown/NOTEBOOK_LIST.html |
| NASA Acres | NASA consortium for US agriculture. Recent work covers cover-crop growth, nitrogen uptake and termination timing from satellites, and a USDA NIFA grant for farmer data sharing with privacy controls | Cover-crop methods match the challenge text. No open prize found | https://nasaacres.org/news/connecting-satellite-science-farmers-and-real-world-impact-at-agu25, https://geog.umd.edu/featured-content/nasa-acres-receives-over-900000-usda-nifa-funding-advance-agricultural-data |
| NASA Harvest | NASA consortium for global food security. Co-ran the Zindi field boundary challenge | Smallholder methods | https://zindi.world/competitions/nasa-harvest-field-boundary-detection-challenge |
| Digital Green FarmerChat | Generative AI assistant for farmers. Works on WhatsApp, Telegram and an app. Supports Hindi, Telugu, English and Bhojpuri, by text or voice | Proof that WhatsApp and voice delivery work for Indian farmers | https://help.gooey.ai/farmerchat, https://gooey.ai/farmerchat, https://digitalgreen.org/farmerchat |
| Source Cooperative (Radiant Earth) | Open data hosting for geospatial datasets | Hosts many Radiant Earth training sets (not confirmed for each one) | Not confirmed |

Digital Green's open code for Farmer.Chat is at https://github.com/digitalgreenorg/monorepo/blob/main/farmer-chat/README.md. The README says it uses Google Translate for many languages in text and audio.

## Items not covered

We did not check ESA Phi-Lab, ESA Space App Camps, GEO and GEOGLAM, Kaggle, USDA, the World Bank, AI4Bharat, Bhashini, or iDEX in this pass. iDEX is a defence programme and is unlikely to hold farm challenges (not confirmed).

## Sources

- https://zindi.world/competitions/agrifieldnet-india-challenge
- https://radiant.earth/blog/2023/04/behind-the-agrifieldnet-model
- https://github.com/radiantearth/model_ecaas_agrifieldnet_gold
- https://github.com/Iheb-ch/AgriFieldNet-India-Challenge-Top-4-Solution
- https://zindi.world/competitions/digital-green-crop-yield-estimate-challenge/discussions/19696
- https://zindi.world/competitions/nasa-harvest-field-boundary-detection-challenge
- https://github.com/geoaigroup/nasa_harvest_boundary_detection_challenge
- https://github.com/radiantearth/Nasa_harvest_field_boundary_competition
- https://zindi.world/competitions/cgiar-crop-damage-classification-challenge
- https://www.earthdata.nasa.gov/news/feature-articles/announcing-eo-dashboard-hackathon-winners
- https://eodashboardhackathon.org/challenges/agricultural-impact/agricultural-impacts-of-covid-19/teams/agreenterra/project
- http://eodashboardhackathon.org/awards
- https://esa.int/Applications/Observing_the_Earth/Copernicus/Harmful_algal_bloom_forecasting_service_wins_prize
- https://copernicus.eu/en/opportunities/calls-competitions-and-prizes
- https://space.blog.gov.uk/2026/01/20/unlocking-space-for-agriculture/
- https://bigdata.cgiar.org/inspire/inspire-winners/
- https://fao.org/e-agriculture/news/reboot-earth-rome-science-and-innovation-forum-2025-youth-led-innovation-driving-open-source-0
- https://time.com/7279701/xprize-winner-mati-carbon-interview
- https://xprize.org/news/impactreport2026
- https://agfundernews.com/xprize-feed-the-next-billion-finalists-learn-there-is-no-10m-grand-prize-it-feels-dishonest
- https://www.agriculture-vision.com/agriculture-vision-2024/prize-challenge-2024
- https://github.com/microsoft/farmvibes-ai
- https://microsoft.github.io/farmvibes-ai/docfiles/markdown/NOTEBOOK_LIST.html
- https://nasaacres.org/news/connecting-satellite-science-farmers-and-real-world-impact-at-agu25
- https://geog.umd.edu/featured-content/nasa-acres-receives-over-900000-usda-nifa-funding-advance-agricultural-data
- https://help.gooey.ai/farmerchat
- https://gooey.ai/farmerchat
- https://digitalgreen.org/farmerchat
- https://github.com/digitalgreenorg/monorepo/blob/main/farmer-chat/README.md
