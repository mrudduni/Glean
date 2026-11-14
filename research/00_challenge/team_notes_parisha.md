# Team notes from Parisha Gupta

Source: `NASA_space_apps_research.docx` on the `Parisha` branch of https://github.com/mrudduni/Team-Brackets (commit "Add research doc"). This file summarises the document so the rest of the research can build on it. The phase 2 agents are checking each factual claim, and the results go into `research/06_context/news_and_reports.md` under "Haryana claims checked".

## Proposed focus

- Region: the Karnal, Kurukshetra, and Kaithal belt in Haryana, India, inside the northwestern Indo-Gangetic Plain.
- Current rotation: rice in kharif (June to November) and wheat in rabi (November to March).
- Candidate crops: rice, maize, wheat, and mustard.
- Core NASA data: NASA POWER, SMAP, MODIS NDVI, and GPM IMERG.

## Problem framing

- Farmers lack tools that turn NASA data into rotation choices.
- The rice-wheat system dominates because of minimum support prices (MSP). It drives groundwater decline, soil degradation, and sodium build-up from flood irrigation.
- Environmental gains alone will not move farmers. An alternative must also pay.
- Paddy stubble burning adds air pollution, and maize residue may ease it.

## Proposed switches

- Kharif: rice to maize. The notes claim maize needs about 80 percent less water than rice and that the state pays farmers to switch.
- Rabi: wheat to mustard. The notes claim mustard needs less water, breaks pest cycles, and has strong domestic demand.
- A cited study reports that switching kharif rice to pearl millet or sorghum and rabi wheat to sorghum could cut water use by 32 percent, raise calories by 39 percent, and raise profit by 140 percent. It also reports that crop switching saves more groundwater than drip irrigation.

## Proposed method: Water-Smart Rotation Score

A weighted score from 0 to 100 with traffic-light colours:

| Factor | Weight | Input |
|---|---|---|
| Soil moisture health | 40 percent | SMAP root-zone moisture percentile against a 5-year history |
| Precipitation outlook | 25 percent | IMERG monthly rainfall against a 20-year climatology |
| Thermal suitability | 20 percent | POWER growing degree days against crop needs, plus a terminal heat warning for wheat |
| Water savings bonus | 15 percent | Seasonal water use per crop against the rice-wheat baseline, plus the Mera Paani Meri Virasat incentive |

The notes also propose a 30-day NDVI forecast from SMAP root-zone moisture. They base it on NASA's Dynamic Agricultural Productivity Indicator (DAPI) paper: https://ntrs.nasa.gov/api/citations/20240012812/downloads/GRL_final.pdf

## Claims that need checking

These figures appear in the notes without a primary source. The phase 2 research checks each one.

- Seasonal water use: rice about 1,500 mm, maize about 500 mm, wheat about 400 mm, and mustard about 250 mm.
- Maize uses about 80 percent less water than rice.
- Mera Paani Meri Virasat pays Rs 7,000 per acre to switch from paddy.
- Wheat needs 1,800 to 2,200 growing degree days.
- The DAPI lead time of about 30 days and how well it works in India.

## Open design questions the notes raise

- The score mixes in-season signals (this month's soil moisture) with rotation planning (a multi-year choice). The tool may need two modes: a rotation planner and a season check.
- The weights come from an AI suggestion, not from farmers or literature. They should become farmer-set priorities with a default that we can defend.

## Project to-do list from the notes

- Integrate POWER and GPM.
- Integrate SMAP and NDVI.
- Build the UI: map, farm boundary, and rotation comparison.
- Write the crop suitability logic.
- Make the presentation, video, and write-up.
- Submission checklist: project page, demo video, GitHub repo, app link, presentation, and a list of the NASA data used.
