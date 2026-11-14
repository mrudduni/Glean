# ISRO and Indian challenges

Phase 2 research, gathered 2026-11-14. This file lists ISRO and other Indian hackathon problem statements that touch agriculture, soil, crops, water or drought. It gives the ID, title, a short paraphrase, the data named, and public winners. Facts we could not check carry the label "not confirmed". Data access details are in `../01_datasets/india/isro_data_access.md`.

## Summary for Field Shift

- No ISRO hackathon so far has asked for a crop-rotation tool. The closest is BAH 2026 PS06 (crop type, moisture stress and irrigation advisory by growth stage).
- ISRO problem statements in SIH 2022 to 2025 were about SAR, navigation, weather and astronaut tools. None was about farms.
- Farm problem statements in SIH come mostly from state governments, MoA&FW, PMFBY and Jal Shakti. Their winners are listed on the SIH result pages but almost none publish code.
- The common data path in ISRO problem statements is Resourcesat LISS-4 or LISS-3 from Bhoonidhi, with EOS-04 SAR for cloud cover. Sentinel-1 and Sentinel-2 appear in many public student repos because they need no Indian login.

## Bharatiya Antariksh Hackathon (BAH)

ISRO runs BAH with Hack2skill. Finals take place at NRSC, Hyderabad.

### BAH 2024

- 12 problem statements. Idea submission ran 4 to 26 July 2024. The finale ran 13 to 14 August 2024 at NRSC. Source: https://isro.hack2skill.com/2024
- Problem statements close to agriculture:

| Theme | Paraphrase | Data named |
|---|---|---|
| Feature extraction from high-resolution data | Extract features such as farm bunds, roads and buildings from very fine imagery | High-resolution ISRO imagery (sensor not confirmed) |
| Voice-enabled map interface | Let users ask map questions by voice | Bhuvan layers (not confirmed) |
| Context-aware geospatial retrieval with LLM or NLP | Turn plain-language questions into geodata queries | ISRO geoportals (not confirmed) |

- Winners: a Thapar Institute team won. Heritage Institute of Technology's team "Lusine" came second. An IIT Roorkee team was second runner-up. Which problem statement each team solved is not confirmed. Sources: https://nknewsodisha.in/2024/08/heritage-institute-students-shine-as.html, https://outlookindia.com/hub4business/honorable-president-of-india-felicitated-students-team-from-heritage-institute-of-technology

### BAH 2025

- 14 problem statements. The finale ran 7 to 8 August 2025 at NRSC. Source: https://hack2skill.com/event/bah2025

| ID | Paraphrase | Data named | Source |
|---|---|---|---|
| PS2 | AI help bot that answers questions from a knowledge graph built on MOSDAC web content | MOSDAC pages, FAQs and product documents | https://hack2skill.com/event/bah2025?psNumber=ps2 |
| PS4 | LLM with chain-of-thought reasoning that plans and runs GIS processing steps | Open geodata (not confirmed which) | https://hack2skill.com/event/bah2025 |
| PS8 | Segmentation of rare land-cover classes in imbalanced training data | LISS-IV at 5.8 m from Bhoonidhi | https://hack2skill.com/event/bah2025?psNumber=ps8 |
| PS14 | Change detection and alerts for a user-drawn area. Asks for a web UI, email alerts, PostGIS storage and GeoJSON or shapefile output | LISS-4 at about 5 m, red, green and NIR bands, from Bhoonidhi | https://hack2skill.com/event/bah2025?psNumber=ps14 |

- Winner: a team that detected halo coronal mass ejections from Aditya-L1 data. No farm problem statement won. Source: https://indiatoday.in/amp/science/story/aditya-l1-isro-solar-storm-coronal-mass-ejection-flare-sun-2785163-2025-09-10

### BAH 2026

- 15 problem statements. Registration ran 10 June to 1 July 2026. The finale ran 6 to 7 August 2026 at NRSC. More than 100,000 students in 15,104 teams took part, and 34 teams reached the finale. Sources: https://hack2skill.com/event/bah2026, https://www.isro.gov.in/Bharatiya_Antariksh_Hackathon_2026_Grand_Finale.html

