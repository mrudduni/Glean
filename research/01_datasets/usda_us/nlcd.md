# National Land Cover Database (NLCD) and Annual NLCD

## What it is

NLCD is the USGS land cover database for the United States, produced at the EROS Center with the Multi-Resolution Land Characteristics (MRLC) Consortium of federal agencies. It is derived from Landsat imagery. There are two generations.

- Legacy NLCD covers nine epochs from 2001 to 2021 (2001, 2004, 2006, 2008, 2011, 2013, 2016, 2019 and 2021) for CONUS. USGS no longer produces it and asks users to move to Annual NLCD. The USGS EROS NLCD page now describes only the legacy product.
- Annual NLCD uses chained deep learning models and harmonic time series analysis to produce one map per year. USGS first released it in 2024.

## Annual NLCD products

| Code | Product | Content |
| --- | --- | --- |
| LndCov | Land Cover | Dominant thematic class for the year |
| LndChg | Land Cover Change | Change from the previous year, recorded in the later year |
| LndCnf | Land Cover Confidence | Classifier probability for the mapped class |
| FctImp | Fractional Impervious Surface | Percent of the pixel covered by artificial surfaces |
| ImpDsc | Impervious Descriptor | Roads versus urban non-road |
| SpcChg | Spectral Change Day of Year | Day of year when Landsat reflectance changed significantly |

MRLC also lists summary products (Land Cover Change Index, Land Cover Change Count) and related products such as RCMAP rangeland cover and Exotic Annual Grass maps.

## Classes

Land cover follows a modified Anderson Level II system. The legacy CONUS legend has 16 classes. The standard codes (from the NLCD legend, not reprinted on the fetched pages) are 11 open water, 12 perennial ice and snow, 21 to 24 developed (open space to high intensity), 31 barren, 41 to 43 deciduous, evergreen and mixed forest, 52 shrub/scrub, 71 grassland/herbaceous, 81 pasture/hay, 82 cultivated crops, 90 woody wetlands and 95 emergent herbaceous wetlands.

## Spatial and temporal resolution

- 30 m raster.
- Annual from 1985.
- Annual NLCD Collection 1.1 covers CONUS for 1985 to 2024 (data.gov record, modified 30 June 2026). The MRLC FAQ mentions downloads spanning "1985-2025" in one answer and "1985 to 2024" in another, so availability of a 2025 map is not confirmed.
- MRLC states that updates come once a year in late spring or summer.

## Coverage

Annual NLCD covers CONUS only. Legacy NLCD exists for Hawaii (latest 2001), Alaska (latest 2016) and Puerto Rico (latest 2001). USGS is building Annual NLCD for Hawaii and Alaska.

## Formats and projection

GeoTIFF. Albers equal area projection on the WGS84 datum (chosen to match Landsat Analysis Ready Data without resampling). Note that the CDL uses NAD83 Albers (EPSG:5070), so the two grids may need alignment checks. No CSV or shapefile downloads.

## Access methods

- MRLC Direct Download Site: four pre-bundled CONUS zip files for the full series.
- MRLC NLCD Viewer: draw or upload an AOI (single-part shapefile or GeoJSON), pick layers and years, and receive a clipped GeoTIFF by email within a few hours. It also plots county zonal histograms.
- MRLC NLCD EVA Tool: county-level charts and statistics.
- OGC services: WMS for all six Annual NLCD products, WMS and WCS for summary products (listed on https://www.mrlc.gov/data-services-page).
- AWS S3 in us-west-2 for programmatic access (bucket name not given on the fetched pages).
- ScienceBase: per-product items with yearly zips, for example the Collection 1.1 Fractional Impervious Surface item (6810c151d4be022940554070).
- USGS EarthExplorer: "Land Cover" category, as Landsat ARD tiles.
- Esri Living Atlas hosts a "USA Annual NLCD - Land Cover" layer for 1985 to 2024.

Example data release DOI for citation: https://doi.org/10.5066/P94UXNTS

## Authentication

None for MRLC downloads, WMS/WCS or ScienceBase. The viewer asks for an email address to deliver clips. EarthExplorer downloads use a free USGS login (general EarthExplorer rule, not confirmed on the NLCD pages).

## License and terms

USGS products are public domain (USGS media on the NLCD page is marked "Public Domain"). MRLC asks users to cite: U.S. Geological Survey, 2024, Annual NLCD Collection 1 Science Products, data release, https://doi.org/10.5066/P94UXNTS.

## Accuracy

Validation for Annual NLCD Collection 1.0 was released in July 2025. USGS has published thematic accuracy assessments for legacy NLCD 2019 and 2021. Accuracy figures were not extracted in this research.

## Limitations

- Legacy and Annual NLCD are not comparable. Differences between them can reflect method changes, not real change. Compare only within one release.
- The "cultivated crops" class (82) lumps all crops, so NLCD cannot show rotations. The CDL is needed for crop types.
- 30 m pixels blur narrow features such as field edges and buffers.

## How it plugs into the rotation tool

- NLCD gives the land cover context around the farm, for example the share of cropland, pasture, forest and wetland in the watershed. The tool can use this when it explains environmental risks of a rotation, such as nutrient runoff into nearby wetlands.
- Annual land cover from 1985 shows long-term conversion between pasture/hay (81) and cultivated crops (82), which helps explain whether perennial forage in a rotation fits local history.
- The Land Cover Confidence layer gives a per-pixel uncertainty flag for the data gaps section.

## Sources

- https://www.usgs.gov/centers/eros/science/national-land-cover-database
- https://www.mrlc.gov/data/project/annual-nlcd
- https://www.mrlc.gov/data-services-page
- https://www.mrlc.gov/faq
- https://www.mrlc.gov/data
- https://catalog.data.gov/dataset/annual-national-land-cover-database-nlcd-conterminous-united-states-collection-1-1-land-co
- https://sciencebase.gov/catalog/item/6810c151d4be022940554070
- https://doi.org/10.5066/P94UXNTS
- https://links.esri.com/LCLayer
