"""Build out/web/fields.json (README §8.3 FieldsFile) for f1, f2, f3.

Inputs: raw/fields_draft.geojson (select_fields), raw/ssurgo/fields_soil.json (ssurgo),
        raw/terrain.json (terrain), out/processed/{fid}/ndvi_modis.csv (optional, irrigation check).
Writes a schema-shaped file even when soil/terrain are still missing (values null),
so M and F can start; rerun when inputs arrive.

irrigated: f1 = true and f2 = false by definition of the demo roles; f3 is detected with
the same rule as the neighbours (MODIS Jul–Aug NDVI peak >= 0.75 in >= half of the CSB
years), falling back to pivot shape when NDVI is not available yet.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

import config as C  # noqa: E402
from common import rel, load_fields_draft, log, meta, polygon_geojson, read_json, simplify_to, write_json  # noqa: E402
from process.rotation_class import classify  # noqa: E402

OUT = C.WEB / "fields.json"
OUTPUTS = [OUT]
INPUTS = [C.RAW / "fields_draft.geojson", C.RAW / "ssurgo" / "fields_soil.json", C.RAW / "terrain.json"]

EMPTY_SOIL = {k: None for k in ["mukey", "map_unit_name", "component", "comppct", "texture", "awc_mm_per_m",
                                "aws_0_100_mm", "om_pct", "k_factor", "hydgrp", "slope_pct", "weg",
                                "wei_t_ac_yr", "drainage_class", "restrictive_depth_cm"]}


def ndvi_irrigated(ndvi: pd.DataFrame, years=C.CROP_YEARS) -> tuple[bool | None, list[float]]:
    """Jul–Aug QA-ok NDVI peak per year; irrigated if >= 0.75 in at least half the years."""
    d = ndvi[ndvi.qa_ok == 1].copy()
    d["date"] = pd.to_datetime(d.date)
    d = d[d.date.dt.month.isin([7, 8]) & d.date.dt.year.isin(years)]
    peaks = d.groupby(d.date.dt.year).ndvi.max()
    if len(peaks) < len(years) // 2:
        return None, peaks.round(3).tolist()
    return bool((peaks >= C.IRRIGATED_NDVI_PEAK).sum() >= len(peaks) / 2), peaks.round(3).tolist()


def main(force: bool = False) -> None:
    gdf = load_fields_draft()
    utm = gdf.to_crs(C.CRS_UTM14)
    soils = read_json(INPUTS[1]) if INPUTS[1].exists() else {}
    terrain = read_json(INPUTS[2]) if INPUTS[2].exists() else {}
    fields = []
    for fid in C.FIELD_IDS:
        row, geom_m = gdf.loc[fid], utm.geometry.loc[fid]
        geom_m = simplify_to(geom_m, 200)
        geom_w = gpd_to_wgs(geom_m)
        cen = geom_w.centroid if geom_w.contains(geom_w.centroid) else geom_w.representative_point()
        codes = [int(row[f"cdl_{y}"]) for y in C.CROP_YEARS]
        history = [{"year": y, "crop": C.cdl_to_crop(c), "cdl_code": c, "cdl_name": C.cdl_name(c)}
                   for y, c in zip(C.CROP_YEARS, codes)]
        det = classify([h["crop"] for h in history])
        det["years"] = [C.CROP_YEARS[0], C.CROP_YEARS[-1]]

        irrigated = {"f1": True, "f2": False}.get(fid)
        ndvi_p = C.PROCESSED / fid / "ndvi_modis.csv"
        nd_irr, peaks = (None, [])
        if ndvi_p.exists():
            nd_irr, peaks = ndvi_irrigated(pd.read_csv(ndvi_p))
        if irrigated is None:
            irrigated = nd_irr if nd_irr is not None else bool(row.get("pivot_fill", 0) >= 0.82)
        elif nd_irr is not None and nd_irr != irrigated:
            log("fields", f"WARNING {fid}: NDVI rule says irrigated={nd_irr} (Jul–Aug peaks {peaks})")
        log("fields", f"{fid}: irrigated={irrigated} (NDVI rule {nd_irr}, peaks {peaks})")

        t = terrain.get(fid, {})
        fields.append({
            "id": fid,
            "name": C.FIELD_META[fid]["name"],
            "kind": C.FIELD_META[fid]["kind"],
            "county_fips": C.COUNTY_FIPS_FULL,
            "centroid": [round(cen.x, 5), round(cen.y, 5)],
            "geometry": polygon_geojson(geom_w),
            "area_ha": round(geom_m.area / 10_000, 1),
            "area_ac": round(geom_m.area / 10_000 * C.HA_TO_AC, 1),
            "irrigated": irrigated,
            "csb_id": str(row["csb_id"]),
            "crop_history": history,
            "detected": det,
            "soil": soils.get(fid, {}).get("soil", EMPTY_SOIL),
            "terrain": {"elev_m": t.get("elev_m"), "slope_pct": t.get("slope_pct"),
                        "low_spot": t.get("low_spot")},
        })
    write_json(OUT, {"_meta": meta("fields", "process/build_fields.py"), "fields": fields})
    log("fields", f"wrote {rel(OUT)}")


def gpd_to_wgs(geom_m):
    import geopandas as gpd

    return gpd.GeoSeries([geom_m], crs=C.CRS_UTM14).to_crs(C.CRS_WGS84).iloc[0]


if __name__ == "__main__":
    main(force="--force" in sys.argv)
