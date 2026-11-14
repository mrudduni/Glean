# ISRO and Indian space data access

Phase 2 research, gathered 2026-11-14. This file covers Indian satellite data and government farm products that could feed rotation decisions for an Indian field. For each, it gives resolution, access, login and licence. Facts we could not check carry the label "not confirmed". We downloaded no data.

## Quick table

| Product | Resolution | Revisit or cadence | Portal | Login | Licence or policy |
|---|---|---|---|---|---|
| NISAR L-band (NASA side) | Product dependent; SME2 soil moisture at 200 m | 12-day repeat | ASF (Earthdata) | Earthdata Login | NASA open data |
| NISAR S-band (ISRO side) | Product dependent | 12-day repeat, about 48 h latency | Bhoonidhi | Bhoonidhi registration | Indian Space Policy 2023 open tier (not confirmed for every product) |
| NISAR L4 soil moisture (ISRO) | 100 m | Two looks per 12 days | Bhoonidhi (planned) | Bhoonidhi registration | Not confirmed |
| EOS-04 soil moisture | 500 m | 17-day repeat | Bhoonidhi | Bhoonidhi registration | Open |
| EOS-04 SAR (CRS and MRS modes) | Mode dependent | Not confirmed | Bhoonidhi | Bhoonidhi registration | Open |
| Resourcesat-2/2A LISS-4 | 5.8 m | 5 days by steering; 2 to 3 days with both satellites | Bhoonidhi | Bhoonidhi registration | Open (5 m and coarser) |
| Resourcesat-2/2A LISS-3 | 23.5 m, includes SWIR | 24 days (not confirmed) | Bhoonidhi | Bhoonidhi registration | Open |
| Resourcesat-2/2A AWiFS | 56 m | About 5 days (not confirmed) | Bhoonidhi | Bhoonidhi registration | Open |
| Cartosat-1, 2S, 3 | Finer than 5 m | Not confirmed | Bhoonidhi, NSIL | Registration and payment | Priced for non-government users |
| MOSDAC soil wetness index | 0.125 degree (from 40 km SMAP) | 3-day composite | MOSDAC | MOSDAC single sign-on | Open |
| VEDAS NDVI time series | Sentinel-2 based, 10 m | Per scene | VEDAS vAPI | Not confirmed | Not confirmed |
| Krishi-DSS parcel crop maps | Parcel level | Seasonal, several years | krishi-dss.gov.in | Not confirmed | Not confirmed |
| NRSC LULC | 56 m (1:250k) | Annual since 2005-06 | Bhuvan, NRSC | Bhuvan login for download (not confirmed) | Not confirmed |

## Data policy

- The Indian Space Policy 2023 sets three tiers. Data at 5 m and coarser is free for everyone. Data finer than 5 m is free for government users and priced for others through NSIL. Derived thematic products are free. Source: https://www.isro.gov.in/media_isro/pdf/Bhoonidhi_NewsLetter_2024_Edition1.pdf
- The same newsletter lists open sensors (Resourcesat-1, 2, 2A, Oceansat, EOS-04 CRS and MRS modes, EOS-06) and priced ones (Cartosat-1, 2S, 3, and RISAT FRS modes). Free thematic products include NDVI, soil moisture and vegetation fraction.
- Conflict: the Bhoonidhi FAQ lists the EOS-04 FRS 3 m terrain-corrected product as free, while the newsletter lists FRS as priced. Check on Bhoonidhi before relying on it. Source: https://bhoonidhi.nrsc.gov.in
- Licence text for open Bhoonidhi data (attribution, redistribution) is not confirmed. The Space Apps project page must list every source and licence, so the team must read the Bhoonidhi terms before using any file.

## NISAR

NISAR is the NASA and ISRO radar mission. It launched on 30 July 2025, has a 12-day repeat and a swath of about 240 km.

### L-band through NASA ASF

Release timeline. Source: https://nisar-docs.asf.alaska.edu/availability-overview