| ID | Title or paraphrase | Data named |
|---|---|---|
| PS06 | "AI-Driven Automated Crop type, Moisture Stress Detection and irrigation advisory..." Classify crop type, detect moisture stress across growth stages, and give irrigation advice | Moderate-resolution optical and microwave satellite data (sensors not named in the title) |
| PS02 | Generative AI to remove clouds from LISS-IV scenes | LISS-IV |
| PS05 | AI digital twin of India's climate | Not confirmed |
| PS11 | Cross-modal image retrieval across sensors | Not confirmed |
| PS12 | Temporal frame interpolation for satellite image series | Not confirmed |

- PS06 finalists: I.N.T.E.R.S.T.E.L.L.A.R (NIT Raipur and DAVV Indore), Logic Legion, and FasalSarathi. Source: https://www.isro.gov.in/media_isro/pdf/BAH_2026_Shortlisted_Teams_16072026_Publication.pdf
- Results. Sources: https://www.instagram.com/p/DbxJnUSGKTh/, https://djsce.ac.in/docs/ISRO%20Bharatiya%20Antariksh%20Hackathon.pdf
  - Winner: The Fellowship of the Ring (DJSCE Mumbai), on PS12.
  - First runner-up: Flux Fixers, on PS1.
  - Second runner-up: ASAP, on PS9.
  - Consolation prizes: I.N.T.E.R.S.T.E.L.L.A.R (PS06) and Cosmic Crasherzzz.
- Public PS06 repositories. None is confirmed as a finalist's code.
  - AgriSat: https://github.com/srinidhikuchana/AI-driven-crop-monitoring-and-irrigation-advisory-system. It reads Sentinel-1 and Sentinel-2 through the Copernicus Data Space Statistics API, soil from SoilGrids, weather from OpenWeatherMap, and writes advice with an LLM through OpenRouter. It falls back to synthetic data when keys are missing. It covers 5 crops and 4 growth stages. MIT licence.
  - agripulse (Shamratha): uses VCI and FAO-56 with Sentinel-1, Sentinel-2 and MODIS. Found through https://github.com/topics/remot (exact repo URL not confirmed).
  - KrishiRakshak AI: https://github.com/ROSHAN-KUMAR-DUTTA/KrishiRakshak-AI-ISRO-HACKATHON-
  - A Prezi deck with a farmer advisory card: https://prezi.com/page/sbclsr7r6dcw/

## Smart India Hackathon (SIH)

SIH is run by the Ministry of Education's Innovation Cell. Each ministry or state posts problem statements. Software finals award one winner per problem statement.

### ISRO problem statements in SIH

| Year | IDs | Topics | Farm related? | Source |
|---|---|---|---|---|
| 2022 | SS596, SS597 and others from SAC | Water quality from imagery, flood inundation probability | No, though SS597 touches flood risk to fields | https://vedas.sac.gov.in/en/sih2022.html |
| 2023 | ISRO and NRSC set | Change detection of human activity (NRSC), explainable AI for heavy rain | No | https://vedas.sac.gov.in/en/sih2023.html |
| 2024 | SIH1732 to SIH1741 | SAR colourisation, INSAT cloud-optimised GeoTIFF, WMS segmentation and others | No | https://vedas.sac.gov.in/en/sih2024.html, https://www.sih.gov.in/letters/SIH_PS_2024.xlsx |
| 2025 | SIH25169 to SIH25179 | Thermal IR super-resolution guided by optical data (SIH25171), MAITRI astronaut assistant (SIH25175), NavIC error prediction (SIH25176), phone navigation (SIH25177), quantum email (SIH25179) | No | https://sih2025probelmstatement.vercel.app, https://www.sih.gov.in/sih2025/sih2025-grand-finale-result |
| 2026 | SIH26166 to SIH26176 | SIH26167 "SatQuery AI", a vision-language assistant for satellite images. Its hidden test set uses Cartosat-2S and RISAT pairs, and its background names agricultural monitoring as a use | Partly | https://www.sih.gov.in/sih2026PS |

