"""PRISM 4 km daily time series at each demo field centre -> out/processed/{fid}/prism_daily.csv

Uses the same endpoint the PRISM Data Explorer calls (prism.oregonstate.edu/explorer),
so no manual export is needed. If you do export CSVs by hand from the Explorer,
drop them in raw/prism/{fid}.csv and they are parsed instead.
Columns: date, tmin_c, tmax_c, precip_mm (1991-01-01 -> 2025-12-31).
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

import config as C  # noqa: E402
from common import cached_json, load_fields_draft, log, request, write_csv  # noqa: E402

RPC = "https://prism.oregonstate.edu/explorer/dataexplorer/rpc.php"
COLUMNS = ["date", "tmin_c", "tmax_c", "precip_mm"]
OUTPUTS = [C.PROCESSED / fid / "prism_daily.csv" for fid in C.FIELD_IDS]


def _rpc(lon: float, lat: float) -> dict:
    resp = request("prism", "POST", RPC, timeout=600, data={
        "spares": "4km", "interp": "idw", "stats": "ppt tmin tmax", "units": "si",
        "range": "daily", "start": C.PRISM_START, "end": C.PRISM_END, "stability": "stable",
        "lon": f"{lon:.4f}", "lat": f"{lat:.4f}", "elev": "", "call": "pp/daily_timeseries",
        "proc": "gridserv"})
    resp.raise_for_status()
    d = resp.json()
    if d.get("errors"):
        raise RuntimeError(f"PRISM error: {d}")
    return d


def from_rpc(d: dict) -> pd.DataFrame:
    data = d["result"]["data"]
    dates = pd.date_range(pd.Timestamp(C.PRISM_START), pd.Timestamp(C.PRISM_END), freq="D")
    n = len(data["ppt"])
    if n != len(dates):
        log("prism", f"WARNING: got {n} days, expected {len(dates)}; aligning from start")
    return pd.DataFrame({"date": dates[:n].strftime("%Y-%m-%d"), "tmin_c": data["tmin"][:n],
                         "tmax_c": data["tmax"][:n], "precip_mm": data["ppt"][:n]})


def from_manual_csv(p: Path) -> pd.DataFrame:
    """PRISM Explorer CSV: ~10 metadata lines, then Date,ppt (mm),tmin (degrees C),tmax (degrees C)."""
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.lower().startswith("date"))
    df = pd.read_csv(io.StringIO("\n".join(lines[start:])))
    cols = {c: c.lower() for c in df.columns}
    df = df.rename(columns=cols)
    pick = lambda key: next(c for c in df.columns if c.startswith(key))  # noqa: E731
    return pd.DataFrame({"date": pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d"),
                         "tmin_c": df[pick("tmin")], "tmax_c": df[pick("tmax")],
                         "precip_mm": df[pick("ppt")]})


def main(force: bool = False) -> None:
    gdf = load_fields_draft()
    for fid, geom in gdf.geometry.items():
        dest = C.PROCESSED / fid / "prism_daily.csv"
        if dest.exists() and not force:
            log("prism", f"exists: {fid}/prism_daily.csv")
            continue
        manual = C.RAW / "prism" / f"{fid}.csv"
        if manual.exists():
            df = from_manual_csv(manual)
        else:
            c = geom.representative_point()
            d = cached_json(C.RAW / "prism" / f"{fid}_rpc.json", lambda: _rpc(c.x, c.y))
            df = from_rpc(d)
        for col in COLUMNS[1:]:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(2)
        write_csv(dest, df, COLUMNS)
        ann = df.assign(y=df.date.str[:4]).groupby("y").precip_mm.sum()
        log("prism", f"{fid}: {len(df)} days, median annual precip {ann.median():.0f} mm")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
