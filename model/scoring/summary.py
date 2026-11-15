"""summary.json (handover 5.6): current rotation, climate normal vs recent, water outlook, headline facts."""
from __future__ import annotations

from datetime import date, timedelta
from statistics import median

import numpy as np
import pandas as pd

from model import config, inputs
from model.contract import HEADLINE_VARS, meta, write_json
from model.library.rotations import Rotation
from model.replay import et0 as et0_mod


def _mmdd(doy: float) -> str:
    return (date(2001, 1, 1) + timedelta(days=int(round(doy)) - 1)).strftime("%m-%d")


def climate_stats(t: pd.DataFrame, et0: pd.Series, years: tuple[int, int]) -> dict:
    """t has tmin_c, tmax_c, precip_mm (PRISM, or POWER as fallback)."""
    lo, hi = years
    t = t.loc[f"{lo}": f"{hi}"]
    springs, falls, ffd, gdd, hot, prec = [], [], [], [], [], []
    for y, d in t.groupby(t.index.year):
        if len(d) < 360:
            continue
        frost = d[d["tmin_c"] <= config.FROST_C]
        sp = frost[frost.index.month < 7]
        fa = frost[frost.index.month >= 7]
        if len(sp) and len(fa):
            ls, ff = sp.index[-1], fa.index[0]
            springs.append(ls.dayofyear - (1 if ls.is_leap_year and ls.month > 2 else 0))
            falls.append(ff.dayofyear - (1 if ff.is_leap_year and ff.month > 2 else 0))
            ffd.append((ff - ls).days - 1)
        g = d[(d.index.month >= 4) & (d.index.month <= 10)]
        tx = g["tmax_c"].clip(config.GDD_BASE_C, config.GDD_CAP_C)
        tn = g["tmin_c"].clip(config.GDD_BASE_C, config.GDD_CAP_C)
        gdd.append(float(((tx + tn) / 2 - config.GDD_BASE_C).clip(lower=0).sum()))
        hot.append(int((d["tmax_c"] >= config.HOT_DAY_C).sum()))
        prec.append(float(d["precip_mm"].sum()))
    e = et0.loc[f"{lo}": f"{hi}"]
    e_yr = e.groupby(e.index.year).sum()
    return {"frost_free_days": int(round(median(ffd))), "last_spring_frost": _mmdd(median(springs)),
            "first_fall_frost": _mmdd(median(falls)), "gdd_base10_c": int(round(np.mean(gdd))),
            "precip_mm_yr": int(round(np.mean(prec))), "days_tmax_ge_35": int(round(np.mean(hot))),
            "et0_mm_yr": int(round(e_yr[e_yr.index.isin(range(lo, hi + 1))].mean()))}


def water_block(fid: str) -> dict:
    w = inputs.water(fid) or {}
    grace = (w.get("grace") or {}).get("trend_cm_per_yr")
    trends = [x["trend_m_per_yr"] for x in w.get("wells", []) if x.get("trend_m_per_yr") is not None]
    wells = round(float(median(trends)), 2) if trends else None
    # wells trend is the depth-to-water trend: positive = water table falling
    declining = (grace is not None and grace < -config.OUTLOOK_GRACE_CM) or (wells is not None and wells > config.OUTLOOK_WELL_M)
    rising = (grace is not None and grace > config.OUTLOOK_GRACE_CM) or (wells is not None and wells < -config.OUTLOOK_WELL_M)
    outlook = "declining" if declining else "rising" if rising else "stable"
    return {"grace_trend_cm_per_yr": round(float(grace), 2) if grace is not None else 0.0,
            "wells_trend_m_per_yr": wells, "outlook": outlook}


def build_summary(fid: str, r0: Rotation) -> tuple[dict, dict]:
    field = inputs.field(fid)
    power = et0_mod.field_weather(fid, field, "actual")
    prism = inputs.processed_csv(fid, "prism_daily.csv")
    if prism is not None and {"tmin_c", "tmax_c", "precip_mm"} <= set(prism.columns):
        temps, srcs = prism[["tmin_c", "tmax_c", "precip_mm"]].dropna(), ["PRISM", "POWER"]
    else:
        temps, srcs = power[["tmin_c", "tmax_c", "precip_mm"]], ["POWER"]
    normal = climate_stats(temps, power["et0_mm"], config.NORMAL_PERIOD)
    recent = climate_stats(temps, power["et0_mm"], config.RECENT_PERIOD)
    water = water_block(fid)
    headlines = []
    w = inputs.water(fid) or {}
    if w.get("grace"):
        headlines.append({"text_id": "grace_trend", "vars": {"cm_per_yr": water["grace_trend_cm_per_yr"]}, "sources": ["GRACE"]})
    elif water["wells_trend_m_per_yr"] is not None:
        headlines.append({"text_id": "well_trend", "vars": {"m_per_yr": water["wells_trend_m_per_yr"]}, "sources": ["USGS"]})
    ffd = recent["frost_free_days"] - normal["frost_free_days"]
    heat = recent["days_tmax_ge_35"] - normal["days_tmax_ge_35"]
    tsrc = [srcs[0]]
    if abs(ffd) >= abs(heat):
        headlines.append({"text_id": "frost_free_change", "vars": {"days": ffd}, "sources": tsrc})
    else:
        headlines.append({"text_id": "heat_days_change", "vars": {"days": heat}, "sources": tsrc})
    yrs = list(r0.years) if r0.years else [config.YEAR_FROM, config.YEAR_TO]
    headlines.append({"text_id": "current_rotation", "vars": {"years_from": yrs[0], "years_to": yrs[1]}, "sources": ["CSB"]})
    for h in headlines:
        assert list(h["vars"]) == HEADLINE_VARS[h["text_id"]]
    payload = {
        "_meta": meta("summary@1", "model/scoring/summary.py"), "field_id": fid,
        "current_rotation": {"steps": [s.as_json() for s in r0.steps], "rotation_class": r0.rotation_class,
                             "years": yrs},
        "climate": {"normal": normal, "recent": recent, "normal_period": "1991-2020", "recent_period": "2016-2025",
                    "sources": srcs},
        "water": water, "headline_facts": headlines,
    }
    return payload, {"frost_free_change": ffd, "heat_days_change": heat}


def write_summary(fid: str, payload: dict) -> None:
    write_json(config.OUT_DIR / "field" / fid / "summary.json", payload)
