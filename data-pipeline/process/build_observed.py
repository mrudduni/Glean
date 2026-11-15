"""Build out/web/field/{fid}/observed.json (README §8.3 ObservedFile).

  ndvi_modis       : QA-filtered 16-day series (qa_ok == 1)
  ndvi_climatology : the 23 composites by day of year, 2000–2025 mean, p10, p90
  drought_years    : Jun–Aug mean NDVI anomaly (%) vs the 2016–2019 Jun–Aug mean, for
                     2002, 2011, 2012, 2018, 2020, 2022 and any other year below −10 %
                     (note: on rotated fields part of this is the crop in that year, not drought)
  openet_monthly   : processed openet_monthly.csv
  ecostress        : processed ecostress.csv
  precip_check     : monthly POWER vs IMERG totals (IMERG null where missing); CoCoRaHS not used
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import config as C  # noqa: E402
from common import log, meta, r, write_json  # noqa: E402

OUTPUTS = [C.WEB_FIELD / fid / "observed.json" for fid in C.FIELD_IDS]


def _read(fid: str, name: str, **kw) -> pd.DataFrame | None:
    p = C.PROCESSED / fid / name
    return pd.read_csv(p, **kw) if p.exists() else None


def ndvi_parts(nd: pd.DataFrame | None):
    if nd is None:
        return [], [], []
    nd = nd[nd.qa_ok == 1].dropna(subset=["ndvi"]).copy()
    nd["date"] = pd.to_datetime(nd.date)
    series = [{"date": d.strftime("%Y-%m-%d"), "ndvi": round(v, 3)} for d, v in zip(nd.date, nd.ndvi)]
    doy = nd.date.dt.dayofyear
    clim = nd.groupby(doy).ndvi.agg(mean="mean", p10=lambda s: s.quantile(0.1), p90=lambda s: s.quantile(0.9))
    clim = [{"doy": int(k), "mean": round(v["mean"], 3), "p10": round(v["p10"], 3), "p90": round(v["p90"], 3)}
            for k, v in clim.iterrows()]
    summer = nd[nd.date.dt.month.isin([6, 7, 8])].groupby(nd.date.dt.year).ndvi.mean()
    normal = summer.reindex(C.NDVI_NORMAL_YEARS).mean()
    anom = ((summer / normal - 1) * 100) if normal and not np.isnan(normal) else pd.Series(dtype=float)
    years = sorted(set(C.DROUGHT_YEARS) | set(anom[anom < -10].index))
    drought = [{"year": int(y), "ndvi_summer_anom_pct": r(anom.get(y), 1)} for y in years if y in anom.index]
    return series, clim, drought


def precip_check(fid: str) -> list[dict]:
    w = _read(fid, "weather_daily.csv", usecols=["date", "precip_mm"], parse_dates=["date"])
    if w is None:
        return []
    w = w[w.date >= C.IMERG_START].set_index("date").precip_mm
    pw = w.resample("MS").sum(min_count=28)
    im = _read(fid, "precip_imerg_daily.csv", parse_dates=["date"])
    if im is not None:
        s = im.set_index("date").precip_mm
        cnt = s.resample("MS").count()
        imm = s.resample("MS").sum().where(cnt >= cnt.index.days_in_month)  # full months only
    else:
        imm = pd.Series(dtype=float)
    return [{"month": m.strftime("%Y-%m"), "power_mm": r(v), "imerg_mm": r(imm.get(m)), "cocorahs_mm": None}
            for m, v in pw.dropna().items()]


def main(force: bool = False) -> None:
    for fid in C.FIELD_IDS:
        series, clim, drought = ndvi_parts(_read(fid, "ndvi_modis.csv"))
        et = _read(fid, "openet_monthly.csv")
        eco = _read(fid, "ecostress.csv")
        doc = {
            "_meta": meta("observed", "process/build_observed.py"), "field_id": fid,
            "ndvi_modis": series, "ndvi_climatology": clim, "drought_years": drought,
            "openet_monthly": [] if et is None else
            [{"month": m, "et_mm": r(v)} for m, v in zip(et.month, et.et_mm) if pd.notna(v)],
            "ecostress": [] if eco is None else
            [{"datetime": t, "et_mm_day": r(a, 2), "esi": r(b, 2)} for t, a, b in zip(eco.datetime, eco.et_mm_day, eco.esi)],
            "precip_check": precip_check(fid),
        }
        write_json(C.WEB_FIELD / fid / "observed.json", doc, compact=True)
        log("observed", f"{fid}: ndvi={len(series)} clim={len(clim)} drought={[(d['year'], d['ndvi_summer_anom_pct']) for d in drought]} "
                        f"openet={len(doc['openet_monthly'])} ecostress={len(doc['ecostress'])} "
                        f"precip_months={len(doc['precip_check'])}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
