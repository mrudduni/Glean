# NASA and space agency agriculture news, 2024 to 2026

Gathered on 2026-11-14. This file covers NISAR, NASA Harvest and NASA Acres, OpenET, SMAP, ECOSTRESS, GRACE-FO and GRACE-C, Landsat, MODIS, NASA Earth science budgets, and Copernicus. "Snippet only" means we saw the text in search results and did not read the page. Read status for every URL is in [source_log.md](source_log.md).

## The short version

- NISAR science data is public. Validated L-band Level 0 to 2 products have been on the Alaska Satellite Facility (ASF) since 6 November 2026. The Level 3 soil moisture product is still provisional.
- OpenET has covered all 48 contiguous states since 16 December 2025.
- Congress rejected the proposed 47 percent cut to NASA science for FY2026. The FY2027 request repeats the cut and is not yet settled. NASA runs on a continuing resolution to 11 December 2026.
- We found no ended mission among those Field Shift uses. SMAP, GPM, GRACE-FO, and ECOSTRESS all went through the 2026 Senior Review, and results are not published.
- Landsat will move to commercial data. NASA and USGS plan one last government satellite and say free distribution will be "explored".

## NISAR (NASA-ISRO Synthetic Aperture Radar)

### Specifications

| Item | Value | Source |
|---|---|---|
| Bands | L-band SAR from NASA/JPL and S-band SAR from ISRO, the first satellite to fly both | https://science.nasa.gov/mission/nisar/about-the-satellite/ (19 Jul 2025) |
| Wavelength | L-band 24 cm. S-band 9.4 cm on NASA pages; a JPL image release rounds it to 10 cm | https://science.nasa.gov/mission/nisar/mission-overview (22 Jul 2025) |
| Antenna | 12 m mesh reflector on a 9 m boom, deployed 15 Aug 2025 | about-the-satellite page; https://www.isro.gov.in/NISAR_Mission_Science_Phase.html (28 Nov 2025) |
| Swath | 242 km, using SweepSAR | about-the-satellite page |
| Resolution | 3 to 10 m depending on mode | mission-overview page |
| Revisit | 12-day exact repeat, about 6 days on average using both ascending and descending passes | mission-overview page |
| Orbit | 747 km, 98.4 degrees, sun-synchronous dawn-dusk | mission-overview page |
| Launch | 30 Jul 2025 on GSLV-F16 from Sriharikota | mission-overview page; ISRO page |
| Design life | NASA needs 3 years of L-band data, ISRO needs 5 years of S-band | about-the-satellite page |
| First images | S-band on 19 Aug 2025 (Godavari Delta). L-band image of North Dakota farmland, taken 23 Aug 2025 and released 24 Sep 2025, showing fallow fields, soy and corn, and centre pivots | ISRO page; https://www.jpl.nasa.gov/images/pia26615/ (24 Sep 2025; exact URL slug not confirmed) |
| Science phase | ISRO announced it on 28 Nov 2025. NASA's quick-facts page says early January 2026. The sources differ | ISRO page; mission-overview page |
| Access | Free and open through Earthdata Search, ASF Vertex, the ASF Search API, and the `asf_search` Python package. S-band data goes through ISRO's Bhoonidhi portal | https://asf.alaska.edu/notices/nisar-l-band-data-now-publicly-available (21 Jul 2026) |

### Data release timeline

| Date | Release | Source |
|---|---|---|
| 23 Jan 2026 | 25 sample products | https://nisar-docs.asf.alaska.edu/availability-overview/ |
| 27 Feb 2026 | Beta release of more than 100,000 Level 1 to 3 products (over 500 TB) | https://www.earthdata.nasa.gov/news/nisar-mission-team-releases-over-100k-new-data-products (27 Feb 2026) |
| 20 Jul 2026 | Provisional, calibrated products at all levels, for acquisitions from 17 Jun 2026 | https://www.earthdata.nasa.gov/news/nisar-l-band-data-released-expanding-record-surface-changes (21 Jul 2026) |
| 6 Nov 2026 | Validated Level 0 to 2 products, for acquisitions from 21 Oct 2026 | availability-overview page (read in full) |
| 2027 | Reprocessing of the earlier backlog and a validated soil moisture product | availability-overview page |

Verdict on public release as of November 2026: confirmed. L-band data is public, and validated Level 0 to 2 products exist from 6 November 2026. The Level 3 soil moisture product is provisional, not validated.

### Products relevant to farms

Source: https://nisar-docs.asf.alaska.edu/products-overview (read in full).

- Level 2 GCOV: radiometrically terrain-corrected backscatter at 10, 20, or 80 m. It supports crop area, biomass, and soil moisture work and is the product most useful to Field Shift.
- Level 2 GSLC (geocoded single-look complex, 5 to 40 m) and GUNW (geocoded unwrapped interferogram, 80 m). GUNW supports subsidence work, such as in the Central Valley.
- Level 3 SME2: soil moisture at 200 m (coarser over the Sahara: 500 m per ASF, 400 m per NASA), from three algorithms.
- Crop area and biomass products cover only calibration and validation sites. The algorithms ship as notebooks that users can run elsewhere.

