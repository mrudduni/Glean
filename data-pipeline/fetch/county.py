"""US Census cartographic boundary for Finney County, KS (FIPS 20055).

Output: raw/county_20055.geojson (EPSG:4326)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import geopandas as gpd  # noqa: E402

import config as C  # noqa: E402
from common import rel, download, log  # noqa: E402

URL = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip"
OUT = C.RAW / f"county_{C.COUNTY_FIPS_FULL}.geojson"
OUTPUTS = [OUT]


def main(force: bool = False) -> None:
    if OUT.exists() and not force:
        log("county", f"exists: {OUT.name}")
        return
    z = C.RAW / "census" / "cb_2023_us_county_500k.zip"
    if not z.exists():
        log("county", "downloading Census cartographic boundary (11.6 MB)")
        download(URL, z)
    gdf = gpd.read_file(f"zip://{z}")
    sel = gdf[(gdf["STATEFP"] == C.STATE_FIPS) & (gdf["COUNTYFP"] == C.COUNTY_FIPS)]
    if len(sel) != 1:
        raise RuntimeError(f"expected 1 county, got {len(sel)}")
    sel = sel.to_crs(C.CRS_WGS84)[["GEOID", "NAME", "STATEFP", "COUNTYFP", "geometry"]]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sel.to_file(OUT, driver="GeoJSON")
    log("county", f"wrote {rel(OUT)} bounds={tuple(round(b, 3) for b in sel.total_bounds)}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
