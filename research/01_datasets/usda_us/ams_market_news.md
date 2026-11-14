# USDA AMS Market News and the MyMarketNews (MARS) API

## What it is

USDA Agricultural Marketing Service (AMS) Market News has published free price and sales information on farm commodities for 100 years. It issues thousands of reports each year with wholesale, retail and shipping data. Commodity groups are cotton and tobacco; dairy; fruits, vegetables and specialty crops; livestock, meats, poultry, eggs, grain and hay; organic; and local and regional foods.

MyMarketNews (MMN, https://mymarketnews.ams.usda.gov) is the portal. Its API is called the MARS API (Market Analysis and Reporting Services).

## Report types relevant to rotations

| Area | Examples found | Content |
| --- | --- | --- |
| Hay and forage | State "Direct Hay" reports, for example Arizona Direct Hay Report (slug 3784, AMS_3784) and Tennessee Direct Hay Report (slug 3793) | Weekly or biweekly trades, asks and offers for hay, straw and silage by quality grade |
| Grain | Public data list includes National Weekly Grain Co-Products Report and National Weekly Non-GMO/GE Grain Report; state and terminal grain bids exist | Cash bids, basis, co-product prices |
| Specialty crops | Fruit and vegetable terminal market, shipping point and movement reports | Prices and volumes by commodity, origin and package |
| Organic, local and regional | Organic grain and feedstuffs, local food reports | Price premiums |

The list above is partial. The FAQ notes that data are still being moved into MARS one commodity at a time, so some reports may only exist as PDF or text. Exact slugs for national grain and hay summaries were not confirmed.

## Spatial and temporal resolution

Reports are tied to a market location (a terminal market, auction, state or region) and published daily, weekly, biweekly or monthly depending on the report. Report history length varies by report and was not checked.

## Access methods

### Web

- Report search and public data: https://mymarketnews.ams.usda.gov/public_data
- Individual report pages: `https://mymarketnews.ams.usda.gov/viewReport/<slug_id>`
- File repository of published reports: https://mymarketnews.ams.usda.gov/filerepo/reports

### MARS API

Base endpoint: `https://marsapi.ams.usda.gov/services/v1.2/reports`. The examples page also shows `v3.0` URLs, and the change history page was not read, so the current preferred version is not confirmed.

Examples from the official docs (the API key goes in as the basic-auth user name with an empty password):

```
curl https://marsapi.ams.usda.gov/services/v1.2/reports -u api_key:                 # table of contents
curl https://marsapi.ams.usda.gov/services/v1.2/reports/1095 -u api_key:            # one report by slug id
curl https://marsapi.ams.usda.gov/services/v1.2/reports/MD_DA953 -u api_key:        # by slug name
curl "https://marsapi.ams.usda.gov/services/v1.2/reports/3148?q=report_begin_date=03/11/2024&allSections=true" -u api_key:
curl "https://marsapi.ams.usda.gov/services/v1.2/reports/1975/Volumes?q=report_begin_date=05/29/2019" -u api_key:
curl "https://marsapi.ams.usda.gov/services/v1.2/reports/1280?q=commodity=Feeder%20Cattle;report_begin_date=01/28/2019:02/01/2019" -u api_key:
curl "https://marsapi.ams.usda.gov/services/v1.2/reports/1089/Details?lastDays=50" -u api_key:
curl https://marsapi.ams.usda.gov/services/v1.2/commodities -u api_key:
curl https://marsapi.ams.usda.gov/services/v1.2/offices -u api_key:
curl https://marsapi.ams.usda.gov/services/v1.2/marketTypes -u api_key:
```

Python pattern:

```python
import requests
r = requests.get("https://marsapi.ams.usda.gov/services/v1.2/reports/3784",
                 params={"q": "report_begin_date=01/01/2025:06/30/2025"},
                 auth=(API_KEY, ""), timeout=60)
```

Rules from the docs:

- Every report has a unique `slug_id` and `slug_name`. Calls target a report, not a commodity. Users cannot search one commodity across all reports, though they can filter by commodity inside a report.
- Filters go in the `q` parameter, joined with semicolons. Date ranges use `start:end` in mm/dd/yyyy.
- Parameters are case sensitive (`correctionsOnly=true` works, `correctionsonly=true` is ignored).
- HTTPS only. The API does not support open web browser calls.
- Corrections can be pulled with `correctionsOnly=true` and `anyChangesSince=yyyy/mm/dd`.
- No webhooks.

## Authentication and limits

- An API key is required in practice. Users get it by logging in to MyMarketNews with USDA eAuthentication (register if needed; confirmation email within a few hours), then clicking their name and "Show API key".
- The FAQ says a sample key exists for unregistered use but will be removed in the future.
- Unregistered users get at most 5,000 rows per request. Registered users get up to 100,000 rows per request.
- AMS says it does not limit the number of queries per time period.
- Keys are personal and must not be shared, so a public app should keep the key on a server.

## License and terms

Market News data are free public USDA information. A formal license statement was not on the fetched pages.

## Limitations

- Report-centric design means the tool needs a lookup table from crop and region to report slugs.
- Coverage is uneven. Major grains and hay have regular reports, but minor and specialty crops may have only distant terminal markets.
- Prices are cash market observations at report locations, not farm-gate prices, and do not include costs.
- Migration of older data into MARS was described as ongoing.

## How it plugs into the rotation tool

- AMS gives market viability. For each crop in a candidate rotation, the tool pulls recent cash prices or hay prices from the nearest reporting market and shows price level and volatility.
- Hay reports by quality grade let the tool value an alfalfa or grass hay phase, which QuickStats only reports as state averages.
- Organic and non-GMO reports let the tool show premium options for diversified rotations.
- If no nearby market reports a crop, the tool should flag weak market access as a risk.

## Sources

- https://www.ams.usda.gov/market-news
- https://mymarketnews.ams.usda.gov/mymarketnews-api
- https://mymarketnews.ams.usda.gov/mymarketnews-api/authentication
- https://mymarketnews.ams.usda.gov/mymarketnews-api/reports
- https://mymarketnews.ams.usda.gov/mymarketnews-api/examples
- https://mymarketnews.ams.usda.gov/mymarketnews-api/faqs
- https://mymarketnews.ams.usda.gov/public_data
- https://mymarketnews.ams.usda.gov/viewReport/3784
- https://mymarketnews.ams.usda.gov/viewReport/3793
- https://mpr.datamart.ams.usda.gov/LMPRS-API-User-Guide.pdf (not fetched)