The SIH 2025 ISRO winners, for example Vasuki (Manipal) on SIH25172, are on the finale result page above. None worked on farms.

### Farm problem statements from other bodies

SIH 2024. Source for all rows: https://www.sih.gov.in/letters/SIH_PS_2024.xlsx

| ID | Body | Paraphrase |
|---|---|---|
| SIH1554 | UAS Dharwad (ICAR) | Smart irrigation system |
| SIH1571 | Ministry of Jal Shakti | Drone sensing of evapotranspiration |
| SIH1638 | Not confirmed | Crop disease prediction |
| SIH1639 | Not confirmed | Fertiliser optimiser using soil, crop and weather data |
| SIH1640 | Not confirmed | Contract farming platform |
| SIH1647 | Department of Consumer Affairs | Price prediction for farm produce |
| SIH1673 | Not confirmed | Crop disease reporting portal |
| SIH1689 | Ministry of Jal Shakti | Water footprint of crops |
| SIH1691 | Ministry of Jal Shakti | Adapting irrigation command areas to shifting cropping patterns |

SIH1691 is the closest to rotation planning in any SIH year: it asks how canal water plans should follow changes in what farmers grow. SIH 2024 winners per problem statement were not collected (not confirmed).

SIH 2025. Sources: https://sih2025probelmstatement.vercel.app and https://www.sih.gov.in/sih2025/sih2025-grand-finale-result unless noted.

| ID | Body | Paraphrase | Public winner |
|---|---|---|---|
| SIH25010 | Government of Punjab | Smart crop advisory for small and marginal farmers (406 idea submissions) | Not confirmed |
| SIH25030 | Government of Jharkhand | AI crop recommendation (302 idea submissions) | Not confirmed |
| SIH25044 | Government of Odisha | Crop yield prediction | Not confirmed |
| SIH25074 | Government of Kerala | AI personal farming assistant | Team Blessed |
| SIH25075 | Government of Kerala | Gamified sustainable farming | InnoVeda_75 |
| SIH25076 | Government of Kerala | Farmer query advisory | PLAN B_ |
| SIH25099 | MathWorks India | Crop health and soil condition from multispectral or hyperspectral images | Not confirmed |
| SIH25168 | MoA&FW, Digital Agriculture Division | "Enhancing farmer productivity through innovative technology solutions" | Team InnoSphere (Amrita, Amaravati) |
| SIH25262 | PMFBY | AI real-time analysis of crop images for insurance | Imaginary_Coders (source is a LinkedIn snippet, not confirmed) |
| SIH25263 | PMFBY | "Farm-Level Yield Estimation Using Very-High Spatial Resolution Data and Robust Crop Models" | Graviton (Amrutvahini College). Source: https://avcoe.org/pdf/Final%20KAVADASA%20SEM-I%202025-2026_compressed.pdf |
| SIH25264 to SIH25268 | MoA&FW Crops division | SIH25265 covers the millets value chain. Other titles not confirmed | Not confirmed |
| SIH25269 to SIH25276 | MoA&FW Oil Palm mission | Titles not confirmed | Not confirmed |

A team called "Farm Copilot" won SIH25229, but that is an NTRO problem statement unrelated to farms.

SIH 2026 (finals not yet held at the time of writing). Source: https://www.sih.gov.in/sih2026PS

| ID | Body | Paraphrase |
|---|---|---|
| SIH26086 | MoES, NCMRWF | Hyperlocal prediction of monsoon onset and breaks to guide kharif sowing. The text explains that a false onset leads farmers to sow early and lose the crop |
| SIH26074 | IMD | Downscale forecasts from block to gram panchayat level for agromet advisories |
| SIH26240 | Ministry of Tribal Affairs | Plan spring recharge in hill areas |
| SIH26015 | Department of Land Resources | Watershed work from geo-tagged photos |
| SIH26131 | Government of Maharashtra | Crop disease detection |
| SIH26180 | Qualcomm | On-device farming assistant that runs without the cloud |

