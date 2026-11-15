"""SSURGO soil attributes via USDA NRCS Soil Data Access (SDA).

Library module (used by select_fields, build_fields, neighbors/pool):
    mukeys_at_points([(id, lon, lat), ...]) -> {id: mukey}
    soil_for_mukey(mukey) -> Soil dict (README §8.3)
    polygon_mix(geom_wgs84) -> [(mukey, fraction), ...] by grid sampling

Every response is cached under raw/ssurgo/.
Run directly to fill soil for the 3 demo fields: raw/ssurgo/fields_soil.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

import config as C  # noqa: E402
from common import rel, Skip, log, read_json, request  # noqa: E402

SDA_URL = "https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest"
CACHE = C.RAW / "ssurgo"
POINT_CACHE = CACHE / "points.json"
OUT = CACHE / "fields_soil.json"
OUTPUTS = [OUT]


def sda(query: str) -> list[dict]:
    resp = request("sda", "POST", SDA_URL, json={"query": query, "format": "JSON+COLUMNNAME"}, timeout=180)
    resp.raise_for_status()
    if not resp.text.strip():
        return []
    data = resp.json()
    table = data.get("Table") or []
    if not table:
        return []
    cols, rows = table[0], table[1:]
    return [dict(zip(cols, row)) for row in rows]


def _f(x):
    try:
        return None if x is None or x == "" else float(x)
    except ValueError:
        return None


# ---------------------------------------------------------------- points -> mukey
def _point_key(lon: float, lat: float) -> str:
    return f"{lon:.5f},{lat:.5f}"


def mukeys_at_points(points: list[tuple[str, float, float]], batch: int = 40) -> dict[str, str | None]:
    cache: dict[str, str | None] = read_json(POINT_CACHE) if POINT_CACHE.exists() else {}
    todo = [(i, lon, lat) for i, lon, lat in points if _point_key(lon, lat) not in cache]
    for k in range(0, len(todo), batch):
        chunk = todo[k:k + batch]
        parts = [
            f"SELECT {n} AS i, mukey FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('POINT({lon:.6f} {lat:.6f})')"
            for n, (_, lon, lat) in enumerate(chunk)
        ]
        rows = sda(" UNION ALL ".join(parts))
        got = {int(r["i"]): str(r["mukey"]) for r in rows}
        for n, (_, lon, lat) in enumerate(chunk):
            cache[_point_key(lon, lat)] = got.get(n)
        CACHE.mkdir(parents=True, exist_ok=True)
        POINT_CACHE.write_text(json.dumps(cache))
        log("ssurgo", f"mukey lookups {min(k + batch, len(todo))}/{len(todo)}")
    return {i: cache.get(_point_key(lon, lat)) for i, lon, lat in points}


# ---------------------------------------------------------------- mukey -> Soil
def _fetch_mukey(mukey: str) -> dict:
    mu = sda(f"""
        SELECT mu.mukey, mu.muname, ma.aws0100wta, ma.drclassdcd, ma.hydgrpdcd
        FROM mapunit mu LEFT JOIN muaggatt ma ON ma.mukey = mu.mukey
        WHERE mu.mukey = '{mukey}'""")
    comps = sda(f"""
        SELECT cokey, compname, comppct_r, slope_r, weg, wei, majcompflag, hydgrp, drainagecl
        FROM component WHERE mukey = '{mukey}' ORDER BY comppct_r DESC""")
    dom = None
    majors = [c for c in comps if str(c.get("majcompflag", "")).lower() == "yes"]
    if majors or comps:
        dom = max(majors or comps, key=lambda c: _f(c["comppct_r"]) or 0)
    hz, restr = [], []
    if dom:
        hz = sda(f"""
            SELECT h.chkey, h.hzdept_r, h.hzdepb_r, h.om_r, h.kwfact, h.awc_r,
                   (SELECT TOP 1 tg.texdesc FROM chtexturegrp tg
                     WHERE tg.chkey = h.chkey AND tg.rvindicator = 'Yes') AS texdesc
            FROM chorizon h WHERE h.cokey = '{dom['cokey']}' ORDER BY h.hzdept_r""")
        restr = sda(f"SELECT MIN(resdept_r) AS resdept FROM corestrictions WHERE cokey = '{dom['cokey']}'")
    return {"mapunit": mu[0] if mu else {}, "components": comps, "dominant": dom,
            "horizons": hz, "restriction": restr[0] if restr else {}}


def raw_mukey(mukey: str) -> dict:
    p = CACHE / f"{mukey}.json"
    if p.exists():
        return read_json(p)
    data = _fetch_mukey(mukey)
    CACHE.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=1))
    return data


def _weighted_awc(horizons: list[dict], top: float = 0, bottom: float = 100) -> float | None:
    num = den = 0.0
    for h in horizons:
        a, b, awc = _f(h.get("hzdept_r")), _f(h.get("hzdepb_r")), _f(h.get("awc_r"))
        if a is None or b is None or awc is None:
            continue
        overlap = max(0.0, min(b, bottom) - max(a, top))
        num += awc * overlap
        den += overlap
    return num / den if den > 0 else None


_HYD = {"A", "B", "C", "D", "A/D", "B/D", "C/D"}


def soil_for_mukey(mukey: str) -> dict:
    d = raw_mukey(mukey)
    mu, dom, hz = d["mapunit"], d["dominant"] or {}, d["horizons"]
    top = hz[0] if hz else {}
    awc = _weighted_awc(hz)
    aws = _f(mu.get("aws0100wta"))
    hyd = (mu.get("hydgrpdcd") or dom.get("hydgrp") or "").strip()
    wei = _f(dom.get("wei"))
    texture = (top.get("texdesc") or "").strip().lower()
    return {
        "mukey": str(mukey),
        "map_unit_name": (mu.get("muname") or "").strip(),
        "component": (dom.get("compname") or "").strip(),
        "comppct": int(_f(dom.get("comppct_r")) or 0),
        "texture": texture,
        "awc_mm_per_m": round(awc * 1000) if awc is not None else None,
        "aws_0_100_mm": round(aws * 10) if aws is not None else None,
        "om_pct": round(_f(top.get("om_r")), 2) if _f(top.get("om_r")) is not None else None,
        "k_factor": _f(top.get("kwfact")),
        "hydgrp": hyd if hyd in _HYD else (hyd[:1] if hyd[:1] in _HYD else None),
        "slope_pct": round(_f(dom.get("slope_r")), 1) if _f(dom.get("slope_r")) is not None else None,
        "weg": (str(dom.get("weg")).strip() or None) if dom.get("weg") not in (None, "") else None,
        "wei_t_ac_yr": int(wei) if wei is not None else None,
        "drainage_class": (mu.get("drclassdcd") or dom.get("drainagecl") or "").strip(),
        "restrictive_depth_cm": int(_f(d["restriction"].get("resdept"))) if _f(d["restriction"].get("resdept")) is not None else None,
    }


def weg_rank(weg: str | None) -> int:
    """Numeric part of a wind erodibility group ('4L' -> 4); 99 if unknown."""
    if not weg:
        return 99
    digits = "".join(ch for ch in str(weg) if ch.isdigit())
    return int(digits) if digits else 99


# ---------------------------------------------------------------- polygon mix
def polygon_mix(geom_wgs84, n: int = 6) -> list[tuple[str, float]]:
    """Share of each map unit inside the polygon, from an n x n grid of points."""
    from shapely.geometry import Point

    minx, miny, maxx, maxy = geom_wgs84.bounds
    pts = []
    for i, x in enumerate(np.linspace(minx, maxx, n + 2)[1:-1]):
        for j, y in enumerate(np.linspace(miny, maxy, n + 2)[1:-1]):
            if geom_wgs84.contains(Point(x, y)):
                pts.append((f"g{i}_{j}", float(x), float(y)))
    keys = [m for m in mukeys_at_points(pts).values() if m]
    if not keys:
        return []
    vals, counts = np.unique(keys, return_counts=True)
    order = np.argsort(-counts)
    return [(str(vals[k]), float(counts[k] / counts.sum())) for k in order]


# ---------------------------------------------------------------- CLI
def field_soils() -> dict:
    """Soil for each demo field: dominant map unit at the centre + polygon mix check."""
    from common import load_fields_draft

    gdf = load_fields_draft()
    out = {}
    pts = [(fid, g.representative_point().x, g.representative_point().y) for fid, g in gdf.geometry.items()]
    centre = mukeys_at_points(pts)
    for fid, geom in gdf.geometry.items():
        mk = centre[fid]
        if not mk:
            raise RuntimeError(f"{fid}: no SSURGO map unit at centre")
        soil = soil_for_mukey(mk)
        mix = polygon_mix(geom)
        other = [(m, f) for m, f in mix if m != mk and f > 0.40]
        if other:
            soil["map_unit_name"] += " (mixed)"
            log("ssurgo", f"{fid}: map unit {other[0][0]} covers {other[0][1]:.0%} of the polygon")
        aws_check = soil["awc_mm_per_m"], soil["aws_0_100_mm"]
        log("ssurgo", f"{fid}: {soil['map_unit_name']} | {soil['texture']} | awc={aws_check[0]} mm/m "
                      f"aws={aws_check[1]} mm | WEG={soil['weg']} WEI={soil['wei_t_ac_yr']}")
        out[fid] = {"soil": soil, "mix": mix}
    return out


def main(force: bool = False) -> None:
    if OUT.exists() and not force:
        log("ssurgo", f"exists: {OUT.name}")
        return
    try:
        data = field_soils()
    except Skip:
        raise
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1))
    log("ssurgo", f"wrote {rel(OUT)}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
