# USDA NASS Quick Stats

## What it is

Quick Stats is the NASS online database of official published aggregate estimates on US agriculture. It draws on hundreds of NASS sample surveys each year and on the Census of Agriculture, which runs every five years and gives state and county aggregates. The Quick Stats API gives direct access to the same database.

## Content useful for rotations

The database is organized by "what", "where" and "when".

- Sectors: Crops, Animals and Products, Economics, Demographics, Environmental.
- Crop groups: Field Crops, Fruit and Tree Nuts, Horticulture, Vegetables.
- Statistic categories include AREA PLANTED, AREA HARVESTED, YIELD, PRODUCTION, PRICE RECEIVED, SALES, INVENTORY.
- Production practices include IRRIGATED and ORGANIC. Utilization practices include GRAIN and SILAGE.
- Domains break totals down by economic class, area operated, chemical type and similar.

Useful queries for a rotation tool include county yield and planted area for corn, soybeans, wheat, oats, barley, sorghum, alfalfa and other hay; state prices received; irrigated versus non-irrigated yields; and Census of Agriculture practice counts. Census items on cover crops and tillage exist in the Census of Agriculture, but their exact `short_desc` strings were not confirmed in this research.

## Spatial and temporal resolution

- Geographic levels (`agg_level_desc`): national, state, agricultural statistics district, county, region, ZIP code and watershed (HUC8), depending on the item.
- Time: annual, season, monthly, weekly or point in time (`freq_desc`). County survey data are usually annual. Census data are every five years.
- Coverage: United States. Years go back many decades for major crops; the start year varies by item and was not checked.

## Access methods

### Web

- Query builder: https://quickstats.nass.usda.gov
- Bulk tab-delimited files: https://www.nass.usda.gov/datasets/ (for pulls above the API limit)

### API

Three resources, each called with HTTP GET:

```
https://quickstats.nass.usda.gov/api/api_GET/?key=API_KEY&{parameters}&format={json|csv|xml}
https://quickstats.nass.usda.gov/api/get_param_values/?key=API_KEY&param={parameter}
https://quickstats.nass.usda.gov/api/get_counts/?key=API_KEY&{parameters}
```

Examples from the docs:

```
https://quickstats.nass.usda.gov/api/api_GET/?key=API_KEY&commodity_desc=CORN&year__GE=2012&state_alpha=VA&format=JSON
https://quickstats.nass.usda.gov/api/get_param_values/?key=API_KEY&param=sector_desc
https://quickstats.nass.usda.gov/api/get_counts/?key=API_KEY&commodity_desc=CORN&year__GE=2012&state_alpha=VA
```

A county yield query for a rotation tool would look like this (parameter names from the docs; values are illustrative):

```
https://quickstats.nass.usda.gov/api/api_GET/?key=API_KEY&source_desc=SURVEY&commodity_desc=SOYBEANS&statisticcat_desc=YIELD&agg_level_desc=COUNTY&state_alpha=IA&county_name=STORY&year__GE=2005&format=JSON
```

Operators appended to parameter names: `__LE`, `__LT`, `__GT`, `__GE`, `__LIKE`, `__NOT_LIKE`, `__NE`. JSONP works with a `callback` parameter.

Key output columns: `source_desc`, `sector_desc`, `group_desc`, `commodity_desc`, `class_desc`, `prodn_practice_desc`, `util_practice_desc`, `statisticcat_desc`, `unit_desc`, `short_desc` (concatenation of six columns), `domain_desc`, `domaincat_desc`, `agg_level_desc`, `state_ansi`, `state_alpha`, `county_ansi`, `county_name`, `asd_code`, `watershed_code`, `year`, `freq_desc`, `reference_period_desc`, `week_ending`, `load_time`, `Value`, and `CV %` (2012 Census only).

## Authentication and limits

- An API key is required. Users request it on the API page by agreeing to the NASS Terms of Service and giving a valid email address. NASS emails the key.
- A single request returns at most 50,000 records. Use `get_counts` first. If a query exceeds the limit, narrow the filters or use the bulk files.
- Error messages: "exceeds limit = 50000", "bad request - invalid query", "bad request - unsupport media type", "unauthorized".
- NASS reserves the right to limit calls and to block users who try to exceed or get around limits. A numeric rate limit was not stated.

## Terms of use

- Apps that use the API must display: "This product uses the NASS API but is not endorsed or certified by NASS."
- Users may not modify or misrepresent NASS content while still naming NASS as the source, and may not imply NASS endorsement.
- NASS can end access at its discretion.

## Limitations

- `Value` is a string with thousands separators and may hold suppression codes such as "(D)" (withheld to avoid disclosing individual operations). The tool must parse and handle these.
- County estimates are missing for many crop and county combinations, especially minor crops. NASS has reduced some county programs over time (general knowledge, not confirmed on the fetched page).
- Estimates are aggregates. They cannot show the yield of a specific field or a specific rotation.
- Forecasts and final estimates can both appear for the same year (`reference_period_desc`, for example "YEAR - MAR FORECAST"), so the tool must filter for final values.

## How it plugs into the rotation tool

- QuickStats calibrates yields. County yield histories for each candidate crop set realistic expected yields and year-to-year variability, which the tool can adjust with soil productivity (NCCPI) from SSURGO.
- Prices received give a long-run price baseline to set beside AMS cash prices.
- County planted area by crop shows which crops are common locally, a proxy for infrastructure and market access.
- Irrigated versus non-irrigated yields help compare dryland and irrigated rotation options.
- Census practice data (cover crops, tillage) show local adoption rates for the explanation text.

## Sources

- https://quickstats.nass.usda.gov
- https://quickstats.nass.usda.gov/api
- https://quickstats.nass.usda.gov/api#param_define
- https://www.nass.usda.gov/datasets/