| Date | Release |
|---|---|
| 23 January 2026 | Sample products |
| 27 February 2026 | BETA products: more than 100,000 products, over 500 TB |
| 20 July 2026 | PROVISIONAL products for acquisitions from 17 June 2026 |
| 6 November 2026 | VALIDATED L0 to L2 products for acquisitions from 21 October 2026 |
| 2027 | VALIDATED SME2 soil moisture, and reprocessing of the backlog |

Farm-relevant products. Sources: https://nisar-docs.asf.alaska.edu/products-overview, https://catalog.data.gov/dataset/nisar-provisional-soil-moisture-version-1

- GCOV (geocoded polarimetric covariance) supports crop area mapping.
- SME2 soil moisture at 200 m, produced with three algorithms (DSG, PMI and TSR). Stated latency is 72 hours, with about two maps every 12 days. It is PROVISIONAL now, so values need a caveat in the tool.
- Access needs a free Earthdata Login, the same as other NASA data in `../nasa/access_tooling.md`.

### S-band through Bhoonidhi

- Daily product releases started with Cycle 25 (8 July 2026). Products: RSLC, GSLC, GCOV, RIFG, RUNW, GUNW, ROFF and GOFF. Latency is about 48 hours. The processing baseline is v1.4.0, CRID P00500. Source: https://www.isro.gov.in/NISARS_Band_SAR_Data_Products_Release.html
- Bhoonidhi offers a tool that converts HDF5 to GeoTIFF or COG, and SARPOLTOOL as a QGIS plugin. API access is for authorised users. Source: https://bhoonidhi.nrsc.gov.in/NISAR/NisarProducts.html

### ISRO soil moisture from NISAR

- ISRO showed a 100 m L4 soil moisture product over India on 14 February 2026, made with a SAC algorithm. NRSC will produce it and serve it on Bhoonidhi with two looks every 12 days. Public release status is not confirmed. Source: https://www.isro.gov.in/NisarData_soil_moisture_products.html

## EOS-04 (RISAT-1A)

- C-band SAR. Launched 14 February 2022, orbit 529 km, 06:00 equator crossing. Source: https://space.oscar.wmo.int/satellites/view/eos_04
- Operational soil moisture product: 500 m, 17-day repeat, analysis-ready, open on Bhoonidhi. ISRO reports about 92% retrieval accuracy over croplands. Source: https://www.isro.gov.in/High-Resolution_Operational_Soil_Moisture_Product.html
- Bhoonidhi also lists an L2B terrain-normalised ARD product and an NRB CEOS-ARD mosaic of India in 1 degree tiles. Source: https://bhoonidhi.nrsc.gov.in
- Use for Field Shift: SAR sees through monsoon cloud, so it can fill kharif gaps when optical images are blank.

## Resourcesat-2 and 2A

- LISS-4: 5.8 m, red, green and NIR, 5-day revisit by steering.
- LISS-3: 23.5 m, adds a SWIR band.
- AWiFS: 56 m wide swath.
- Source: https://www.isro.gov.in/RESOURCESAT_2A.html
- With both satellites, the revisit drops to 2 to 3 days. Source: https://pubs.usgs.gov/publication/ofr20211030V/full
- Bhoonidhi offers a synthetic SWIR band for LISS-4. Source: https://bhoonidhi.nrsc.gov.in
- LISS-4 has no blue band, so true-colour views and some indices need care.

## Cartosat

- Cartosat-1, 2S and 3 data is finer than 5 m, so it is priced for non-government users through NSIL. Source: https://www.isro.gov.in/media_isro/pdf/Bhoonidhi_NewsLetter_2024_Edition1.pdf
- Field Shift should not depend on it.

## Bhoonidhi

- Portal: https://bhoonidhi.nrsc.gov.in
- Search and preview are open. Downloads need a free registration and login.
- An API exists, by request to bhoonidhi@nrsc.gov.in. Approval time is not confirmed, so a weekend build should not rely on it.

