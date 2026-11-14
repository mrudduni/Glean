# Frontend stack

This file compares frontend frameworks, map libraries, charting, field drawing, basemaps, internationalisation, offline support, and accessibility for Field Shift. Versions, dates, and licences come from the npm registry (`https://registry.npmjs.org/<name>`) on 14 November 2026 unless a row says otherwise.

## Summary

| Layer | Recommendation |
| --- | --- |
| Framework | React with Vite and TypeScript, as a static single-page app |
| Map | MapLibre GL JS, with deck.gl only if we need large overlays |
| Charts | Observable Plot for time series and small multiples; Vega-Lite as an option for declarative specs the backend can emit |
| Field drawing | Terra Draw with its MapLibre adapter |
| Basemap | OpenFreeMap vector tiles, a self-hosted Protomaps PMTiles extract for offline, and NASA GIBS for imagery |
| i18n | i18next with react-i18next |
| Offline | vite-plugin-pwa (Workbox) |

## Framework: React and Vite vs Next.js vs SvelteKit

| Package | Version (date) | Licence | Source |
| --- | --- | --- | --- |
| react | 19.3.1 (2026-10-14) | MIT | https://registry.npmjs.org/react |
| vite | 8.3.8 (2026-11-11) | MIT | https://registry.npmjs.org/vite |
| next | 16.4.6 (2026-11-09) | MIT | https://registry.npmjs.org/next |
| @sveltejs/kit | 3.2.0 (2026-11-10) | MIT | https://registry.npmjs.org/@sveltejs/kit |
| svelte | 5.57.3 (2026-10-26) | MIT | https://registry.npmjs.org/svelte |
| typescript | 7.0.2 (2026-07-08) | Apache-2.0 | https://registry.npmjs.org/typescript |
| @tanstack/react-query | 5.107.1 (2026-11-06) | MIT | https://registry.npmjs.org/@tanstack/react-query |
| zustand | 5.1.0 (2026-11-06) | MIT | https://registry.npmjs.org/zustand |

