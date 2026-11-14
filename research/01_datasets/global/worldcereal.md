# ESA WorldCereal 2021

WorldCereal is an ESA-funded set of global 10 m crop maps for 2021. It is the closest global match to the US Cropland Data Layer, but it covers only one year and a few crop groups.

## Key facts

| Item | Value |
|---|---|
| Resolution | 10 m |
| Year | 2021 only (v1.0.0) |
| Products | temporary crops extent, winter cereals, spring cereals, maize (main and second season), active cropland, active irrigation |
| Tiling | By agro-ecological zone (AEZ). Karnal sits in AEZ 34119 and Ludhiana in AEZ 25147. |
| Values | Each product has a `classification` asset (0 or 100) and a `confidence` asset (0 to 100). 254 means no data, for example over built-up land. |
| Point access | STAC search at `https://stac.terrascope.be/search`, then a TiTiler point read at `https://titiler.terrascope.be/collections/{collection}/items/{item}/point/{lon},{lat}` |
| Auth | None for STAC and point reads. Full GeoTIFF download from Terrascope needs a free login. |
| Licence | CC BY 4.0 |
| Rice | No rice product |

Sources: https://esa-worldcereal.org/en/products/global-maps and probe output. Licence: https://producciocientifica.uv.es/documentos/67bc32b6478fbf5d29390b6e?lang=en (Van Tricht et al. 2023 dataset record).

## What the probe found

At the Karnal cropland point (29.69 N, 76.90 E):

| Product | Class | Confidence |
|---|---|---|
| Temporary crops | crop | 99 |
| Winter cereals | yes | 66 |
| Irrigation in winter season | yes | 86 |
| Maize, second season | yes | 50 |
| Maize, main season | no | 94 |

The point is very likely rice in kharif and wheat in rabi, the same as most of the district. WorldCereal has no rice class, so it can't show the rice. It also tags the point as second-season maize at 50 percent confidence, which is probably wrong. The active cropland reads returned HTTP 404 for every item.

At the Ludhiana cropland point, winter cereals came back "no" with only 37 percent confidence, inside the Punjab wheat belt.

## Role in the tool

- Use it to check that a drawn field is cropland and, with care, to confirm wheat in rabi.
- Do not use it to infer the current rotation. It has one year, no rice class, and low confidence on these points. Ask the farmer for the current rotation instead.
- For Indian crop history, the better candidates are Krishi-DSS parcel maps and a simple NDVI phenology classifier on HLS (see `../india/isro_data_access.md` and `../nasa/landsat_hls.md`).

## Sources

- https://esa-worldcereal.org/en/products/global-maps
- https://hydrological.org/datasets/esa-worldcereal (licence summary)
- Probe output: `research/04_data_probes/samples/global_probe_results.json`, key `worldcereal`