## MOSDAC

- Run by SAC. About 230 products and more than 12,000 registered users. Source: https://vedas.sac.gov.in/content/vcms/pdf/0_mosdac_vedas_newsletter_oct2025.pdf
- Soil wetness index from SMAP, resampled from 40 km to 0.125 degree, as a 3-day composite. It is open, but downloads need MOSDAC single sign-on. Source: https://mosdac.gov.in/soil-moisture-0
- A weather API offers 3-day forecasts at 3-hour steps and 5 km grid. Access terms are not confirmed. Source: the newsletter above.
- INSAT-3D, 3DR and 3DS products (rainfall, land surface temperature) are also on MOSDAC. Exact farm products and resolutions are not confirmed.

## VEDAS

- Run by SAC. Source for this section: https://vedas.sac.gov.in/content/vcms/pdf/0_mosdac_vedas_newsletter_oct2025.pdf
- Digital Drought Manual down to tehsil level, linked to NADAMS: https://vedas.sac.gov.in/krishi/dashboard/index.html
- GeoCrEST under FASAL 2.0: semi-physical yield estimates for 10 crops at district and state level.
- Sangrahi: offline app for collecting field data.
- KrishiDSS field-level analytics: https://vedas.sac.gov.in/vapps/krishi_dss/fla
- vAPI: a WMS API with AWiFS and Sentinel-2 composites, and a Temporal API that returns Sentinel-2 NDVI time series for a point or polygon. Whether it needs a key is not confirmed. Source: https://vedas.sac.gov.in/vconsole
- SAC ran a NISAR workshop for non-government users on 29 April 2025. Attendees showed interest in agriculture, insurance and soil moisture.

## Krishi-DSS

- National decision support system for agriculture, launched 16 August 2024 and run by MNCFC. Portal: https://krishi-dss.gov.in/
- Features: parcel-level crop maps across several years, which the launch release says help users understand crop rotation; drought monitoring; crop weather watch; field parcel segmentation; a "One nation-one soil information system"; and a ground truth and spectral library. Source: https://pib.gov.in/PressReleasePage.aspx?PRID=2045987
- Public download, API and licence are not confirmed. This is the most direct Indian source for a farmer's past rotation, so it is worth a live check.

## FASAL, CHAMAN and KISAN

- FASAL makes pre-harvest forecasts from satellite data. A 2021 release lists 9 crops: rice, wheat, tur, rabi pulses, mustard, rabi jowar, cotton, jute and sugarcane. A later release says 11 crops. Sources: https://pib.gov.in/PressReleasePage.aspx?PRID=1741940, https://pib.gov.in/PressReleasePage.aspx?PRID=2197707
- CHAMAN maps and assesses 7 horticulture crops: potato, onion, tomato, chilli, mango, banana and citrus. Source: https://pib.gov.in/PressReleasePage.aspx?PRID=1741940
- KISAN ran pilot studies on yield estimation that led to smart sampling of crop-cutting experiments under PMFBY. Source: https://pib.gov.in/PressReleasePage.aspx?PRID=1741940
- These outputs are reports at district or state level. They are not open field-level layers (not confirmed). The MNCFC site (ncfc.gov.in) blocked our fetch.

## YES-TECH and PMFBY

- YES-TECH (Yield Estimation System based on Technology) started in Kharif 2023 for paddy and wheat. Soybean was added in Kharif 2024. Technology yields carry at least 30% weight in final yield, and it runs in 10 states. Source: https://pib.gov.in/PressReleasePage.aspx?PRID=2085179
- Madhya Pradesh gives YES-TECH yields 100% weight. Source: https://downtoearth.org.in/agriculture/can-technology-make-indias-crop-insurance-payouts-more-accurate
- Manual: https://pmfby.gov.in/pdf/YES_TECH_Manual_2023.pdf (our fetch failed, so its contents are not confirmed).
- No public field-level YES-TECH data was found.

