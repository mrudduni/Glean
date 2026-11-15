"""OpenET Ensemble monthly ET (openet-api.org).

  demo fields : polygon time series -> out/processed/{fid}/openet_monthly.csv (month, et_mm)
  neighbours  : point time series at each pool centre -> raw/openet/neighbors_annual.json
                {nid: annual ET median (mm, full years only)}

Every response is cached in raw/openet/ (the free tier has request limits), so reruns
only fetch what is missing. Calls are counted against the "openet" budget in common.py
(90 per month); on the quota message or HTTP 429 the step stops and keeps what it has.
Also accepts manual Data Explorer CSV exports at raw/openet/{fid}.csv (columns
DateTime/time + ET or et_ensemble_mad).
Needs OPENET_API_KEY in data-pipeline/.env.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

import config as C  # noqa: E402
from common import Skip, load_fields_draft, log, mark_exhausted, read_json, request, write_csv  # noqa: E402

API = "https://openet-api.org/raster/timeseries"
DIR = C.RAW / "openet"
COLUMNS = ["month", "et_mm"]
OUTPUTS = [C.PROCESSED / fid / "openet_monthly.csv" for fid in C.FIELD_IDS]
END = "2025-12-31"   # one fixed range: a fallback range would spend a second request


class RateLimited(Exception):
    pass


def _post(kind: str, geometry: list[float]) -> list[dict]:
    """One OpenET request, counted against the 'openet' budget in common.BUDGETS."""
    if not C.OPENET_API_KEY:
        raise Skip("OPENET_API_KEY not set in data-pipeline/.env")
    body = {"date_range": [C.OPENET_START, END], "interval": "monthly", "geometry": geometry,
            "model": "Ensemble", "variable": "ET", "reference_et": "gridMET", "units": "mm",
            "file_format": "JSON"}
    if kind == "polygon":
        body["reducer"] = "mean"
    r = request("openet", "POST", f"{API}/{kind}", json=body,
                headers={"Authorization": C.OPENET_API_KEY}, timeout=300)
    # the free-tier quota comes back as 404 "Monthly request limit has been reached"
    if "request limit" in r.text.lower():
        mark_exhausted("openet", r.text[:120])
        raise RateLimited(r.text[:200])
    if not r.ok:
        raise RuntimeError(f"OpenET {kind}: {r.status_code} {r.text[:300]}")
    return r.json()


def to_monthly(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    tcol = next(c for c in df.columns if c.lower() in ("time", "date", "datetime"))
    vcol = next(c for c in df.columns if c != tcol and ("et" in c.lower() or c.lower() == "value"))
    out = pd.DataFrame({"month": pd.to_datetime(df[tcol]).dt.strftime("%Y-%m"),
                        "et_mm": pd.to_numeric(df[vcol], errors="coerce").round(0)})
    return out.dropna().drop_duplicates("month").sort_values("month")


def _cached(key: str, kind: str, geometry: list[float]) -> list[dict]:
    p = DIR / f"{key}.json"
    if p.exists():
        return read_json(p)
    rows = _post(kind, geometry)
    DIR.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rows))
    return rows


def demo(force: bool = False) -> None:
    gdf = load_fields_draft()
    for fid, geom in gdf.geometry.items():
        dest = C.PROCESSED / fid / "openet_monthly.csv"
        if dest.exists() and not force:
            continue
        manual = DIR / f"{fid}.csv"
        if manual.exists():
            df = to_monthly(pd.read_csv(manual).to_dict("records"))
        else:
            flat = [round(v, 6) for xy in geom.exterior.coords for v in xy]
            df = to_monthly(_cached(f"{fid}_polygon", "polygon", flat))
        write_csv(dest, df, COLUMNS)
        log("openet", f"{fid}: {len(df)} months {df.month.iloc[0]}..{df.month.iloc[-1]}")


def annual_median(df: pd.DataFrame) -> float | None:
    df = df.assign(year=df.month.str[:4])
    full = df.groupby("year").filter(lambda g: len(g) == 12)
    if full.empty:
        return None
    return float(full.groupby("year").et_mm.sum().median())


def neighbors(force: bool = False) -> None:
    p = C.RAW / "neighbors" / "pool.geojson"
    if not p.exists():
        raise Skip("neighbour pool not built yet")
    import geopandas as gpd

    pool = gpd.read_file(p)
    out_p = DIR / "neighbors_annual.json"
    out = read_json(out_p) if out_p.exists() and not force else {}
    limited = None
    try:
        for r in pool.itertuples():
            if str(r.nid) in out:
                continue
            rows = _cached(f"nb_{r.nid}", "point", [round(r.lon, 6), round(r.lat, 6)])
            out[str(r.nid)] = annual_median(to_monthly(rows))
    except (RateLimited, Skip) as e:
        limited = str(e)
    DIR.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(out))
    log("openet", f"neighbours: {sum(v is not None for v in out.values())}/{len(pool)} with annual ET")
    if limited:
        raise Skip(f"OpenET quota reached after {len(out)}/{len(pool)} neighbours; saved, rerun after "
                   f"the monthly reset to fetch the rest ({limited[:80]})")


def main(force: bool = False) -> None:
    try:
        demo(force)
    except RateLimited as e:
        raise Skip(f"OpenET quota reached before the demo fields finished; rerun after the monthly reset ({e})")
    neighbors(force)


if __name__ == "__main__":
    main(force="--force" in sys.argv)