### Agriculture requirements and latency

- Requirement: map cropland and inundated area each season with at least 80 percent classification accuracy at 1 hectare. Biomass accuracy is within 20 Mg/ha over 80 percent of areas below 100 Mg/ha. Source: https://science.nasa.gov/mission/nisar/mission-requirements (23 Jul 2025, read in full).
- Latency: Level 2 backscatter within 48 hours, and SME2 soil moisture within 72 hours, delivered about twice per 12 days (snippet only). Raw Level 0B data takes 2 to 10 hours (snippet only).

### Design note for Field Shift

ASF warns that beta, provisional, and validated products differ in processing. If the tool mixes them, it may read a processing change as a real change in the field. A rotation tool that uses NISAR should use one processing level for any time series and say so.

## NASA Earth science budget

- FY2026 request (May 2025): a 24 percent cut to NASA and a 47 percent cut to the Science Mission Directorate, from $7.334 billion to $3.908 billion. Earth Science would have fallen to $1,033.2 million, and termination plans were drawn up for 19 operating missions. Sources: The Planetary Society, https://www.planetary.org/articles/advocacy-success-fy2026-nasa-budget, 15 Jan 2026, and SpacePolicyOnline, https://spacepolicyonline.com/news/great-news-for-nasa-in-the-house-senate-fy2026-appropriations-report/, 5 Jan 2026.
- FY2026 enacted: H.R. 6938, signed 23 Jan 2026. NASA gets $24.438 billion, Science $7.25 billion, and Earth Science $2,153.0 million. Landsat Next gets $110 million with a 2031 target. The law requires NASA to spend at least each division's amount. Sources: as above, plus https://www.planetary.org/articles/nasa-is-funded-now-what, 30 Jan 2026.
- Context: a 43-day federal shutdown in October and November 2025, and about 4,000 NASA staff left through deferred resignation. The Planetary Society says no active science mission was terminated by the end of 2025. Source: planetary.org, 30 Jan 2026.
- FY2027 request (3 Apr 2026): NASA $18.83 billion (minus 23 percent) and Science $3.894 billion (minus 46 percent). The Planetary Society counts 53 missions likely to end, 16 of them in Earth science, mostly climate and carbon missions such as OCO-2, OCO-3, and Aura. Source: https://www.planetary.org/articles/analyzing-the-fy-2027-nasa-budget-request, 23 Apr 2026. On 28 April 2026 the NASA Administrator told appropriators these missions were not yet cancelled. Source: The Register, https://www.theregister.com/2026/04/28/despite_proposed_science_cuts_nasa/, 28 Apr 2026.
- Current status: a continuing resolution signed 2 September 2026 holds NASA at $24.4 billion until 11 December 2026. The House committee bill gives Science $6 billion, and the Senate subcommittee bill released 12 November 2026 gives Science $7.43 billion. No FY2027 bill has passed. Sources: https://spacepolicyonline.com/news/house-clears-fy2027-cr-now-to-the-president/, 1 Sep 2026, and https://spacepolicyonline.com/news/senate-appropriations-cjs-subcommittee-proposes-24-9-billion-for-nasa-in-fy2027/, 12 Nov 2026.
- We found no executed termination of SMAP, GPM, GRACE-FO, ECOSTRESS, or Landsat. Not confirmed for any of them.

## 2026 Earth Science Senior Review

NASA invited 16 missions to the 2026 review, which covers FY2027 to FY2029: Aqua, Aura, ECOSTRESS, EMIT, GEDI, GPM, GRACE-FO, ICESat-2, OCO-2, OCO-3, PREFIRE, SAGE-III, SMAP, SWOT, TEMPO, and TSIS-1. Terra was not on the list. The panel met 13 to 17 April 2026, and guidance letters went out in August 2026. Source: https://science.nasa.gov/earth-science/senior-review-2026/, Jan 2026. Results for each mission are not published and not confirmed.

## SMAP

- SMAP was invited to the 2026 Senior Review (see above).
- A Version 8 Level 4 soil moisture product came out in 2026, with surface error (ubRMSE) of 0.039 m³/m³, meeting the mission requirement. Source: https://ntrs.nasa.gov/citations/20260006721 (snippet only).
- A September 2026 paper says SMAP has outlived its design life and has no definite follow-on mission, and that GNSS reflectometry can complement but not replace it. Source: https://ntrs.nasa.gov/citations/20260008832, 9 Sep 2026 (abstract read).
- We found no report of radiometer failure, but a 2026 statement that it still works is not confirmed. The radar failed in July 2015.
- The SMAP-based NDVI forecast paper (Le et al. 2024, GRL) is summarised in the "Haryana claims checked" section of [news_and_reports.md](news_and_reports.md).

## ECOSTRESS

- About 620,000 scenes collected, averaging more than 230 per day. The team presented its Senior Review extension proposal in April 2026 and reported positive feedback. Source: ECOSTRESS April and May 2026 community digest on https://ecostress.jpl.nasa.gov (read in full).
- Version 3 higher-level products came out on 26 May 2026 (Earthdata alert, snippet only).
- The pixel is 69 by 38 m and the swath is 384 km. Source: https://ecostress.jpl.nasa.gov/mission.
- Operations past FY2026 are not confirmed. A report that ISS operations run to 2030 comes from a snippet only.

