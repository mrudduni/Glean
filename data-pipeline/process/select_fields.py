"""Pick the 3 demo fields from the Finney County CSB polygons.

f1 · irrigated pivot : centre-pivot circle (area / min bounding circle >= 0.82), corn >= 6 of 8 years
f2 · dryland         : rectangular field classified wsf (wheat–sorghum–fallow), no corn
f3 · sandy / wind    : dominant SSURGO component with wind erodibility group 1–3, not alfalfa

All three prefer 50–65 ha, 8 known crop years, and lie within ~20 km of each other
(so their neighbour pools overlap). Selection is deterministic.
Override any pick by putting a CSB id in raw/field_overrides.json, e.g. {"f1": "200551234567"}.

Output: raw/fields_draft.geojson (EPSG:4326)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import geopandas as gpd  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import config as C  # noqa: E402
from common import rel, Skip, circularity, log, pivot_fill, simplify_to  # noqa: E402
from fetch import ssurgo  # noqa: E402
from process.rotation_class import classify  # noqa: E402

OUT = C.RAW / "fields_draft.geojson"
OUTPUTS = [OUT]
GARDEN_CITY = (-100.873, 37.971)
YEAR_COLS = [f"cdl_{y}" for y in C.CROP_YEARS]


def load_candidates() -> gpd.GeoDataFrame:
    p = C.RAW / "csb_finney.gpkg"
    if not p.exists():
        raise Skip("raw/csb_finney.gpkg missing — run fetch/csb.py")
    gdf = gpd.read_file(p)
    crops = gdf[YEAR_COLS].apply(lambda row: [C.cdl_to_crop(v) for v in row], axis=1)
    gdf["crops"] = crops
    gdf["known"] = crops.apply(lambda cs: sum(c != "other" for c in cs))
    gdf["circ"] = gdf.geometry.apply(circularity)
    gdf["pivot_fill"] = pivot_fill(gdf.geometry)
    gdf["rect_fill"] = gdf.area / gdf.geometry.minimum_rotated_rectangle().area
    cls = crops.apply(classify)
    gdf["rotation_class"] = cls.apply(lambda d: d["rotation_class"])
    gdf["confidence"] = cls.apply(lambda d: d["confidence"])
    gdf["n_corn"] = crops.apply(lambda cs: cs.count("corn"))
    wgs = gdf.geometry.representative_point().to_crs(C.CRS_WGS84)
    gdf["lon"], gdf["lat"] = wgs.x, wgs.y
    gc = gpd.GeoSeries.from_xy([GARDEN_CITY[0]], [GARDEN_CITY[1]], crs=C.CRS_WGS84).to_crs(C.CRS_UTM14).iloc[0]
    gdf["d_gc_km"] = gdf.geometry.representative_point().distance(gc) / 1000
    return gdf


def _area_score(a: pd.Series) -> pd.Series:
    # 1 inside 50–65 ha, falling off linearly to 0 at 35 / 80 ha
    return np.clip(np.minimum((a - 35) / 15, (80 - a) / 15), 0, 1)


def _dist_km(gdf, row) -> pd.Series:
    return gdf.geometry.representative_point().distance(row.geometry.representative_point()) / 1000


def pick_f1(gdf) -> pd.Series:
    """Centre-pivot circle, mostly corn, north of Garden City, close to town."""
    c = gdf[(gdf.known == 8) & (gdf.n_corn >= 6) & (gdf.pivot_fill >= 0.82) & gdf.area_ha.between(40, 70)]
    if c.empty:
        c = gdf[(gdf.known >= 7) & (gdf.n_corn >= 4) & (gdf.pivot_fill >= 0.78)]
    score = (_area_score(c.area_ha) + c.n_corn / 4 + (c.pivot_fill - 0.8) * 3
             + (c.lat > GARDEN_CITY[1]).astype(float) * 0.5   # "north pivot"
             - c.d_gc_km / 20)
    return c.loc[score.idxmax()]


def pick_f2(gdf, f1) -> pd.Series:
    """Rectangular dryland field with a clean wheat–sorghum–fallow history near f1."""
    base = (gdf.rect_fill >= 0.90) & (gdf.pivot_fill < 0.75) & gdf.area_ha.between(40, 70)
    c = gdf[base & (gdf.known == 8) & (gdf.rotation_class == "wsf") & (gdf.n_corn == 0)]
    if c.empty:
        c = gdf[base & (gdf.known >= 6) & gdf.rotation_class.isin(["wsf", "wheat_fallow"])]
    d = _dist_km(c, f1)
    if (d <= 15).any():
        c, d = c[d <= 15], d[d <= 15]
    score = (_area_score(c.area_ha) + (c.confidence == "good") * 1.0 + c.rect_fill - d / 15)
    return c.loc[score.idxmax()]


def pick_f3(gdf, f1, f2) -> tuple[pd.Series, dict]:
    """Sandy field (WEG 1–3) with bare-soil seasons in its rotation, near f1/f2."""
    c = gdf[(gdf.known >= 7) & gdf.area_ha.between(40, 75) & ~gdf.index.isin([f1.name, f2.name])]
    d = np.minimum(_dist_km(c, f1), _dist_km(c, f2))
    c = c[d <= 20].copy()
    # sandy soils are mostly south of the Arkansas River; check those first
    c["south"] = c.lat < GARDEN_CITY[1] - 0.01
    c = c[c.rotation_class != "alfalfa"]   # perennial cover: weak wind-erosion story
    c = c.sort_values(["south", "known", "area_ha"], ascending=[False, False, True]).head(400)
    log("select", f"f3: looking up SSURGO for {len(c)} candidates")
    mk = ssurgo.mukeys_at_points([(str(i), r.lon, r.lat) for i, r in c.iterrows()])
    soils = {m: ssurgo.soil_for_mukey(m) for m in set(v for v in mk.values() if v)}
    c["mukey"] = [mk.get(str(i)) for i in c.index]
    c["weg"] = c.mukey.map(lambda m: soils[m]["weg"] if m in soils else None)
    c["wei"] = c.mukey.map(lambda m: soils[m]["wei_t_ac_yr"] if m in soils else None)
    c["weg_rank"] = c.weg.map(ssurgo.weg_rank)
    s = c[c.weg_rank <= 3]
    if s.empty:
        raise RuntimeError("no candidate with WEG 1–3 within 20 km; widen the search")
    d = np.minimum(_dist_km(s, f1), _dist_km(s, f2))
    bare = s.crops.apply(lambda cs: sum(x in ("fallow", "wheat", "sorghum", "corn") for x in cs))
    new_class = ~s.rotation_class.isin([f1.rotation_class, f2.rotation_class, "mixed"])
    score = (_area_score(s.area_ha) + (s.known == 8) * 0.5 + (4 - s.weg_rank) * 0.3
             + s.wei.fillna(0) / 300 + (s.confidence == "good") * 0.3 + bare / 8
             + new_class * 0.5 - d / 20)
    best = s.loc[score.idxmax()]
    return best, soils[best.mukey]


def main(force: bool = False) -> None:
    if OUT.exists() and not force:
        log("select", f"exists: {OUT.name}")
        return
    gdf = load_candidates()
    log("select", f"{len(gdf):,} CSB fields; {int((gdf.known == 8).sum()):,} with 8 known years")
    overrides = {}
    ov = C.RAW / "field_overrides.json"
    if ov.exists():
        overrides = json.loads(ov.read_text())

    def chosen(fid, auto):
        if fid in overrides:
            row = gdf[gdf.csb_id == str(overrides[fid])]
            if row.empty:
                raise RuntimeError(f"override {fid}={overrides[fid]} not found in CSB")
            log("select", f"{fid}: using override CSB {overrides[fid]}")
            return row.iloc[0]
        return auto()

    f1 = chosen("f1", lambda: pick_f1(gdf))
    f2 = chosen("f2", lambda: pick_f2(gdf, f1))
    f3 = chosen("f3", lambda: pick_f3(gdf, f1, f2)[0])

    rows = []
    for fid, row in (("f1", f1), ("f2", f2), ("f3", f3)):
        geom = simplify_to(row.geometry, 200)
        rows.append({
            "id": fid, "csb_id": row.csb_id, "area_ha": round(geom.area / 10_000, 1),
            "circularity": round(float(row.circ), 3), "pivot_fill": round(float(row.pivot_fill), 3), "rotation_class": row.rotation_class,
            "crops": ",".join(row.crops), **{k: int(row[k]) for k in YEAR_COLS}, "geometry": geom,
        })
        log("select", f"{fid}: CSB {row.csb_id} {row.area_ha:.1f} ha pivot_fill={row.pivot_fill:.2f} rect={row.rect_fill:.2f} "
                      f"lon/lat={row.lon:.4f},{row.lat:.4f} {row.rotation_class}/{row.confidence} "
                      f"crops={list(row.crops)}")
    out = gpd.GeoDataFrame(rows, crs=C.CRS_UTM14).to_crs(C.CRS_WGS84)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_file(OUT, driver="GeoJSON")
    log("select", f"wrote {rel(OUT)}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
