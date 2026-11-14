# Existing crop-rotation and cover-crop decision tools

This file reviews tools a farmer, adviser, or researcher can already use to plan rotations, pick cover crops, track drought, or simulate crops. For each tool it notes what the tool does well, where it falls short, and what that means for our Field Shift project. The last section lists gaps our tool can fill.

Our tool has a specific job. It must take NASA Earth observations plus soil, crop, and farmer priorities, compare at least three rotation strategies including the current one, and explain the reasoning, evidence, benefits, information gaps, and risks for each. Very few existing tools do all of that in one place.

## Summary table

| Tool | Owner | Main job | Uses satellite data | Compares whole rotations | Explains trade-offs | Cost |
| --- | --- | --- | --- | --- | --- | --- |
| MCCC Cover Crop Decision Tool | Midwest Cover Crops Council, MSU | Pick cover crop species by county, cash crop window, and goal | No | No | Partly (goal ratings) | Free |
| NECCC Species Selector and Cover Crop Explorer | Northeast Cover Crops Council | Same idea for the Northeast, plus an N calculator | No | No | Partly | Free |
| SCCC Species Selector | Southern Cover Crops Council | Same idea for the South | No | No | Partly | Free |
| RUSLE2 | USDA ARS and NRCS | Sheet and rill erosion for a crop rotation | No | Yes (one at a time) | Erosion only | Free |
| Soil Conditioning Index (inside RUSLE2) | NRCS | Organic matter trend score | No | Yes (one at a time) | One score | Free |
| Conservation Stewardship Program tools | NRCS | Rank and pay for conservation, including rotation add-ons | No | Indirectly | Program scoring | Free (program) |
| Climate FieldView | Bayer | Farm data platform, field imagery, yield analysis | Yes (field health imagery) | No | Yield comparisons | Paid tiers |
| OpenET | OpenET consortium (NASA, USGS, partners) | Field-scale actual ET from satellites | Yes (Landsat thermal) | No | No | Free |
| CropManage | UC Agriculture and Natural Resources | Irrigation and N scheduling | No (weather station ET) | No | No | Free |
| CropRota, ROTOR | Research groups (BOKU Vienna, ZALF) | Generate agronomically sound rotations | No | Yes | Rule-based | Research code |
| FAO AquaCrop | FAO | Yield response to water | No (user inputs) | Through scripted runs | No | Free |
| DSSAT | DSSAT Foundation | Process crop models for over 45 crops | No (user inputs) | Yes (sequence mode) | No | Free |
| APSIM | APSIM Initiative | Farming systems simulation | No (user inputs) | Yes | No | Free for non-commercial use |
| USDA Climate Hubs tools | USDA | Regional adaptation tools and links | Some | No | Some narrative | Free |
| U.S. Drought Monitor | NDMC, NOAA, USDA | Weekly drought map | Indirectly | No | No | Free |
| Crop-CASMA | USDA NASS and George Mason University, NASA funded | SMAP soil moisture and MODIS vegetation maps for cropland | Yes (SMAP, MODIS) | No | No | Free |
| NASA Harvest and GEOGLAM Crop Monitor | NASA Harvest consortium, GEO | Global crop condition and food supply assessments | Yes | No | Narrative for policy users | Free reports |

## Cover crop selector tools

### Midwest Cover Crops Council (MCCC) Cover Crop Decision Tool

The MCCC tool helps farmers choose cover crops at the county level. The user picks a state and county, enters the cash crop planting and harvest dates, and chooses goals such as erosion control, nitrogen scavenging, or weed suppression. The tool then lists species with ratings and seeding windows. Each state's data comes from a team of researchers, Extension staff, NRCS staff, crop advisers, seed dealers, and farmers, who adapted the SARE book Managing Cover Crops Profitably to local conditions. The tool uses current climate data to set establishment windows.

What it does well. It packages expert consensus in a form farmers trust, it is local to the county, and it frames choices around farmer goals. The OSU crimson clover fact sheet shows how state teams turn its ratings into short guides (for example, crimson clover rates "very good" as a nitrogen source and supplies 70 to 150 lb total N per acre).

Where it falls short. It picks a cover crop for one gap between cash crops; it does not compare multi-year rotations. Ratings are expert opinion, not field-specific evidence. It uses no satellite data on current soil moisture, drought, or past field use. The MCCC site itself notes that the calendar cannot handle a cash crop that spans two calendar years, such as winter wheat, without a workaround.

### Northeast and Southern cover crop councils (Species Selector, Cover Crop Explorer)