## NRSC land use and land cover

- Annual national LULC at 56 m (1:250k) since 2005-06. Layers include kharif crop, rabi crop, monthly crop layers, and double, triple and annual crop classes. Source: https://www.nrsc.gov.in/nrscnew/assets/pdf/atlas/LULC/LULC%20Atlas%20Final%20With%20Cover_March2024.pdf
- At 56 m, one pixel covers about 0.3 ha, which is larger than many Indian fields. Use it for context around a field, not for the field itself.
- Download path and licence are not confirmed.

## AgriStack and the Digital Crop Survey

- The Digital Agriculture Mission has a budget of 2,817 crore rupees and a target of 11 crore farmer IDs. Source: https://pib.gov.in/PressReleasePage.aspx?PRID=2051719
- The Digital Crop Survey covered 648 districts and more than 31.3 crore plots in Rabi 2025-26. Source: https://www.pib.gov.in/PressReleaseDetail.aspx?PRID=2296209 (the fetch returned little text, so the figures need a second check).
- Plot-level crop records exist, but they are personal data about farmers. They are not open, and Field Shift should not try to use them without a formal agreement.

## Recommended Indian data path for the hackathon

1. NISAR L-band GCOV or SME2 through ASF, because it counts as NASA data and needs only Earthdata Login.
2. EOS-04 soil moisture from Bhoonidhi as an ISRO cross-check for monsoon months.
3. VEDAS Temporal API for an NDVI time series of the field, if it works without a key.
4. Krishi-DSS parcel crop maps for past rotation, if public access works. Otherwise ask the farmer.

Steps 2 to 4 need live tests before any code depends on them.

## Sources

- https://www.isro.gov.in/media_isro/pdf/Bhoonidhi_NewsLetter_2024_Edition1.pdf
- https://bhoonidhi.nrsc.gov.in
- https://bhoonidhi.nrsc.gov.in/NISAR/NisarProducts.html
- https://nisar-docs.asf.alaska.edu/availability-overview
- https://nisar-docs.asf.alaska.edu/products-overview
- https://catalog.data.gov/dataset/nisar-provisional-soil-moisture-version-1
- https://www.isro.gov.in/NISARS_Band_SAR_Data_Products_Release.html
- https://www.isro.gov.in/NisarData_soil_moisture_products.html
- https://space.oscar.wmo.int/satellites/view/eos_04
- https://www.isro.gov.in/High-Resolution_Operational_Soil_Moisture_Product.html
- https://www.isro.gov.in/RESOURCESAT_2A.html
- https://pubs.usgs.gov/publication/ofr20211030V/full
- https://mosdac.gov.in/soil-moisture-0
- https://vedas.sac.gov.in/content/vcms/pdf/0_mosdac_vedas_newsletter_oct2025.pdf
- https://vedas.sac.gov.in/krishi/dashboard/index.html
- https://vedas.sac.gov.in/vapps/krishi_dss/fla
- https://vedas.sac.gov.in/vconsole
- https://krishi-dss.gov.in/
- https://pib.gov.in/PressReleasePage.aspx?PRID=2045987
- https://pib.gov.in/PressReleasePage.aspx?PRID=1741940
- https://pib.gov.in/PressReleasePage.aspx?PRID=2197707
- https://pib.gov.in/PressReleasePage.aspx?PRID=2085179
- https://downtoearth.org.in/agriculture/can-technology-make-indias-crop-insurance-payouts-more-accurate
- https://pmfby.gov.in/pdf/YES_TECH_Manual_2023.pdf
- https://www.nrsc.gov.in/nrscnew/assets/pdf/atlas/LULC/LULC%20Atlas%20Final%20With%20Cover_March2024.pdf
- https://pib.gov.in/PressReleasePage.aspx?PRID=2051719
- https://www.pib.gov.in/PressReleaseDetail.aspx?PRID=2296209
