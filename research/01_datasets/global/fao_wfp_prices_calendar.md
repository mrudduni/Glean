# FAOSTAT prices, WFP food prices, and the FAO crop calendar

These three sources give the economic and calendar context the rotation comparison needs outside the US.

## FAOSTAT producer prices

| Item | Value |
|---|---|
| What | Annual producer prices by country and crop, in local currency and in USD per tonne |
| Record | 1991 onward. The bulk file had year columns up to Y2025. |
| API | `https://faostatservices.fao.org/api/v1/en/data/PP` returns HTTP 401 "Missing Authorization Header" without a token |
| Bulk download | `https://bulks-faostat.fao.org/production/Prices_E_Asia.zip` (2.6 MB) works with no login |
| Licence | CC BY 4.0 (FAO open data policy) |

India rows exist for chickpea, maize, rapeseed, rice, wheat and other crops. Many recent cells for India were empty in the sample. FAOSTAT gives one national price per year, which is too coarse for a field decision. Use it only as a fallback.

Sample: `research/04_data_probes/samples/faostat_producer_prices_india.csv`

## WFP food prices (through HDX)

| Item | Value |
|---|---|
| What | Market prices by market, commodity and date, retail and wholesale |
| India record | 1994 onward, last updated 2026-11-05 |
| Access | HDX CKAN API, `package_show?id=wfp-food-prices-for-india`, then the CSV (`wfp_food_prices_ind.csv`, about 26 MB) |
| Auth | None |
| Licence | CC BY-IGO |

The India file covers mainly retail prices of food (rice, wheat, mustard oil, sugar) in large cities. It does not cover farm-gate prices in Haryana mandis. Agmarknet is the right source for those (see `../india/agmarknet.md`).

Sample: `research/04_data_probes/samples/wfp_prices_india_head.csv`

## FAO crop calendar API

| Item | Value |
|---|---|
| Endpoint | `https://api-cropcalendar.apps.fao.org/api/v1/countries/{code}/cropCalendar` |
| Coverage | 58 countries, mostly in Africa, Asia and Latin America |
| India | Returns HTTP 204 with no content. India is not covered. |
| Kenya | 290 entries for 31 crops |
| Auth | None |

For India we need sowing and harvest windows from another source, such as ICAR crop calendars or state agriculture department advisories.

Sample: `research/04_data_probes/samples/fao_crop_calendar_kenya_first3.json`

## Sources

- https://www.fao.org/faostat/en/#data/PP
- https://data.humdata.org/dataset/wfp-food-prices-for-india
- https://api-cropcalendar.apps.fao.org/
- Probe output: `research/04_data_probes/samples/global_probe_results.json`, keys `faostat`, `wfp_hdx`, `crop_calendar`