## Bhuvan and NRSC hackathons

- Bhuvan IISF 2023 Space Hackathon topics: NLP and voice queries on geodata, an offline mobile GIS app, a Bhuvan voice chatbot, extraction of farm ponds and check dams, LULC level-2 classification, and links between LULC and state GDP. Winners are not confirmed. Source: https://bhuvan.nrsc.gov.in/hackathon/iisf2023
- IIRS hackathons: we found no public IIRS hackathon with a farm problem statement (not confirmed).

## IN-SPACe

- The IN-SPACe Seed Fund use-case call (results June 2026) drew 92 proposals and funded 15. The problem statements came from consultation with MoA&FW. Source: https://mediaexpress24.com/business/in-space-announces-winners-of-space-technology-use-cases-under-seed-fund-scheme
  - Pest and disease forewarning for major crops: Infosys, Bhoomicam and AgCane.
  - SAR applications using NISAR data: JalViks, Nansei Restoration with Semantic Technologies, and Agritech Services.
- No code from these grantees is public (not confirmed).

## Patterns worth noting

- ISRO judges reward strong use of ISRO data. In BAH, problem statements name Bhoonidhi sensors directly. A Field Shift build that reads one ISRO product (for example EOS-04 soil moisture or NISAR) would speak to the ISRO partner judges.
- Indian farm problem statements repeat four needs: advice for small and marginal farmers, local-language or voice access, sowing-time risk from the monsoon, and farm-level yield for insurance.
- Winning farm teams in SIH rarely publish repos, so their methods are not confirmed.

## Sources

- https://isro.hack2skill.com/2024
- https://nknewsodisha.in/2024/08/heritage-institute-students-shine-as.html
- https://outlookindia.com/hub4business/honorable-president-of-india-felicitated-students-team-from-heritage-institute-of-technology
- https://hack2skill.com/event/bah2025
- https://hack2skill.com/event/bah2025?psNumber=ps2
- https://hack2skill.com/event/bah2025?psNumber=ps8
- https://hack2skill.com/event/bah2025?psNumber=ps14
- https://indiatoday.in/amp/science/story/aditya-l1-isro-solar-storm-coronal-mass-ejection-flare-sun-2785163-2025-09-10
- https://hack2skill.com/event/bah2026
- https://www.isro.gov.in/Bharatiya_Antariksh_Hackathon_2026_Grand_Finale.html
- https://www.isro.gov.in/media_isro/pdf/BAH_2026_Shortlisted_Teams_16072026_Publication.pdf
- https://www.instagram.com/p/DbxJnUSGKTh/
- https://djsce.ac.in/docs/ISRO%20Bharatiya%20Antariksh%20Hackathon.pdf
- https://github.com/srinidhikuchana/AI-driven-crop-monitoring-and-irrigation-advisory-system
- https://github.com/topics/remot
- https://github.com/ROSHAN-KUMAR-DUTTA/KrishiRakshak-AI-ISRO-HACKATHON-
- https://prezi.com/page/sbclsr7r6dcw/
- https://vedas.sac.gov.in/en/sih2022.html
- https://vedas.sac.gov.in/en/sih2023.html
- https://vedas.sac.gov.in/en/sih2024.html
- https://www.sih.gov.in/letters/SIH_PS_2024.xlsx
- https://sih2025probelmstatement.vercel.app
- https://www.sih.gov.in/sih2025/sih2025-grand-finale-result
- https://avcoe.org/pdf/Final%20KAVADASA%20SEM-I%202025-2026_compressed.pdf
- https://www.sih.gov.in/sih2026PS
- https://bhuvan.nrsc.gov.in/hackathon/iisf2023
- https://mediaexpress24.com/business/in-space-announces-winners-of-space-technology-use-cases-under-seed-fund-scheme