The Northeast Cover Crops Council (NECCC) offers a Species Selector, a Cover Crop Explorer that browses species by USDA hardiness zone, and a Cover Crop Nitrogen Calculator that estimates residue breakdown and N release after termination. The Southern Cover Crops Council runs a similar Species Selector that asks for site conditions, goals, and the cash crop growing window. The USDA Northeast Climate Hub lists the Species Selector among its tools.

What they do well. They share a common design across regions, and the NECCC nitrogen calculator goes one step past species choice to estimate a nutrient outcome.

Where they fall short. They share the MCCC limits: one cover crop decision at a time, expert ratings, and no live Earth observation inputs.

## USDA NRCS conservation tools

### RUSLE2

RUSLE2 estimates average annual sheet and rill erosion over a full crop rotation in tons per acre per year. It uses A = R x K x LS x C x P, where R is rainfall erosivity, K is soil erodibility, LS is slope length and steepness, C is cover and management (residue, tillage, rotation, cover crops), and P is support practices such as contouring and strip cropping. NRCS compares the result with the soil loss tolerance (T), which ranges from 1 to 5 tons per acre per year. Penn State Extension describes how planners use it to test how practice changes alter soil loss.

What it does well. It is the official NRCS planning model, it evaluates a whole rotation, and its factors map cleanly to data we can get (R from rainfall, K from SSURGO, LS from SRTM or lidar, C from crop and residue cover).

Where it falls short. It covers only water erosion from sheet and rill flow. It needs trained users and local databases, and it does not account for current-season weather, drought, or water use.

### Soil Conditioning Index (SCI)

The SCI runs inside RUSLE2 and predicts whether a system will gain or lose soil organic matter. Its formula weights three parts: organic matter (40 percent), field operations (40 percent), and erosion (20 percent). A negative score means organic matter is predicted to decline.

What it does well. It gives a single, explainable soil health trend for a rotation, which fits our "benefits and risks" output.

Where it falls short. It is a relative index, not a measurement, and it inherits the RUSLE2 setup burden.

### Conservation Stewardship Program (CSP)

CSP is an NRCS program, not a calculator. It pays producers to keep and add conservation practices, including add-on payments for adopting or improving a resource-conserving crop rotation. NRCS uses its own ranking and evaluation tools to score applications.

What it does well. It links rotation changes to money, which matters to farmers.

Where it falls short. It is a program with paperwork and local staff review, not a public decision tool that a farmer can run in a few minutes.

## Commercial farm platforms

### Climate FieldView (Bayer)

FieldView collects planting, application, and yield data from equipment, shows field health imagery, and lets users compare yields across fields, inputs, and practices with maps and charts. Some features need a paid subscription.

What it does well. It works with machine data and gives farmers a polished, field-level view of what happened.

Where it falls short. It looks backward at yield, not forward at rotation options. The models are proprietary, so users cannot see the reasoning. It does not use NASA soil moisture, ET, or groundwater data in an open way.

## Water and irrigation tools

### OpenET

OpenET produces field-scale (30 m) actual evapotranspiration from Landsat thermal data and an ensemble of six models: ALEXI/DisALEXI, eeMETRIC, geeSEBAL, PT-JPL, SIMS, and SSEBop. It runs on Google Earth Engine and offers daily, monthly, and annual values. Coverage started with the western United States, and a Brazil expansion is under way. Melton et al. (2021) reported that the ensemble mean and several models came within about 5 percent of flux tower ET at closed-balance sites.

What it does well. It measures how much water each field actually used, which is the missing number in most rotation advice. The data are free and peer reviewed.

Where it falls short. It reports water use but gives no advice on what to plant. Coverage and accuracy vary by region, and OpenET publishes a list of known issues.

### CropManage (UC ANR)

CropManage is a free web app for irrigation and nitrogen scheduling. It tracks a soil water balance from weather, soil, and crop data and recommends irrigation run times and N rates. Irrigation advice covers California, Arizona, Hawaii, and Guam; fertilizer planning works nationwide. It supports over 40 crops, mostly vegetables and orchard crops plus alfalfa and corn. UC reports trials with 27 percent less water in broccoli and up to 31 percent less N in lettuce.

What it does well. It shows that a free, research-backed tool with plain recommendations can win grower trust, and it offers an API.

Where it falls short. It manages one crop in one season. It does not plan rotations or use satellite data.

## Rotation generators and crop models

### CropRota and ROTOR

