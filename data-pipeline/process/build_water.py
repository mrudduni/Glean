"""Build out/web/field/{fid}/water.json (README §8.3 WaterFile).

  grace              : raw/grace/grace_fields.json + processed grace_monthly.csv
                       (null until GRACE is downloaded — needs an Earthdata login)
  wells              : raw/wells/wells.json (USGS)
  smap_rootzone_anom : monthly mean root-zone soil moisture, % anomaly vs the 2015–2025
                       mean for that calendar month (empty until SMAP arrives)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

import config as C  # noqa: E402
from common import log, meta, read_json, write_json  # noqa: E402

OUTPUTS = [C.WEB_FIELD / fid / "water.json" for fid in C.FIELD_IDS]
INPUTS = [C.RAW / "grace" / "grace_fields.json", C.RAW / "wells" / "wells.json"]


def smap_anom(fid: str) -> list[dict]:
    p = C.PROCESSED / fid / "smap_l4_daily.csv"
    if not p.exists():
        return []
    d = pd.read_csv(p, parse_dates=["date"]).dropna(subset=["sm_rootzone_m3m3"])
    m = d.set_index("date").sm_rootzone_m3m3.resample("MS").mean().dropna()
    clim = m.groupby(m.index.month).transform("mean")
    anom = ((m / clim - 1) * 100).round(0)
    return [{"month": t.strftime("%Y-%m"), "anom_pct": int(v)} for t, v in anom.items()]


def grace_block(fid: str) -> dict | None:
    info = read_json(INPUTS[0]) if INPUTS[0].exists() else {}
    p = C.PROCESSED / fid / "grace_monthly.csv"
    if fid not in info or not p.exists():
        return None
    s = pd.read_csv(p).dropna()
    return {"cell_center": info[fid]["cell_center"],
            "series": [{"month": m, "tws_anom_cm": round(float(v), 2)} for m, v in zip(s.month, s.tws_anom_cm)],
            "trend_cm_per_yr": info[fid]["trend_cm_per_yr"], "period": info[fid]["period"]}


def main(force: bool = False) -> None:
    wells = read_json(INPUTS[1]) if INPUTS[1].exists() else {}
    for fid in C.FIELD_IDS:
        g = grace_block(fid)
        sm = smap_anom(fid)
        doc = {"_meta": meta("water", "process/build_water.py"), "field_id": fid,
               "grace": g, "wells": wells.get(fid, []), "smap_rootzone_anom": sm}
        write_json(C.WEB_FIELD / fid / "water.json", doc, compact=True)
        log("water", f"{fid}: grace={'yes' if g else 'MISSING'} wells={len(doc['wells'])} smap_months={len(sm)}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
