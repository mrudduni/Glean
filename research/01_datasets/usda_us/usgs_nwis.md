# USGS water data (NWIS, Water Data for the Nation, Water Data APIs)

## What it is

The USGS collects water data at more than one million monitoring locations, with records spanning more than 135 years. More than 13,500 locations report in real time (streams, lakes, reservoirs, precipitation, water quality and groundwater). The legacy system is called NWIS (National Water Information System) and its web pages NWISWeb. The modern public site is Water Data for the Nation (WDFN) at https://waterdata.usgs.gov, and the modern programmatic access is the USGS Water Data APIs at https://api.waterdata.usgs.gov.

Data categories are continuous data (sensor readings, often every 15 minutes), daily data (daily mean, min, max and other statistics), field measurements (manual measurements, including groundwater levels), and discrete sample data (water quality).

## Legacy deprecation timeline

This is the most important practical fact for a 2026-2027 build.

- USGS stated (29 January 2026) that legacy WaterServices at https://waterservices.usgs.gov will be decommissioned in the first quarter of 2027, and that intentional degradation would not start before August 2026.
- NWISWeb Decommission Campaign 3 runs from November 2026 through February 2027. It retires all remaining NWISWeb pages (/uv, /peaks, /ratings, /revisions, NWISMapper) and all WaterServices URLs. After February 2027 there will be no access to legacy NWISWeb pages.
- WaterServices will be throttled and will have planned outages before final shutdown.
- Code that calls waterservices.usgs.gov, the R `readNWIS()` family, or the Python `dataretrieval.nwis` module must move to the new APIs.

As of the research date (13 November 2026), the tool should not depend on any legacy endpoint.

## Water Data APIs

| API | Content |
| --- | --- |
| Continuous Values | Most recent real-time measurements of streamflow, gage height and hundreds of other parameters |
| Daily Values | Historical daily statistics for streams, lakes and wells |
| Monitoring Locations | Site name, id, agency, type (stream, lake, groundwater), state, county, coordinates, HUC |
| Time Series Metadata | Units, thresholds, first and last observation per time series |
| OGC-compliant APIs | Shared OGC API Features interface for the collections above plus field measurements |
| Samples API and Water Quality Portal | Discrete water quality data (USGS, EPA and more than 400 other agencies) |
| Water Data Statistics | Computed statistics on the historical record |
| Real-Time Flood Impacts, NIMS | Flood impact locations; gage camera imagery |

### OGC API examples from the official docs

```
https://api.waterdata.usgs.gov/ogcapi/v1/collections
https://api.waterdata.usgs.gov/ogcapi/v1/collections/daily/items?limit=2&api_key=DEMO_KEY
https://api.waterdata.usgs.gov/ogcapi/v1/collections/daily/items?limit=2&api_key=DEMO_KEY&datetime=2024-12-01/2024-12-31&statistic_id=00003&parameter_code=00065
```

- Responses are GeoJSON FeatureCollections with `numberMatched`, `numberReturned` and a `next` link for paging (`offset`, `limit`).
- Browsers get HTML by default. Add `f=json` for JSON.
- `datetime` accepts a single RFC 3339 time or an interval separated by `/`, with open ends allowed.
- Any property in the response (for example `monitoring_location_id`, `parameter_code`, `statistic_id`) can be used as a filter.
- Collection ids listed on the API home include `continuous`, `daily`, `monitoring-locations` and `time-series-metadata`. A `field-measurements` collection for groundwater levels is likely but was not confirmed on the fetched pages.

Common parameter codes: 00060 discharge, 00065 gage height. Statistic code 00003 is the daily mean. The groundwater level parameter code (72019, depth to water below land surface) is standard USGS usage but was not confirmed here.

### Python: dataretrieval

```
pip install dataretrieval
```

```python
from dataretrieval import waterdata

df, meta = waterdata.get_daily(
    monitoring_location_id="USGS-01646500",
    parameter_code="00060",            # discharge
    time="2024-10-01/2025-09-30",
)

sites, _ = waterdata.get_monitoring_locations(state="Iowa", site_type_code="ST")
```

The package also reads the Water Quality Portal, the National Ground-Water Monitoring Network (NGWMN) and the Network Linked Data Index (NLDI). The README advises splitting continuous-data requests into short time windows to avoid timeouts. A `parallel_chunks(n)` context speeds up large paginated pulls.

## Authentication and limits

- An API key is optional but strongly encouraged for higher rate limits. Sign up at https://api.waterdata.usgs.gov/signup/. The docs use `api_key=DEMO_KEY` in examples.
- In dataretrieval, supply the key with `dataretrieval.configure(...)`, the `API_USGS_PAT` environment variable, or `~/.dataretrieval/config.toml`.
- Exact rate limit numbers with and without a key were not found on the fetched pages (not confirmed).
- The server rejects URLs longer than about 8 KB (dataretrieval README).

## Formats

GeoJSON and JSON (also JSON-LD and HTML) from the OGC APIs. CSV download options exist at https://api.waterdata.usgs.gov/download (not examined).

## License and terms

USGS data are public domain as federal government works. A specific license statement was not on the fetched pages. Recent data carry an approval status such as "Provisional" or "Working" and can change.

## Limitations

- Gauges sit on rivers and in selected wells, not on farms. Nearest-site values describe the watershed or aquifer, not field conditions.
- Provisional data change after review.
- Groundwater well networks vary greatly in density and measurement frequency.
- The legacy shutdown means older tutorials and code samples will break.

## How it plugs into the rotation tool

- Groundwater level trends at wells near the farm show whether irrigation-dependent rotations (for example continuous irrigated corn) are sustainable. A falling water table is a risk the tool can report.
- Streamflow and low-flow statistics in the farm's watershed show water supply stress and support the risk section for irrigated options.
- Water quality samples (nitrate) from the Samples API or Water Quality Portal can back statements about nutrient loss risks of different rotations.
- Pair with OpenET evapotranspiration to compare crop water use with local water supply signals.

## Sources

- https://waterdata.usgs.gov/nwis
- https://waterdata.usgs.gov/data-collection-categories
- https://api.waterdata.usgs.gov/
- https://api.waterdata.usgs.gov/docs/ogcapi/
- https://api.waterdata.usgs.gov/signup/
- https://api.waterdata.usgs.gov/ogcapi/v1/openapi?f=html
- https://www.usgs.gov/tools/usgs-water-data-apis
- https://waterdata.usgs.gov/blog/nwisweb-decommission-campaign3/
- https://waterdata.usgs.gov/blog/wdfn-updates-2025/ (search snippet only)
- https://github.com/DOI-USGS/dataretrieval-python
- https://doi-usgs.github.io/dataretrieval-python/
- https://waterdata.usgs.gov/blog/wdfn-waterservices-2025/ (404)