## GRACE-FO and GRACE-C

- GRACE-FO has operated since 2018 and is in the 2026 Senior Review.
- GRACE-C is a US-German mission (NASA/JPL with DLR and GFZ). Airbus builds the twin satellites, which are planned to launch in December 2028 on a Falcon 9 from Vandenberg. They will fly at 500 km, about 220 km apart, with a laser ranging interferometer, and give at least 5 years of data. Sources: https://grace.jpl.nasa.gov/mission/grace-c/ and JPL news of 19 Mar 2024.
- For Field Shift, GRACE-C means the groundwater record should continue past GRACE-FO, though a gap between the two is possible (not confirmed).

## Landsat

- The FY2026 request called the roughly $2 billion Landsat Next plan "gold-plated" and proposed restructuring it. Source: NASA FY2026 budget excerpt, May 2025.
- Congress funded Landsat Next at $110 million with a 2031 target. Source: SpacePolicyOnline, 5 Jan 2026.
- The NASA-USGS commercial strategy of 8 September 2026 plans one final government satellite, Landsat 10, with one LandIS instrument. By 2035 at the latest, all or most USGS Landsat products would use commercial data. Products under review for FY2027 include ET, crop residue, vegetation indices, and land cover. The plan says free distribution will be "explored", not guaranteed. Source: https://assets.science.nasa.gov/content/dam/science/esd/SLI_Commercial_Solutions_Strategy-9.8.26.pdf (read in full; exact path not confirmed, filename confirmed).
- USGS fully funds Landsat 8 and 9 operations in FY2026 (snippet only).

## MODIS and VIIRS

- A MODIS team slide gives Aqua's expected end of mission as September 2026, with a possible extension to fall 2027 if the Senior Review allows (snippet only).
- Terra's end date is not confirmed.
- VIIRS on Suomi NPP and the JPSS satellites is the named continuity sensor. Field Shift should plan to use VIIRS vegetation and LST products where MODIS ends.

## NASA Harvest and NASA Acres

- NASA Harvest's main NASA grant runs on a 5-year cycle. Source: https://www.nasaharvest.org/faqs.
- Harvest joined Google.org's AI collaborative on food security (15 Sep 2025) and a Gates-funded consortium led by Mathematica that is building a public AI decision tool, first for Ethiopia, Kenya, and Nigeria. That tool estimates how farm practices affect yield given weather and soil. Source: nasaharvest.org news, 7 Oct 2026 (read in full).
- NASA Acres, led by the University of Maryland since 2023, has more than 40 projects and more than 70 partners. USDA NIFA awarded it $936,310 for a farm data cooperative that shares data only by mutual consent. Source: University of Maryland Geographical Sciences news, 11 Nov 2026 (read in full).
- NASA Acres ran a listening tour of Texas, Oklahoma, and Kansas in September 2026. Source: https://www.nasaacres.org.
- We found no end of funding for either consortium (not confirmed).
- Relevance: the Harvest consortium tool is the closest public project to Field Shift's aims, but it targets practices and yield, not whole-rotation comparison.

## OpenET

- OpenET expanded to all 48 contiguous states on 16 December 2025, adding 25 eastern states. It launched with 17 western states in 2021 and reached 23 in 2023. It gives daily and monthly ET at 30 m and has more than 13,000 registered users. USGS uses it for national irrigation water-use estimates. Source: https://etdata.org/openet-expands-satellite-based-water-use-data-48-states/ (16 Dec 2025, read in full; exact slug not confirmed).
- This settles the open question in `research/INDEX.md`: the FAQ figure of 23 states is out of date.
- California water agencies used OpenET in SGMA planning in 2025, and a USDA-funded outreach program covers Kansas, Oklahoma, and Texas. Source: OpenET 2025 Annual Report, https://etdata.org/wp-content/uploads/2026/10/2025-OpenET-Annual-Report.pdf, Oct 2026.

## Copernicus (ESA)

- Sentinel-1C launched on 5 December 2024 and Sentinel-1D on 4 November 2025. Sentinel-1A ended in June 2026, and the two-satellite revisit is 6 days. Source: ESA Sentinel-1 facts and figures page (read in full).
- Sentinel-2C launched on 5 September 2024 and replaced Sentinel-2A on 25 January 2025. Source: ESA.
- CHIME, LSTM, CIMR, CRISTAL, and ROSE-L launch after 2028 according to CNES. Exact dates are not confirmed.

## What this means for Field Shift

- NISAR is a creative addition: radar sees crops and soil moisture through monsoon cloud, which matters for the Haryana demo in kharif. It should stay a stretch goal, since products below Level 2 validation are recent and SME2 is provisional.
- The pitch can say NASA data underpins state water policy: California reports GRACE data and uses OpenET, and Kansas pairs OpenET with soil probes.
- The tool should show data continuity risk honestly. SMAP has no follow-on, Aqua MODIS is near its end, and Landsat is moving to commercial data.