CropRota (Schönhart et al., 2011) generates typical multi-year crop rotations for farms or regions from observed land use and agronomic rules, so that larger land use models can use realistic rotations. ROTOR (Bachinger and Zander, ZALF) is a rule-based tool that generates and evaluates rotations for organic farms, checking N supply, weed and disease risk, and yield. Reckling et al. (2016) describe rule-based rotation generators like these as static tools designed to produce agronomically sound rotations.

What they do well. They encode the expert rules our tool needs, such as minimum break years and preceding-crop effects.

Where they fall short. They are research code with little user interface. They use no live satellite data and offer little explanation for a farmer.

### FAO AquaCrop

AquaCrop is FAO's crop water productivity model. It simulates the yield response of herbaceous crops to water and suits places where water limits yield. It uses few parameters and intuitive inputs. FAO now offers the source code in Python (version 7.3), and the community package AquaCrop-OSPy is also available.

What it does well. It is simple enough to calibrate in a hackathon and directly answers "what happens to yield under drought."

Where it falls short. It simulates one crop per season and does not model nitrogen in detail or rotation effects such as pest breaks.

### DSSAT

DSSAT bundles process-based crop models for over 45 crops with tools for weather, soil, genetics, and management data. Users in over 198 countries have applied it to precision management, climate impact studies, and food security. Version 4.8.6 came out in July 2026.

What it does well. It has deep science, a sequence mode for multi-year rotations, and decades of validation.

Where it falls short. It is a Windows desktop program with a steep learning curve and many inputs. Results need expert reading.

### APSIM

APSIM is a farming systems simulator that has run for over 30 years. It models soil, plant, and climate interactions across crops, pasture, and agroforestry, and its developers are linking it with remote sensing and AI.

What it does well. It handles multi-year rotations, soil water, and nitrogen carryover better than single-season models.

Where it falls short. It needs skilled setup, and its license terms differ for commercial use. Like DSSAT, it gives numbers, not explanations.

## Climate and drought services

### USDA Climate Hubs tools

The regional Climate Hubs list decision tools for farmers, including cover crop species selectors, a cover crop nitrogen calculator, and tools such as Grass-Cast for rangeland. The North Central hub's adaptation guidance names practical shifts such as switching from corn to sorghum or sudangrass, using drought-tolerant varieties, reduced tillage, and cover crops.

What they do well. They curate trusted tools and adaptation options by region.

Where they fall short. They are mostly a catalog that links out to separate tools, so a farmer must combine the outputs by hand.

### U.S. Drought Monitor (USDM)

The USDM is a weekly map produced since 1999 by the National Drought Mitigation Center, NOAA, and USDA. Authors blend precipitation, streamflow, reservoirs, temperature, evaporative demand, soil moisture, and vegetation health with impact reports from over 450 local experts. It looks back, not forward; maps come out on Thursdays with data through Tuesday morning. USDA uses it to trigger disaster declarations and program eligibility.

What it does well. It is the most trusted drought label in U.S. agriculture.

Where it falls short. It is a coarse, regional category, not a field-scale measure. It does not suggest crop or rotation changes.

### Crop-CASMA (NASA SMAP for agriculture)

Crop-CASMA is a web map built by USDA NASS and George Mason University with NASA and NASS funding. It serves NASA SMAP Level 4 surface and root-zone soil moisture at 9 km (3-hourly, daily, weekly), a 1 km soil moisture product made from SMAP, MODIS land surface temperature, and soil texture, soil moisture anomalies, and MODIS 250 m NDVI, VCI, and MVCI from 2000. Its anomaly is the percent departure from the 2015-to-present mean. NASS began using SMAP data in crop progress reports in April 2021.

What it does well. It puts NASA soil moisture in front of agricultural users in a simple map, and the data are public domain.

Where it falls short. It monitors conditions; it does not translate them into planting or rotation choices. The 9 km and 1 km grids are coarse for single fields, and the anomaly baseline (2015 onward) is short.

### NASA Harvest and GEOGLAM

NASA Harvest is NASA's global food supply and agriculture consortium. It uses Earth observation and partnerships to assess crop conditions, production risk, and food supply, and it helps produce the GEOGLAM Crop Monitor reports. Recent news items include a crop-rotation verification system tested in Ukraine and the open Galileo multimodal Earth observation model.

What they do well. They set the standard for operational, satellite-based crop assessments and publish open models and datasets.

Where they fall short. Their users are governments, markets, and aid groups. They do not give a single farm advice on next season's rotation.

## Gaps our tool can fill