- React with Vite builds a static bundle that any static host serves (GitHub Pages, Cloudflare Pages, Netlify). It has the largest set of map and chart wrappers (`react-map-gl` 8.1.3 and `@vis.gl/react-maplibre` 8.1.3, both MIT). Recruiters and reviewers know it. Server-side rendering adds little for a map-heavy tool.
- Next.js adds server rendering and API routes. Those are useful for a content site but push us toward Vercel and a Node backend, while our science code is Python. The Vercel Hobby plan limits functions to 300 seconds and 2 GB (https://vercel.com/docs/limits).
- SvelteKit produces smaller bundles and simpler state code. Its map and chart ecosystem is smaller, and fewer contributors know it.

Recommendation: React, Vite, and TypeScript, built as a static app that calls the FastAPI backend. Use TanStack Query for fetching and caching API calls, and Zustand for shared UI state (selected strategy, weights, language).

TypeScript 7.0 is the Go-based compiler rewrite (version from npm; the rewrite claim is not confirmed in this session). If a tool in the chain does not support 7.0 yet, pin TypeScript 5.x.

## Map libraries

| Library | Version (date) | Licence | Notes | Source |
| --- | --- | --- | --- | --- |
| maplibre-gl | 6.18.0 (2026-11-11) | BSD-3-Clause | WebGL vector maps, open fork of Mapbox GL v1 | https://registry.npmjs.org/maplibre-gl |
| deck.gl | 9.4.1 (2026-10-28) | MIT | GPU layers for large data, works as a MapLibre overlay | https://registry.npmjs.org/deck.gl |
| leaflet | 1.9.4 (2023-05-18) | BSD-2-Clause | Simple raster-tile maps, no new release since 2023 | https://registry.npmjs.org/leaflet |
| ol (OpenLayers) | 10.11.0 (2026-10-04) | BSD-2-Clause | Full GIS client, strong projection and COG support | https://registry.npmjs.org/ol |

- MapLibre renders vector basemaps, raster XYZ layers (GIBS, our tiles), and GeoJSON fields. It handles 3D terrain if we want to show slope.
- deck.gl helps if we draw thousands of CSB polygons or a hex grid of suitability. Not needed for one farm.
- Leaflet is the easiest to learn, but it has no vector-tile rendering built in, and the 2.0 line was not on npm `latest` on 14 November 2026.
- OpenLayers can read COGs in the browser directly (`ol/source/GeoTIFF`), which avoids a tile server. It is heavier to learn.

Recommendation: MapLibre GL JS. Keep OpenLayers in mind if we need in-browser COG reading without a server.

## Charting

| Library | Version (date) | Licence | Source |
| --- | --- | --- | --- |
| @observablehq/plot | 0.6.19 (2026-11-05) | ISC | https://registry.npmjs.org/@observablehq/plot |
| vega-lite | 6.5.0 (2026-10-08) | BSD-3-Clause | https://registry.npmjs.org/vega-lite |
| vega-embed | 7.3.0 (2026-09-23) | BSD-3-Clause | https://registry.npmjs.org/vega-embed |
| echarts | 6.1.0 (2026-05-19) | Apache-2.0 | https://registry.npmjs.org/echarts |
| recharts | 3.10.1 (2026-07-25) | MIT | https://registry.npmjs.org/recharts |

- Observable Plot writes compact code for time series, ranges, and faceted small multiples (one panel per strategy). It renders SVG, which screen readers and print handle well. It is still 0.x.
- Vega-Lite uses JSON specs. The Python backend can emit a spec through Altair, so a notebook and the web app share one chart definition. It adds a larger bundle.
- ECharts has many chart types, canvas rendering, and built-in ARIA descriptions (not confirmed for every chart type). Good for dense dashboards.
- Recharts is React-native and simple, but less flexible for scientific plots.

Recommendation: Observable Plot for strategy comparison charts and weather or NDVI time series. Use Vega-Lite only if we want shared specs with notebooks.

## Field boundary drawing

| Library | Version (date) | Licence | Source |
| --- | --- | --- | --- |
| terra-draw | 1.39.0 (2026-10-28) | MIT | https://registry.npmjs.org/terra-draw |
| terra-draw-maplibre-gl-adapter | 1.5.0 (2026-10-06) | MIT | https://registry.npmjs.org/terra-draw-maplibre-gl-adapter |
| @watergis/maplibre-gl-terradraw | 1.17.0 (2026-10-04) | MIT | https://registry.npmjs.org/@watergis/maplibre-gl-terradraw |
| @mapbox/mapbox-gl-draw | 1.5.2 (2026-09-14) | ISC | https://registry.npmjs.org/@mapbox/mapbox-gl-draw |
| maplibre-gl-draw | 1.6.9 (2023-07-21) | ISC | https://registry.npmjs.org/maplibre-gl-draw |
| @turf/turf | 7.4.0 (2026-08-03) | MIT | https://registry.npmjs.org/@turf/turf |

Terra Draw works across MapLibre, Leaflet, OpenLayers, and Google Maps through adapters, and supports polygon, freehand, select, and edit modes. `@watergis/maplibre-gl-terradraw` wraps it as a ready MapLibre control. The `maplibre-gl-draw` fork has not released since 2023. Mapbox GL Draw works with MapLibre in practice but targets Mapbox (compatibility not confirmed for MapLibre 6).

Recommendation: Terra Draw through the watergis control. Use Turf for area, centroid, and self-intersection checks before sending a polygon to the backend. Let the user pick a CSB or FTW polygon by clicking, and fall back to drawing.

## Basemaps

| Basemap | Cost and limits | Licence and attribution | Source |
| --- | --- | --- | --- |
| OpenFreeMap (vector) | Public instance free, "no limits on the number of map views or requests", no API key, commercial use allowed | MIT code; OSM data; attribution "OpenFreeMap © OpenMapTiles Data from OpenStreetMap" required | https://openfreemap.org/ |
| Protomaps basemap (PMTiles) | Self-host one file on any static host or object store; daily builds | "Open Database License Produced Work (OpenStreetMap attribution required)" | https://docs.protomaps.com/basemaps/downloads |
| NASA GIBS imagery | Free, no login, WMTS and XYZ, daily MODIS and VIIRS true colour | NASA asks for an acknowledgement line | `research/01_datasets/nasa/access_tooling.md` |
| Esri World Imagery | Needs an ArcGIS Location Platform or ArcGIS Online account for the basemap styles service; "Powered by Esri" attribution required | Proprietary terms | https://developers.arcgis.com/rest/basemap-styles/ and https://location.arcgis.com/help/licensing-and-attribution |

Offline downloads from OpenFreeMap are allowed if each download is "at most 3,000 tiles or 50 MB", uses at most 4 parallel requests, and sends a unique User-Agent (https://openfreemap.org/). The `pmtiles` npm package is 4.5.0 (2026-08-10, BSD-3-Clause, https://registry.npmjs.org/pmtiles) and `@protomaps/basemaps` is 5.7.2 (BSD-3-Clause, https://registry.npmjs.org/@protomaps/basemaps).

Esri imagery is the sharpest free-looking satellite basemap, but its terms need an account and key, and older forum answers say free use requires no revenue (https://gis.stackexchange.com/questions/320798/, not an official source, not confirmed for 2026). That conflicts with an open, keyless project. Use GIBS for true-colour context and our own HLS or Sentinel-2 composites for field-scale imagery. HLS at 30 m is coarse but honest, and it is NASA data, which helps the Relevance score.

## Internationalisation

| Library | Version (date) | Licence | Source |
| --- | --- | --- | --- |
| i18next | 27.1.1 (2026-11-10) | MIT | https://registry.npmjs.org/i18next |
| react-i18next | 18.0.1 (2026-11-08) | MIT | https://registry.npmjs.org/react-i18next |
| react-intl (FormatJS) | 12.1.7 (2026-11-08) | BSD-3-Clause | https://registry.npmjs.org/react-intl |
| @lingui/core | 6.12.0 (2026-11-03) | MIT | https://registry.npmjs.org/@lingui/core |
| @inlang/paraglide-js | 3.2.2 (2026-11-10) | MIT | https://registry.npmjs.org/@inlang/paraglide-js |

Note: the npm package named `paraglide-js` (without the `@inlang` scope) is a 0.0.1 security placeholder. Use only `@inlang/paraglide-js`.

- i18next has the largest ecosystem, lazy-loads language files, and handles plurals through the browser `Intl` API. Hindi plural rules and Devanagari text work through standard `Intl` (not tested).
- react-intl uses ICU message format, which suits translators who know it.
- Paraglide compiles messages to tree-shakable functions, giving small bundles. It is younger.

Recommendation: i18next with react-i18next. Store English as the source and add Spanish and Hindi first. Use `Intl.NumberFormat` and `Intl.DateTimeFormat` for units and dates. The LLM layer can draft translations, but a fluent speaker must review farmer-facing text, and the challenge requires English in the submission itself (`research/02_hackathon/rules_judging.md`).

## Offline and PWA

vite-plugin-pwa 2.0.0 (2026-10-03, MIT, https://registry.npmjs.org/vite-plugin-pwa) generates a service worker with Workbox (`workbox-window` 7.4.1, MIT, https://registry.npmjs.org/workbox-window). A PWA can cache the app shell, the last farm report as JSON, and a small PMTiles extract around the farm. This suits farmers with weak signal who open the report in the field. Live data still needs a connection.

## Accessibility for maps and charts

- WCAG 2.2 asks for text contrast of at least 4.5:1 and non-text contrast (chart lines, map symbols, focus rings) of at least 3:1 (https://www.w3.org/TR/WCAG22/).
- Never use colour alone for meaning. Pair colour with labels, patterns, or icons, for example a hatch pattern for "data missing".
- Use colour-blind-safe palettes. Okabe-Ito for categories such as strategies (https://jfly.uni-koeln.de/color/), and viridis or ColorBrewer sequential and diverging schemes for maps (https://colorbrewer2.org/). Observable Plot includes viridis and ColorBrewer schemes (not confirmed for every scheme name).
- Give every chart a text summary and a data table toggle. Give the map a list view of fields and layers, so keyboard and screen-reader users can choose a field without the canvas.
- MapLibre canvases are not readable by screen readers, so the key numbers must also appear as text outside the map.

## Python-only alternatives

| Framework | Version (date) | Licence | Source |
| --- | --- | --- | --- |
| Streamlit | 1.67.0 (2026-11-05) | Apache-2.0 | https://pypi.org/pypi/streamlit/json |
| Panel (HoloViz) | 1.10.0 (2026-10-23) | BSD | https://pypi.org/pypi/panel/json |
| Dash (Plotly) | 4.5.0 (2026-10-29) | MIT | https://pypi.org/pypi/dash/json |
| Solara | 1.66.3 (2026-11-10) | MIT | https://pypi.org/pypi/solara/json |
| Shiny for Python | 1.9.0 (2026-10-29) | MIT | https://pypi.org/pypi/shiny/json |
| Gradio | 6.32.0 (2026-11-12) | Apache-2.0 | https://pypi.org/pypi/gradio/json |
| leafmap | 0.64.7 (2026-11-12) | MIT | https://pypi.org/pypi/leafmap/json |
| maplibre (Python) | 0.3.6 (2025-12-13) | MIT | https://pypi.org/pypi/maplibre/json |
| lonboard | 0.17.0 (2026-10-01) | MIT | https://pypi.org/pypi/lonboard/json |

How they compare for this project:

- Streamlit is the fastest path from a notebook to a page. It reruns the whole script on each interaction, so caching (`st.cache_data`) matters. leafmap and `streamlit-folium` give maps, but drawing a field and reacting to clicks is clumsy.
- Shiny for Python uses reactive updates, so only the affected outputs rerun. It suits a form-plus-results layout well.
- Solara is React-like and component-based, and runs in Jupyter and as a web app. It scales to larger apps better than Streamlit.
- Panel has the strongest support for xarray and HoloViews plots, which fits raster time series.
- Dash suits Plotly-heavy dashboards and has a mature callback model.
- Gradio is built for model demos. Free Hugging Face hosting for Gradio now needs a paid plan, except up to 2 ZeroGPU Spaces on free personal accounts (https://huggingface.co/docs/hub/spaces-overview).

When Python-only is good enough:

- For the 30-second video, yes. The video can be recorded on a laptop, so hosting, cold starts, and polish of interaction matter little. A Streamlit or Solara page with a map, three strategy cards, and one chart can carry the demo.
- For the long-term portfolio app, no. Custom field drawing, offline use, multilingual text, accessibility control, and mobile layout all fight these frameworks. They also tie the UI to a Python server process per user session.

Recommendation: if the team has no React developer during the hackathon, build the demo in Solara or Streamlit on top of the same `fieldshift_core` package, then build the React app after the event. If the team has one React developer, go straight to React and keep a notebook for analysis.

## Sources

- npm registry metadata, queried 14 November 2026: https://registry.npmjs.org/{package}
- Vercel limits: https://vercel.com/docs/limits
- OpenFreeMap: https://openfreemap.org/
- Protomaps downloads: https://docs.protomaps.com/basemaps/downloads
- Esri basemap styles: https://developers.arcgis.com/rest/basemap-styles/
- Esri licensing and attribution: https://location.arcgis.com/help/licensing-and-attribution
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Okabe-Ito palette: https://jfly.uni-koeln.de/color/
- ColorBrewer: https://colorbrewer2.org/
