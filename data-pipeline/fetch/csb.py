"""USDA NASS Crop Sequence Boundaries (CSB) -> candidate fields in Finney County.

The CSB is only published as one national zip (~3.8 GB). We read it in place
(GDAL /vsizip/) with a bounding-box filter, so it is never fully extracted.

Output: raw/csb_finney.gpkg — one row per CSB field polygon inside the county,
        EPSG:32614, columns csb_id, area_ha, cdl_<year> for each of C.CROP_YEARS.
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import geopandas as gpd  # noqa: E402
import pyogrio  # noqa: E402

import config as C  # noqa: E402
from common import rel, Skip, download, log  # noqa: E402

ZIP = C.RAW / "csb" / f"{C.CSB_RELEASE}.zip"
OUT = C.RAW / "csb_finney.gpkg"
OUTPUTS = [OUT]


def _find_dataset(zpath: Path) -> tuple[str, str | None]:
    """Return (/vsizip/ path, layer name) for the GDB or SHP inside the zip."""
    with zipfile.ZipFile(zpath) as z:
        names = z.namelist()
    gdbs = sorted({re.sub(r"(\.gdb)/.*$", r"\1", n) for n in names if ".gdb/" in n})
    if gdbs:
        ds = f"/vsizip/{zpath.as_posix()}/{gdbs[0]}"
        return ds, None
    shps = [n for n in names if n.lower().endswith(".shp")]
    ks = [n for n in shps if re.search(r"(^|[^0-9])20[^0-9]|_KS|kansas", n, re.I)]
    pick = (ks or shps)[0]
    return f"/vsizip/{zpath.as_posix()}/{pick}", None


def main(force: bool = False) -> None:
    if OUT.exists() and not force:
        log("csb", f"exists: {OUT.name}")
        return
    county_p = C.RAW / f"county_{C.COUNTY_FIPS_FULL}.geojson"
    if not county_p.exists():
        raise Skip("county outline missing — run fetch/county.py")
    if not ZIP.exists() or ZIP.stat().st_size < 3_000_000_000:
        log("csb", f"downloading {ZIP.name} (~3.8 GB) — this takes a while")
        download(C.CSB_URL, ZIP, chunk=8 << 20)

    ds, _ = _find_dataset(ZIP)
    layers = pyogrio.list_layers(ds)
    layer = layers[0][0]
    for name, gtype in layers:
        if gtype and "polygon" in str(gtype).lower():
            layer = name
            break
    info = pyogrio.read_info(ds, layer=layer)
    crs = info["crs"]
    log("csb", f"dataset {ds.split('/')[-1]} layer={layer} features={info['features']:,} crs={crs}")

    county = gpd.read_file(county_p)
    county_l = county.to_crs(crs)
    minx, miny, maxx, maxy = county_l.total_bounds
    log("csb", "reading features in county bbox (one-time; can take several minutes)")
    gdf = pyogrio.read_dataframe(ds, layer=layer, bbox=(minx, miny, maxx, maxy))
    log("csb", f"{len(gdf):,} polygons in bbox")

    cols = {c.upper(): c for c in gdf.columns}
    # Prefer the attribute filter when the county code is present, then clip.
    st = cols.get("STATEFIPS")
    ct = cols.get("CNTYFIPS")
    if st and ct:
        gdf = gdf[(gdf[st].astype(str).str.zfill(2) == C.STATE_FIPS)
                  & (gdf[ct].astype(str).str.zfill(3) == C.COUNTY_FIPS)]
    county_l_geom = county_l.geometry.iloc[0]
    gdf = gdf[gdf.geometry.representative_point().within(county_l_geom)]

    year_cols = {}
    for y in C.CROP_YEARS:
        k = f"CDL{y}"
        if k not in cols:
            raise RuntimeError(f"CSB has no column {k}; columns: {list(gdf.columns)}")
        year_cols[cols[k]] = f"cdl_{y}"
    id_col = cols.get("CSBID") or cols.get("CSB_ID")
    out = gdf[[id_col, *year_cols, "geometry"]].rename(columns={id_col: "csb_id", **year_cols})
    out = out.to_crs(C.CRS_UTM14)
    out["csb_id"] = out["csb_id"].astype(str)
    out["area_ha"] = out.geometry.area / 10_000
    for c in year_cols.values():
        out[c] = out[c].fillna(0).astype(int)
    out = out.reset_index(drop=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_file(OUT, driver="GPKG")
    log("csb", f"wrote {rel(OUT)}: {len(out):,} fields in Finney County")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
