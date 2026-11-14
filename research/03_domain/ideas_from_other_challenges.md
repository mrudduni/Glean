# Ideas from other challenges

Phase 2 research, gathered 2026-11-14. This file lists ideas Field Shift could borrow from the challenges in `../02_hackathon/isro_and_indian_challenges.md` and `../02_hackathon/other_global_challenges.md`, with a focus on Indian smallholders. Each idea names where it came from and how hard it would be in a 2-day build. Ratings: core (do it), stretch (if time allows), later (after the hackathon).

## Seasons and rotation history

| Idea | Source | Rating |
|---|---|---|
| Model the year as kharif, rabi and zaid seasons for Indian fields, not as one crop per year. A rotation becomes a sequence of season slots, some of them fallow | NRSC LULC has separate kharif, rabi, double, triple and annual crop layers: https://www.nrsc.gov.in/nrscnew/assets/pdf/atlas/LULC/LULC%20Atlas%20Final%20With%20Cover_March2024.pdf | Core |
| Fill the farmer's current rotation from parcel crop maps across past years, then let the farmer correct it | Krishi-DSS parcel-level crop maps, which its launch release links to crop rotation: https://pib.gov.in/PressReleasePage.aspx?PRID=2045987 | Stretch (access not confirmed) |
| Show bare-field periods between seasons from an NDVI time series of the field | VEDAS Temporal API: https://vedas.sac.gov.in/vconsole | Stretch |

## Data under monsoon cloud

| Idea | Source | Rating |
|---|---|---|
| Use SAR for kharif months, when optical images are cloudy. NISAR L-band soil moisture and GCOV through ASF count as NASA data | https://nisar-docs.asf.alaska.edu/products-overview | Core |
| Cross-check with EOS-04 soil moisture (500 m) and mark where the two disagree | https://www.isro.gov.in/High-Resolution_Operational_Soil_Moisture_Product.html | Stretch |
| Label NISAR soil moisture as provisional in the evidence panel, since validated SME2 comes in 2027 | https://nisar-docs.asf.alaska.edu/availability-overview | Core |

## Sowing and weather risk

| Idea | Source | Rating |
|---|---|---|
| Add a false monsoon onset check: count past years where early rain was followed by a long dry spell, and flag the sowing risk for each rotation's kharif crop | SIH26086 (MoES, NCMRWF): https://www.sih.gov.in/sih2026PS | Core. Can use IMERG and NASA POWER history |
| Report advice at gram panchayat scale, matching how agromet advisories reach farmers | SIH26074 (IMD): https://www.sih.gov.in/sih2026PS | Later |
| Show district drought class next to the field's own drought indicators | VEDAS Digital Drought Manual (NADAMS): https://vedas.sac.gov.in/krishi/dashboard/index.html | Stretch |

## Tiny fields

| Idea | Source | Rating |
|---|---|---|
| Treat small fields with care: compute statistics over the field polygon with a buffer inside the edge, and warn when the field covers few pixels of a coarse product | AgriFieldNet winners found fields very small with low variation inside each one: https://radiant.earth/blog/2023/04/behind-the-agrifieldnet-model | Core |
| Show the pixel size of each dataset against the field outline, so the farmer sees why 9 km soil moisture is only regional context | NRSC LULC at 56 m is about 0.3 ha per pixel, larger than many fields: same atlas as above | Core |

## Local knowledge

| Idea | Source | Rating |
|---|---|---|
| Encode regional farming knowledge as explicit rules, for example irrigation system type and season timing by region. These rules beat model tuning in the Bihar yield contest | Digital Green yield challenge, third-place write-up: https://zindi.world/competitions/digital-green-crop-yield-estimate-challenge/discussions/19696 | Core |
| Ask the farmer whether the field is rainfed or irrigated, and change which rotations are allowed | Repeats across SIH farm problem statements, for example SIH25010 for small and marginal farmers: https://sih2025probelmstatement.vercel.app | Core |

## Language, voice and delivery

| Idea | Source | Rating |
|---|---|---|
| Offer a voice or local-language summary of each rotation card | Bhuvan IISF 2023 voice chatbot topic: https://bhuvan.nrsc.gov.in/hackathon/iisf2023. Kerala SIH25074 and SIH25076: https://sih2025probelmstatement.vercel.app | Stretch |
| Send a short text summary through WhatsApp, which Indian farmers already use for farm advice | Digital Green FarmerChat works on WhatsApp and Telegram in Hindi, Telugu, English and Bhojpuri: https://help.gooey.ai/farmerchat, https://gooey.ai/farmerchat | Later. For the demo, a "share as text" button is enough |
| Keep a phone hotline or IVR path in mind for farmers without smartphones | CGIAR Inspire winners CubicA and TALIA ran advisory hotlines: https://bigdata.cgiar.org/inspire/inspire-winners/ | Later |
| Make pages light enough for slow mobile data, and cache the last result offline | Sangrahi offline field app: https://vedas.sac.gov.in/content/vcms/pdf/0_mosdac_vedas_newsletter_oct2025.pdf. Qualcomm SIH26180 asks for on-device use: https://www.sih.gov.in/sih2026PS | Stretch |

