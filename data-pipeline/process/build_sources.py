"""Build out/web/sources.json (README §8.3 SourcesFile) and docs/DATA_SOURCES.md.

Only SourceTags whose data actually reached out/ are listed in sources.json; the doc
also lists sources still pending (with the reason) and the datasets skipped on purpose.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config as C  # noqa: E402
from common import log, meta, read_json, write_json  # noqa: E402

OUT = C.WEB / "sources.json"
DOC = C.DOCS / "DATA_SOURCES.md"
OUTPUTS = [OUT, DOC]

CATALOG = {
    "POWER": dict(name="NASA POWER daily (AG community)", provider="NASA Langley Research Center",
                  url="https://power.larc.nasa.gov/",
                  what="Daily max/min/mean air temperature, humidity, wind at 2 m and 10 m, solar radiation, corrected precipitation",
                  resolution="0.5° × 0.625° grid, daily", period="1981–2025 (solar from 1984)",
                  used_for="Rotation Replay weather, reference ET, heat, frost and wind days"),
    "IMERG": dict(name="GPM IMERG Final Run daily (GPM_3IMERGDF v07)", provider="NASA GES DISC",
                  url="https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDF_07/summary",
                  what="Satellite-gauge merged daily precipitation", resolution="0.1° grid, daily",
                  period="2000-06 → 2025", used_for="Storm days and the POWER rainfall cross-check"),
    "SMAP": dict(name="SMAP L4 Global 3-hourly 9 km Surface and Root Zone Soil Moisture (SPL4SMGP v8)",
                 provider="NASA NSIDC DAAC, via AppEEARS", url="https://nsidc.org/data/spl4smgp",
                 what="Modelled + assimilated surface (0–5 cm) and root-zone (0–100 cm) soil moisture",
                 resolution="9 km, 3-hourly (averaged to daily)", period="2015-04 → 2025",
                 used_for="Soil-water check of the Replay and dry-period context"),
    "MODIS": dict(name="MODIS Terra Vegetation Indices 16-day (MOD13Q1 v6.1)", provider="NASA LP DAAC",
                  url="https://lpdaac.usgs.gov/products/mod13q1v061/",
                  what="NDVI with pixel reliability", resolution="250 m, 16-day composites",
                  period="2000–2025", used_for="Season curves, bare windows, drought-year greenness, neighbour irrigation check"),
    "ECOSTRESS": dict(name="ECOSTRESS L3 ET (ECO_L3T_JET v2) and L4 ESI (ECO_L4T_ESI v2)", provider="NASA LP DAAC, via AppEEARS",
                      url="https://lpdaac.usgs.gov/products/eco_l3t_jetv002/",
                      what="Daily ET estimate and Evaporative Stress Index at each cloud-free overpass",
                      resolution="70 m, irregular overpasses", period="2018-07 → 2025",
                      used_for="Crop water-stress snapshots on the field and neighbours"),
    "GRACE": dict(name="JPL GRACE/GRACE-FO Mascon RL06.3 (CRI filtered)", provider="NASA JPL / PO.DAAC",
                  url="https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4",
                  what="Monthly terrestrial water storage anomaly (liquid water equivalent)",
                  resolution="0.5° grid; ~300 km true resolution", period="2002-04 → latest (gap 2017-07 → 2018-05)",
                  used_for="Regional aquifer / water-storage trend in the water outlook"),
    "SRTM": dict(name="SRTM Global 1 arc second DEM (SRTMGL1 v3)", provider="NASA LP DAAC, via AppEEARS",
                 url="https://lpdaac.usgs.gov/products/srtmgl1v003/", what="Elevation",
                 resolution="30 m", period="February 2000", used_for="Field slope and cold-air low-spot flag"),
    "SSURGO": dict(name="SSURGO via Soil Data Access", provider="USDA NRCS",
                   url="https://sdmdataaccess.sc.egov.usda.gov/",
                   what="Map units, components and horizons: AWC, AWS 0–100 cm, organic matter, K factor, hydrologic group, WEG/WEI, drainage, restrictions",
                   resolution="Map units at 1:12,000–1:24,000", period="Current release",
                   used_for="Soil water holding, erodibility, soil-health inputs and neighbour matching"),
    "CSB": dict(name="Crop Sequence Boundaries 2018–2025 (rev23)", provider="USDA NASS",
                url="https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/",
                what="Field polygons with the Cropland Data Layer crop for each year",
                resolution="Field polygons from 30 m CDL", period="2018–2025",
                used_for="Demo field outlines, crop history, detected rotation, neighbour pool"),
    "NASS": dict(name="Quick Stats", provider="USDA NASS", url="https://quickstats.nass.usda.gov/",
                 what="Survey yields (irrigated / non-irrigated), prices received, acres planted",
                 resolution="Finney County, SW Kansas district, Kansas", period="2000–2025 (prices 2015–2024)",
                 used_for="Yields, prices and the local-market check"),
    "OpenET": dict(name="OpenET Ensemble", provider="OpenET (NASA, USGS, DRI, EDF, Google and partners)",
                   url="https://etdata.org/", what="Actual evapotranspiration, ensemble of 6 satellite models",
                   resolution="30 m, monthly", period="2016 → latest",
                   used_for="Replay validation and neighbours' real water use"),
    "PRISM": dict(name="PRISM daily (4 km)", provider="PRISM Climate Group, Oregon State University",
                  url="https://prism.oregonstate.edu/", what="Daily min/max temperature and precipitation",
                  resolution="4 km, daily", period="1991–2025",
                  used_for="1991–2020 climate normals vs 2016–2025, ground-based check of POWER"),
    "USGS": dict(name="USGS Water Data APIs — groundwater field measurements", provider="U.S. Geological Survey",
                 url="https://api.waterdata.usgs.gov/",
                 what="Depth to water below land surface at monitoring wells (USGS, KGS and Kansas DWR wells)",
                 resolution="Individual wells", period="2000–2025",
                 used_for="Local aquifer trend near each field"),
    "FAO56": dict(name="FAO Irrigation and Drainage Paper 56 (Penman-Monteith, crop coefficients)", provider="FAO",
                  url="https://www.fao.org/4/x0490e/x0490e00.htm",
                  what="Reference ET method and crop coefficients (Kc)", resolution="Method, not a dataset",
                  period="1998", used_for="Reference ET and crop water demand in the Replay"),
    "MODEL": dict(name="Field Shift water-budget model (FAO-56)", provider="Team Brackets (M)",
                  url="https://github.com/mrudduni/Team-Brackets/blob/main/docs/METHODS.md",
                  what="Simulated yield, water use and soil outputs built from the inputs above",
                  resolution="Field, daily/annual", period="2016–2025",
                  used_for="Rotation Replay results and the calendar"),
}

SKIPPED = [
    ("GEDI", "Lidar canopy height/structure; Kansas cropland has no canopy structure that matters for rotation choice and footprints are sparse."),
    ("LANDFIRE", "Wildland fuel and vegetation types; built for fire management, not cropland rotations."),
    ("NLCD", "Land cover every 2–3 years at 30 m; CDL / Crop Sequence Boundaries already give the crop each year."),
    ("ERA5", "Global reanalysis at ~31 km; NASA POWER covers the same need here. ERA5 is the path to taking the tool global."),
    ("GLDAS", "Global land model at 0.25°; SMAP L4 gives assimilated soil moisture at 9 km. Also a path to going global."),
    ("NLDAS", "North American land model at 1/8°; overlaps POWER + SMAP and adds a third weather source without a clear gain."),
    ("STATSGO2", "Generalised 1:250,000 soils; SSURGO is far more detailed for field-scale decisions."),
    ("Ag Data Commons", "A catalogue, not a dataset; the specific USDA datasets we need (CSB, NASS, SSURGO) are used directly."),
]
COULD = [
    ("HLS", "Harmonized Landsat Sentinel-2 30 m NDVI — COULD tier, not done; MODIS covers the season curves."),
    ("CoCoRaHS", "Volunteer rain gauges — COULD tier, not done; precip_check.cocorahs_mm is null."),
    ("GAEZ", "FAO future crop suitability — COULD tier, not done."),
    ("AMS", "USDA AMS local cash prices — COULD tier, not done; NASS Kansas prices are used."),
]


def used_tags() -> tuple[list[str], dict[str, str]]:
    P = C.PROCESSED
    has = lambda name: all((P / f / name).exists() for f in C.FIELD_IDS)  # noqa: E731
    terrain = read_json(C.RAW / "terrain.json") if (C.RAW / "terrain.json").exists() else {}
    t_src = {v.get("source") for v in terrain.values()}
    checks = {
        "POWER": has("weather_daily.csv"), "IMERG": has("precip_imerg_daily.csv"),
        "SMAP": has("smap_l4_daily.csv"), "MODIS": has("ndvi_modis.csv"), "ECOSTRESS": has("ecostress.csv"),
        "GRACE": has("grace_monthly.csv"), "SRTM": "SRTM" in t_src,
        "SSURGO": (C.RAW / "ssurgo" / "fields_soil.json").exists() or (C.WEB / "fields.json").exists(),
        "CSB": (C.WEB / "fields.json").exists(), "NASS": (P / "nass.json").exists(),
        "OpenET": has("openet_monthly.csv"), "PRISM": has("prism_daily.csv"),
        "USGS": (C.RAW / "wells" / "wells.json").exists() or (C.WEB / "field" / "f1" / "water.json").exists(),
        "FAO56": True, "MODEL": True,
    }
    pending = {
        "IMERG": "needs an Earthdata login (or Giovanni CSVs in raw/imerg/)",
        "SMAP": "AppEEARS task needs an Earthdata login",
        "MODIS": "AppEEARS needs an Earthdata login; ORNL subset fallback still downloading",
        "ECOSTRESS": "AppEEARS task needs an Earthdata login",
        "GRACE": "PO.DAAC download needs an Earthdata login",
        "SRTM": "AppEEARS area task needs an Earthdata login; terrain currently from USGS 3DEP",
        "NASS": "needs NASS_API_KEY",
        "OpenET": "needs OPENET_API_KEY",
    }
    used = [t for t, ok in checks.items() if ok]
    return used, {t: pending.get(t, "not produced yet") for t, ok in checks.items() if not ok}


def write_doc(used: list[str], pending: dict[str, str], extra: dict[str, str]) -> None:
    lines = [
        "# Data sources",
        "",
        "Produced by `data-pipeline/process/build_sources.py` (D). The machine-readable version is",
        "`data-pipeline/out/web/sources.json`, which lists only the sources that reached the app.",
        "",
        "## Used",
        "",
        "| Tag | Dataset | Provider | Resolution | Period | Used for |",
        "|---|---|---|---|---|---|",
    ]
    for t in used:
        s = CATALOG[t]
        uf = s["used_for"] + (f" ({extra[t]})" if t in extra else "")
        lines.append(f"| `{t}` | [{s['name']}]({s['url']}) | {s['provider']} | {s['resolution']} | {s['period']} | {uf} |")
    if pending:
        lines += ["", "## Planned, not delivered yet", "", "| Tag | Dataset | Why it's missing |", "|---|---|---|"]
        for t, why in pending.items():
            s = CATALOG[t]
            lines.append(f"| `{t}` | [{s['name']}]({s['url']}) | {why} |")
    lines += ["", "## Access notes", "",
              "- MODIS NDVI comes from AppEEARS when available, otherwise from the ORNL DAAC MODIS/VIIRS",
              "  Land Product Subsets service (https://modis.ornl.gov/data/modis_webservice.html), which needs no login.",
              "- Terrain uses SRTM from AppEEARS when available, otherwise USGS 3DEP 1/3 arc-second elevation",
              "  (https://www.usgs.gov/3d-elevation-program) through the National Map ImageServer.",
              "- Groundwater uses the new USGS Water Data APIs; the legacy `waterservices.usgs.gov/nwis/gwlevels`",
              "  service was decommissioned in fall 2025.",
              "- PRISM series use the same time-series endpoint as the PRISM Data Explorer.",
              "", "## Skipped on purpose", "", "| Dataset | Why |", "|---|---|"]
    lines += [f"| {n} | {why} |" for n, why in SKIPPED]
    lines += ["", "## COULD tier, not done", "", "| Dataset | Status |", "|---|---|"]
    lines += [f"| {n} | {why} |" for n, why in COULD]
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(force: bool = False) -> None:
    used, pending = used_tags()
    extra = {}
    terrain = read_json(C.RAW / "terrain.json") if (C.RAW / "terrain.json").exists() else {}
    if any(v.get("source") == "3DEP" for v in terrain.values()):
        extra["USGS"] = "also terrain (USGS 3DEP) until SRTM arrives"
    sources = []
    for t in used:
        s = dict(CATALOG[t])
        if t in extra:
            s["used_for"] += f"; {extra[t]}"
        sources.append({"tag": t, **s})
    write_json(OUT, {"_meta": meta("sources", "process/build_sources.py"), "sources": sources})
    write_doc(used, pending, extra)
    log("sources", f"used {used}; pending {list(pending)}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
