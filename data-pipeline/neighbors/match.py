"""Farms Like Yours, step 2: similarity + groups -> out/web/field/{fid}/neighbors.json

For each demo field:
  * candidates = pool fields with the same `irrigated` value
  * features z-scored across the pool: awc_mm_per_m, om_pct, slope_pct, wei_t_ac_yr,
    hydgrp (ordinal A=1 … D=4; dual groups use the drained letter). Missing -> pool median.
  * distance = Euclidean; similarity = 1 / (1 + distance); keep the K=30 most similar
  * group by rotation_class; groups with n < 3 fold into "mixed"; a final "mixed" with n < 3 is dropped
Group stats: median OpenET annual ET, median NDVI drop in 2012 / 2022 (% below the 2016–2019
Jun–Aug normal; positive = less green), mean summer ECOSTRESS ESI.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import geopandas as gpd  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import config as C  # noqa: E402
from common import Skip, log, meta, polygon_geojson, r, read_json, simplify_to, write_json  # noqa: E402
from neighbors.pool import FEATURES, POOL  # noqa: E402

NUM = ["awc_mm_per_m", "om_pct", "slope_pct", "wei_t_ac_yr", "hyd_ord"]
OUTPUTS = [C.WEB_FIELD / fid / "neighbors.json" for fid in C.FIELD_IDS]
HYD = {"A": 1, "B": 2, "C": 3, "D": 4}


def hyd_ord(h) -> float:
    return float(HYD.get(str(h)[:1], np.nan)) if h else np.nan


def _med(s: pd.Series):
    s = pd.to_numeric(s, errors="coerce").dropna()
    return float(s.median()) if len(s) else None


def main(force: bool = False) -> None:
    if not FEATURES.exists():
        raise Skip("raw/neighbors/pool_features.csv missing — run neighbors/pool.py features")
    pool = pd.read_csv(FEATURES, dtype={"nid": str}).set_index("nid")
    geoms = gpd.read_file(POOL).set_index("nid").to_crs(C.CRS_UTM14)
    fields = {f["id"]: f for f in read_json(C.WEB / "fields.json")["fields"]}
    pool["hyd_ord"] = pool.hydgrp.map(hyd_ord)
    X = pool[NUM].astype(float)
    mu, sd = X.mean(), X.std(ddof=0).replace(0, 1)
    Z = ((X.fillna(X.median()) - mu) / sd)
    irr_method = pool.irr_method.value_counts().to_dict()

    for fid in C.FIELD_IDS:
        f = fields[fid]
        s = f["soil"]
        demo = pd.Series({"awc_mm_per_m": s["awc_mm_per_m"], "om_pct": s["om_pct"],
                          "slope_pct": s["slope_pct"], "wei_t_ac_yr": s["wei_t_ac_yr"],
                          "hyd_ord": hyd_ord(s["hydgrp"])}, dtype=float)
        zd = (demo.fillna(X.median()) - mu) / sd
        cand = pool.index[pool.irrigated.astype(bool) == bool(f["irrigated"])]
        dist = np.sqrt(((Z.loc[cand] - zd) ** 2).sum(axis=1))
        sim = (1 / (1 + dist)).sort_values(ascending=False)
        top = sim.head(C.NEIGHBOR_K)
        sel = pool.loc[top.index].assign(similarity=top)

        counts = sel.rotation_class.value_counts()
        group_of = sel.rotation_class.where(sel.rotation_class.map(counts) >= 3, "mixed")
        groups = []
        for cls, g in sel.groupby(group_of):
            if len(g) < 3:
                continue
            groups.append({
                "rotation_class": cls,
                "matches_rotation": C.CLASS_TO_ROTATION.get(cls),
                "is_current": cls == f["detected"]["rotation_class"],
                "n": int(len(g)),
                "et_mm_yr_median": r(_med(g.get("et_mm_yr", pd.Series(dtype=float)))),
                "ndvi_drop_2012_pct": r(_med(g.get("ndvi_drop_2012_pct", pd.Series(dtype=float))), 1),
                "ndvi_drop_2022_pct": r(_med(g.get("ndvi_drop_2022_pct", pd.Series(dtype=float))), 1),
                "esi_summer_mean": r(pd.to_numeric(g.get("esi_summer_mean", pd.Series(dtype=float)),
                                                   errors="coerce").mean(), 2),
            })
        groups.sort(key=lambda g: (-g["n"], g["rotation_class"]))

        out_fields = []
        for nid, row in sel.iterrows():
            gm = simplify_to(geoms.geometry.loc[nid], 60)
            gw = gpd.GeoSeries([gm], crs=C.CRS_UTM14).to_crs(C.CRS_WGS84).iloc[0]
            out_fields.append({"id": f"csb_{nid}", "centroid": [round(row.lon, 5), round(row.lat, 5)],
                               "geometry": polygon_geojson(gw, 5), "rotation_class": row.rotation_class,
                               "irrigated": bool(row.irrigated), "similarity": round(float(row.similarity), 3)})
        note = ("Observational comparison of nearby USDA Crop Sequence Boundary fields with the same "
                "irrigation status and similar SSURGO soil; not a controlled experiment. Irrigation status "
                f"from {', '.join(f'{k} ({v})' for k, v in irr_method.items())}. NDVI drop = % below the "
                "field's 2016–2019 Jun–Aug mean (positive = less green).")
        doc = {"_meta": meta("neighbors", "neighbors/match.py"), "field_id": fid,
               "pool_size": int(len(pool)), "matched": int(len(sel)),
               "method": {"features": ["awc_mm_per_m", "om_pct", "slope_pct", "wei_t_ac_yr", "hydgrp",
                                       "irrigated (exact match)"],
                          "k": C.NEIGHBOR_K, "note": note},
               "groups": groups, "fields": out_fields}
        write_json(C.WEB_FIELD / fid / "neighbors.json", doc, compact=True)
        matches = [g["matches_rotation"] for g in groups if g["matches_rotation"]]
        log("match", f"{fid}: {len(cand)} candidates, kept {len(sel)}, groups "
                     f"{[(g['rotation_class'], g['n']) for g in groups]}, rotation matches {matches}")
        if not matches:
            log("match", f"  NOTE for M: {fid} has no group matching R1/R2/R4/R5")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