## Ground truth from farmers

| Idea | Source | Rating |
|---|---|---|
| Let the farmer add a geo-tagged photo of the field as evidence, shown next to the satellite view | AgriSnapp (FAO Reboot the Earth 2025): https://fao.org/e-agriculture/news/reboot-earth-rome-science-and-innovation-forum-2025-youth-led-innovation-driving-open-source-0. Croppie and picture-based insurance: https://bigdata.cgiar.org/inspire/inspire-winners/ | Later |
| Keep any model small enough to run on modest hardware | CGIAR crop damage rules: one GPU, under 8 hours of training, 4-core 16 GB deployment: https://zindi.world/competitions/cgiar-crop-damage-classification-challenge | Core as a design rule |

## Build and demo habits

| Idea | Source | Rating |
|---|---|---|
| Fall back to cached or sample data when an API key or service is missing, and label it as sample data in the UI | AgriSat (BAH 2026 PS06 repo): https://github.com/srinidhikuchana/AI-driven-crop-monitoring-and-irrigation-advisory-system | Core |
| Let users draw a field and save it, then send alerts when conditions change | BAH 2025 PS14 asks for exactly this with PostGIS and GeoJSON: https://hack2skill.com/event/bah2025?psNumber=ps14 | Later (alerts); core (draw and save) |
| Name the ISRO product in the evidence panel when it is used, since partner judges value their own data | EO Dashboard data awards per agency: http://eodashboardhackathon.org/awards | Stretch |

## Insurance and policy links

- Mention in the pitch that crop insurance in India already uses satellite yields. YES-TECH gives technology yields at least 30% weight, and Madhya Pradesh gives them 100%. Sources: https://pib.gov.in/PressReleasePage.aspx?PRID=2085179, https://downtoearth.org.in/agriculture/can-technology-make-indias-crop-insurance-payouts-more-accurate
- This shows the evidence style Field Shift uses is already trusted by Indian institutions. Field Shift should not claim to predict insurance payouts.

## Things to avoid

- Do not depend on Bhoonidhi API approval or Krishi-DSS access during the hackathon. Both are not confirmed for public use.
- Do not use AgriStack or Digital Crop Survey plot data. It is personal farmer data and not open.
- Do not present an LLM's advice as fact. AgriSat and FarmerChat both use LLMs to write advice, but Field Shift must tie each claim to a cited source, as `../../CLAUDE.md` requires.

## Sources

- https://www.nrsc.gov.in/nrscnew/assets/pdf/atlas/LULC/LULC%20Atlas%20Final%20With%20Cover_March2024.pdf
- https://pib.gov.in/PressReleasePage.aspx?PRID=2045987
- https://vedas.sac.gov.in/vconsole
- https://nisar-docs.asf.alaska.edu/products-overview
- https://nisar-docs.asf.alaska.edu/availability-overview
- https://www.isro.gov.in/High-Resolution_Operational_Soil_Moisture_Product.html
- https://www.sih.gov.in/sih2026PS
- https://vedas.sac.gov.in/krishi/dashboard/index.html
- https://radiant.earth/blog/2023/04/behind-the-agrifieldnet-model
- https://zindi.world/competitions/digital-green-crop-yield-estimate-challenge/discussions/19696
- https://sih2025probelmstatement.vercel.app
- https://bhuvan.nrsc.gov.in/hackathon/iisf2023
- https://help.gooey.ai/farmerchat
- https://gooey.ai/farmerchat
- https://bigdata.cgiar.org/inspire/inspire-winners/
- https://vedas.sac.gov.in/content/vcms/pdf/0_mosdac_vedas_newsletter_oct2025.pdf
- https://fao.org/e-agriculture/news/reboot-earth-rome-science-and-innovation-forum-2025-youth-led-innovation-driving-open-source-0
- https://zindi.world/competitions/cgiar-crop-damage-classification-challenge
- https://github.com/srinidhikuchana/AI-driven-crop-monitoring-and-irrigation-advisory-system
- https://hack2skill.com/event/bah2025?psNumber=ps14
- http://eodashboardhackathon.org/awards
- https://pib.gov.in/PressReleasePage.aspx?PRID=2085179
- https://downtoearth.org.in/agriculture/can-technology-make-indias-crop-insurance-payouts-more-accurate
