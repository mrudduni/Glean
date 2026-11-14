# Agmarknet mandi prices through data.gov.in

Agmarknet records daily arrivals and prices at Indian agricultural markets (mandis). It is the best open source for the prices a Haryana farmer actually gets, outside the crops bought at MSP.

## Key facts

| Item | Value |
|---|---|
| What | Daily minimum, maximum and modal price in rupees per quintal, by state, district, market, commodity and variety |
| API | Open Government Data (OGD) platform, resource `9ef84268-d588-465a-a308-a864a43d0070` ("Current Daily Price of Various Commodities from Various Markets (Mandi)") at `https://api.data.gov.in/resource/{id}` |
| Auth | An API key from a free data.gov.in account. Without a key the API returns HTTP 400 "Authorization field missing". |
| Coverage | This resource holds current prices only. History comes from the Agmarknet portal reports at https://agmarknet.gov.in |
| Licence | Government Open Data License - India (GODL), the default for data.gov.in. Not checked on the resource page. |

data.gov.in shows a public sample key in its docs that returns only a few rows. We do not use it, and the real key goes in the git-ignored `.env` as `DATA_GOV_IN_API_KEY`.

Sources: probe output and https://mandi-api.vercel.app/blog/agmarknet-2-api (third-party summary of Agmarknet 2.0).

## Role in the tool

- Price inputs for maize, mustard, and pulses, the crops without an assured MSP purchase in Haryana. Rice and wheat use MSP from CACP and PIB notices.
- The spread of modal prices over past seasons gives the price risk band for each strategy. That is the market risk every Karnal study names as the main barrier to maize.

## Gaps

- We need a free key to probe the API. The team should create one and store it in `.env`.
- We need a route to historical prices. Agmarknet 2.0 report pages may need scraping, which needs a check of their terms first.

## Sources

- https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
- https://agmarknet.gov.in
- Probe output: `research/04_data_probes/samples/global_probe_results.json`, key `india`, entry `data_gov_in_no_key`