1. No tool compares three or more whole rotations side by side for one field and explains each one. Cover crop selectors handle one gap between cash crops, RUSLE2 scores one rotation at a time, and crop models need experts.
2. Free NASA data on soil moisture (SMAP), rainfall (IMERG), ET and water stress (OpenET, ECOSTRESS), and groundwater (GRACE) sit in monitoring tools like Crop-CASMA and the Drought Monitor, but none of them turns those signals into rotation advice.
3. Existing advice tools rarely show their evidence and uncertainty. Selectors give expert ratings and commercial platforms hide their models. A tool that states the evidence, the data gaps, and the items that need local review for each option would stand out.
4. Farmer priorities appear only as simple goal checkboxes in cover crop tools. No public tool weighs profit, water use, erosion, soil health, and risk tolerance together with a transparent method such as AHP or TOPSIS.
5. Field history is underused. The Cropland Data Layer and Crop Sequence Boundaries give each field's past crops, but tools rarely use them to detect the existing rotation, flag pest risks such as corn rootworm variants, or count bare-soil months.
6. Water use and erosion live in separate tools (OpenET or CropManage for water, RUSLE2 for soil loss). Our tool can show both for each rotation, using Kc-based ET estimates and RUSLE factors.
7. Climate-shift framing is missing. Few tools show how frost dates, growing degree days, heat stress, or drought frequency have changed for a field, which is the core of the "Field Shift" challenge.

## Sources

- MCCC selector tools: https://www.midwestcovercrops.org/selector-tools/
- OSU crimson clover fact sheet (MCCC data): https://cfaes.osu.edu/fact-sheet/crimson-clover-cover-crop-ohio
- NECCC decision tools: https://northeastcovercrops.com/decision-tool/
- Southern Cover Crops Council tools: https://southerncovercrops.org/cover-crop-resource-guide/cover-crop-decision-support-tools/
- USDA Northeast Climate Hub species selector: https://www.climatehubs.usda.gov/hubs/northeast/tools/cover-crop-species-selector
- Penn State Extension, Predicting soil loss with RUSLE2: https://extension.psu.edu/predicting-soil-loss-with-rusle2
- MSU Institute of Water Research, T value: http://www.iwr.msu.edu/rusle/tvalue.htm
- RUSLE2 handbook (NRCS): https://www.nrcs.usda.gov/sites/default/files/2022-10/RUSLE2%20Handbook_0.pdf
- Carlson (2016), The Soil Conditioning Index model service: https://docs.lib.purdue.edu/cgi/viewcontent.cgi?article=1111&context=agroenviron
- NRCS Conservation Stewardship Program: https://www.nrcs.usda.gov/programs-initiatives/conservation-stewardship-program
- Climate FieldView analysis features: https://climate.com/en-us/solutions/analyze-data.html
- OpenET ensemble description (Google Earth Engine catalog): https://developers.google.com/earth-engine/datasets/catalog/projects_openet_assets_ensemble_conus_gridmet_monthly_v2_1
- Melton et al. (2021), OpenET, JAWRA (https://doi.org/10.1111/1752-1688.12956), preprint: https://digitalcommons.csumb.edu/context/aes_fac/article/1029/viewcontent/OpenET___Filling_a_Critical_Data_Gap.pdf
- OpenET Brazil: https://etdata.org/openet-brazil-expansion/about-team-partners/
- CropManage: https://cropmanage.ucanr.edu/
- Schönhart et al. (2011), CropRota: https://ui.adsabs.harvard.edu/abs/2011EuJAg..34..263S/abstract
- ROTOR manual (ZALF): https://www.zalf.de/de/forschung_lehre/software_downloads/Documents/oekolandbau/rotor/manual_ROTOR.pdf
- Reckling et al. (2016): https://www.sciencedirect.com/science/article/pii/S1161030115300538
- FAO AquaCrop: https://www.fao.org/aquacrop/en/
- DSSAT: https://dssat.net/
- APSIM: https://www.apsim.info/
- USDA Climate Hubs tools: https://www.climatehubs.usda.gov/hubs/southwest/tools
- North Central Climate Hub adaptation resources: https://northcentralclimate.org/wp-content/uploads/sites/387/2023/05/Wilson_Adaptive-Management_20190826.pdf
- What is the USDM: https://droughtmonitor.unl.edu/About/WhatistheUSDM.aspx
- Crop-CASMA metadata (NASS): https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_cropcasma.htm
- NSIDC, SMAP in NASS crop progress: https://nsidc.org/news-analyses/news-stories/sensing-soil-moisture-better-crops
- NASA Harvest: https://www.nasaharvest.org/
