"""Acceptance checks (handover §7) for everything in out/. Run before telling the team a file is ready.

    python data-pipeline/validate.py

Prints PASS / FAIL / PENDING per check. PENDING = the input has not arrived yet
(missing key or queued task), not a bug. Exit code 1 only on FAIL.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

import pandas as pd  # noqa: E402

import config as C  # noqa: E402

RES: list[tuple[str, str, str]] = []
CROPS = {"corn", "sorghum", "wheat", "soybean", "alfalfa", "triticale", "rye_cover", "cotton", "fallow"}
CLASSES = {"continuous_corn", "corn_wheat_sorghum", "corn_soy", "wsf", "wheat_fallow", "alfalfa", "mixed"}
SOIL_KEYS = ["mukey", "map_unit_name", "component", "comppct", "texture", "awc_mm_per_m", "aws_0_100_mm",
             "om_pct", "k_factor", "hydgrp", "slope_pct", "weg", "wei_t_ac_yr", "drainage_class",
             "restrictive_depth_cm"]


def check(name: str, ok: bool | None, detail: str = "") -> None:
    RES.append(("PENDING" if ok is None else "PASS" if ok else "FAIL", name, detail))


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def json_files() -> None:
    for p in sorted(C.OUT.rglob("*.json")):
        d = load(p)
        rel = p.relative_to(C.OUT).as_posix()
        first = next(iter(d)) if d else None
        m = d.get("_meta", {})
        ok = first == "_meta" and m.get("mock") is False and m.get("generator", "").startswith("data-pipeline/") \
            and m.get("schema", "").startswith(p.stem + "@")
        check(f"_meta first + mock:false  {rel}", ok, str(m) if not ok else "")
        size = p.stat().st_size
        check(f"size < 2 MB  {rel}", size < 2_000_000, f"{size / 1e6:.2f} MB")
        txt = p.read_text(encoding="utf-8")
        check(f"no NaN/Infinity  {rel}", not re.search(r"\b(NaN|Infinity)\b", txt))


def fields() -> None:
    d = load(C.WEB / "fields.json")
    if d is None:
        return check("fields.json exists", False)
    fs = d["fields"]
    check("fields.json has exactly f1, f2, f3", [f["id"] for f in fs] == C.FIELD_IDS)
    for f in fs:
        fid = f["id"]
        ring = f["geometry"]["coordinates"][0]
        check(f"{fid} polygon, ≤ 200 vertices", f["geometry"]["type"] == "Polygon" and 4 <= len(ring) <= 201,
              f"{len(ring)} vertices")
        h = f["crop_history"]
        check(f"{fid} 8-year crop_history oldest→newest", [x["year"] for x in h] == C.CROP_YEARS
              and all(x["crop"] in CROPS | {"other"} for x in h))
        det = f["detected"]
        check(f"{fid} detected class/sequence valid", det["rotation_class"] in CLASSES
              and all(c in CROPS for c in det["sequence"]) and det["confidence"] in ("good", "fair", "limited"))
        s = f["soil"]
        filled = all(k in s for k in SOIL_KEYS) and s["mukey"] is not None
        check(f"{fid} soil filled", filled)
        if filled:
            lo, hi = (50, 140) if "sand" in s["texture"] else (90, 260)
            check(f"{fid} aws_0_100_mm plausible for {s['texture']}", lo <= s["aws_0_100_mm"] <= hi,
                  f"{s['aws_0_100_mm']} mm")
        t = f["terrain"]
        check(f"{fid} terrain filled", all(t.get(k) is not None for k in ("elev_m", "slope_pct", "low_spot")), str(t))
        check(f"{fid} area_ac = area_ha × 2.471", abs(f["area_ac"] - f["area_ha"] * C.HA_TO_AC) < 0.2)
    kinds = {f["id"]: (f["kind"], f["irrigated"]) for f in fs}
    check("f1 irrigated pivot, f2 dryland", kinds.get("f1") == ("irrigated_pivot", True)
          and kinds.get("f2") == ("dryland", False))


def processed() -> None:
    for fid in C.FIELD_IDS:
        P = C.PROCESSED / fid
        w = P / "weather_daily.csv"
        if not w.exists():
            check(f"{fid} weather_daily.csv", False)
            continue
        df = pd.read_csv(w, parse_dates=["date"])
        r = df[(df.date >= "2000-01-01") & (df.date <= "2025-12-31")]
        full = pd.date_range("2000-01-01", "2025-12-31")
        check(f"{fid} weather 2000–2025 complete", len(r) == len(full) and r.drop(columns="date").notna().all().all(),
              f"{len(r)}/{len(full)} days, {int(r.isna().sum().sum())} empty cells")
        ann = r.groupby(r.date.dt.year).precip_mm.sum()
        check(f"{fid} annual precip ~400–550 mm (median)", 350 <= ann.median() <= 600, f"median {ann.median():.0f} mm")
        summer = r[r.date.dt.month.isin([6, 7, 8])]
        check(f"{fid} summer Tmax often > 32 °C", (summer.tmax_c > 32).mean() > 0.3,
              f"{(summer.tmax_c > 32).mean():.0%} of summer days")
        rs = r.rs_mj_m2.dropna()
        check(f"{fid} rs_mj_m2 mostly 5–30 (not kWh)", rs.between(5, 30).mean() > 0.85 and rs.median() > 10,
              f"median {rs.median():.1f}")
        nd = P / "ndvi_modis.csv"
        if nd.exists():
            n = pd.read_csv(nd, parse_dates=["date"])
            check(f"{fid} NDVI within −0.2…1.0", n.ndvi.between(-0.2, 1.0).all())
            if fid == "f1":
                ja = n[(n.qa_ok == 1) & n.date.dt.month.isin([7, 8])]
                peak = ja.groupby(ja.date.dt.year).ndvi.max().median()
                check("f1 irrigated corn peaks ~0.8 Jul–Aug", peak >= 0.7, f"median peak {peak:.2f}")
        else:
            check(f"{fid} ndvi_modis.csv", None, "waiting for AppEEARS / ORNL")
        sm = P / "smap_l4_daily.csv"
        if sm.exists():
            s = pd.read_csv(sm).sm_rootzone_m3m3.dropna()
            check(f"{fid} SMAP root-zone 0.05–0.45", s.between(0.05, 0.45).mean() > 0.98,
                  f"{s.min():.2f}–{s.max():.2f}")
        else:
            check(f"{fid} smap_l4_daily.csv", None, "needs Earthdata (AppEEARS)")
        for name, why in (("precip_imerg_daily.csv", "Earthdata"), ("openet_monthly.csv", "OPENET_API_KEY"),
                          ("ecostress.csv", "Earthdata (AppEEARS)"), ("grace_monthly.csv", "Earthdata"),
                          ("prism_daily.csv", "")):
            check(f"{fid} {name}", True if (P / name).exists() else None, "" if (P / name).exists() else f"needs {why}")
    nass = load(C.PROCESSED / "nass.json")
    if nass is None:
        check("nass.json", None, "needs NASS_API_KEY")
    else:
        ok = all(y.get("unit") and y.get("level") for y in nass["yields"]) and len(nass["yields"]) > 0
        check("NASS yields have unit + level", ok, f"{len(nass['yields'])} rows")


def web_field_files() -> None:
    for fid in C.FIELD_IDS:
        D = C.WEB_FIELD / fid
        w = load(D / "water.json")
        if w:
            check(f"{fid} water.json wells present", len(w["wells"]) > 0, f"{len(w['wells'])} wells")
            check(f"{fid} water.json grace block", None if w["grace"] is None else True,
                  "grace is null until GRACE is downloaded" if w["grace"] is None else "")
        o = load(D / "observed.json")
        if o:
            check(f"{fid} observed.json ndvi_climatology has 23 composites",
                  None if not o["ndvi_climatology"] else len(o["ndvi_climatology"]) == 23,
                  f"{len(o['ndvi_climatology'])}")
        n = load(D / "neighbors.json")
        if n is None:
            check(f"{fid} neighbors.json", False)
            continue
        check(f"{fid} neighbour groups all n ≥ 3", all(g["n"] >= 3 for g in n["groups"]),
              str([(g["rotation_class"], g["n"]) for g in n["groups"]]))
        check(f"{fid} a group matches R1/R2/R4/R5",
              any(g["matches_rotation"] in ("R1", "R2", "R4", "R5") for g in n["groups"]))
        check(f"{fid} neighbour polygons ≤ 60 vertices",
              all(len(x["geometry"]["coordinates"][0]) <= 61 for x in n["fields"]))
        check(f"{fid} similarity in 0–1", all(0 <= x["similarity"] <= 1 for x in n["fields"]))
        check(f"{fid} neighbour NDVI drop available",
              None if all(g["ndvi_drop_2012_pct"] is None for g in n["groups"]) else True, "needs MODIS for the pool")


def secrets() -> None:
    keys = [v for v in (C.NASS_API_KEY, C.OPENET_API_KEY, C.EARTHDATA_PASSWORD) if v and len(v) >= 6]
    leaked = [p for p in list(C.OUT.rglob("*")) + list(C.ROOT.glob("*.py")) + list(C.ROOT.rglob("*.md"))
              if p.is_file() and any(k in p.read_text(encoding="utf-8", errors="ignore") for k in keys)]
    check("no API keys in committed files", not leaked, ", ".join(map(str, leaked)))


def main() -> int:
    json_files()
    fields()
    processed()
    web_field_files()
    secrets()
    width = max(len(n) for _, n, _ in RES)
    for st, n, d in RES:
        print(f"{st:8s} {n:{width}s}  {d}")
    tally = {s: sum(1 for x in RES if x[0] == s) for s in ("PASS", "FAIL", "PENDING")}
    print(f"\n{tally}")
    return 1 if tally["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
