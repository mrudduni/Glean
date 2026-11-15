"""validation.json (handover 5.7): model vs OpenET, model vs SMAP, POWER vs IMERG / CoCoRaHS.

The model side is R0 run on the field's actual CDL crop sequence (not phase-averaged). Items whose
reference data D has not delivered are left out (never filled with made-up numbers) and logged.
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from model import config, inputs
from model.contract import meta, write_json
from model.replay import run as R
from model.replay.crop_calendar import build_timeline, place_history, profile_depth
from model.replay.water_balance import run_bucket


def actual_run(fid: str, crops: dict, weather: R.Weather) -> pd.DataFrame:
    field = inputs.field(fid)
    hist = field["crop_history"]
    start = date(hist[0]["year"] - 1, 1, 1)
    seasons = place_history(hist, crops, field["soil"], start)
    df = weather.df.loc[str(start):]
    tl = build_timeline(seasons, crops, df.index)
    irrigate = bool(field["irrigated"])
    res = run_bucket(tl, df["et0_mm"].to_numpy(), df["precip_mm"].to_numpy(), field["soil"],
                     config.CAP_MM[config.ACTUAL_RUN_CAP], irrigate, profile_depth(field["soil"]))
    wet = np.where(res.taw_root > 0, 1 - res.dr / res.taw_root, np.nan)
    return pd.DataFrame({"eta_mm": res.eta, "irr_mm": res.irr, "rel_wetness": wet}, index=df.index), \
        (hist[0]["year"], hist[-1]["year"])


def _level_bias_r(bias: float, r: float, rule: dict) -> str:
    g_b, g_r = rule["good"]
    if abs(bias) <= g_b and r >= g_r:
        return "good"
    return "fair" if abs(bias) <= rule["fair"][0] else "limited"


def et_vs_openet(fid: str, sim: pd.DataFrame, years: tuple[int, int]) -> dict | None:
    oe = inputs.processed_csv(fid, "openet_monthly.csv", date_col="month")
    if oe is None:
        return None
    lo = max(years[0], config.VALID_YEARS[0])
    hi = min(years[1], config.VALID_YEARS[1])
    model_m = sim["eta_mm"].resample("MS").sum()
    j = pd.DataFrame({"model": model_m, "openet": oe["et_mm"]}).dropna()
    j = j[(j.index.year >= lo) & (j.index.year <= hi) & j.index.month.isin(list(config.VALID_MONTHS))]
    if len(j) < 6:
        return None
    bias = 100 * (j.model.sum() - j.openet.sum()) / j.openet.sum()
    r2 = float(np.corrcoef(j.model, j.openet)[0, 1] ** 2)
    lev = config.LEVELS["et_vs_openet"]
    level = "good" if abs(bias) <= lev["good"][0] and r2 >= lev["good"][1] else "fair" if abs(bias) <= lev["fair"][0] else "limited"
    return {"id": "et_vs_openet", "metric": "bias_pct", "value": round(bias, 1), "n": int(len(j)), "level": level,
            "vars": {"bias_pct": round(bias, 1)}, "sources": ["MODEL", "OpenET"],
            "_extra": {"r2": round(r2, 2), "model_mm": round(j.model.sum()), "openet_mm": round(j.openet.sum()),
                       "period": f"{lo}-{hi}"}}


def sm_vs_smap(fid: str, sim: pd.DataFrame) -> dict | None:
    sm = inputs.processed_csv(fid, "smap_l4_daily.csv")
    if sm is None or "sm_rootzone_m3m3" not in sm:
        return None
    lo, hi = config.SMAP_YEARS
    j = pd.DataFrame({"model": sim["rel_wetness"], "smap": sm["sm_rootzone_m3m3"]}).dropna()
    j = j[(j.index.year >= lo) & (j.index.year <= hi)]
    if len(j) < 60:
        return None
    for c in ("model", "smap"):
        j[c] = j[c] - j.groupby(j.index.month)[c].transform("mean")
    r = float(np.corrcoef(j.model, j.smap)[0, 1])
    lev = config.LEVELS["sm_vs_smap"]
    level = "good" if r >= lev["good"] else "fair" if r >= lev["fair"] else "limited"
    return {"id": "sm_vs_smap", "metric": "r", "value": round(r, 2), "n": int(len(j)), "level": level,
            "vars": {"r": round(r, 2)}, "sources": ["MODEL", "SMAP"], "_extra": {"period": f"{j.index.year.min()}-{j.index.year.max()}"}}


def _precip_item(item_id: str, power: pd.Series, ref: pd.Series, ref_tag: str) -> dict | None:
    j = pd.DataFrame({"power": power, "ref": ref}).dropna()
    if len(j) < 12 or j.ref.sum() <= 0:
        return None
    bias = 100 * (j.power.sum() - j.ref.sum()) / j.ref.sum()
    r = float(np.corrcoef(j.power, j.ref)[0, 1])
    level = _level_bias_r(bias, r, config.LEVELS["precip"])
    return {"id": item_id, "metric": "bias_pct", "value": round(bias, 1), "n": int(len(j)), "level": level,
            "vars": {"bias_pct": round(bias, 1)}, "sources": ["POWER", ref_tag],
            "_extra": {"r": round(r, 2), "period": f"{j.index.min():%Y-%m}..{j.index.max():%Y-%m}"}}


def precip_checks(fid: str, weather: pd.DataFrame) -> tuple[list[dict], dict]:
    power_m = weather["precip_mm"].resample("MS").sum()
    items, extras = [], {}
    imerg = inputs.processed_csv(fid, "precip_imerg_daily.csv")
    obs = inputs.observed(fid) or {}
    pc = pd.DataFrame(obs.get("precip_check", []))
    if imerg is not None and len(imerg.dropna()):
        im = imerg["precip_mm"].dropna()
        full = im.resample("MS").count() >= 25
        im_m = im.resample("MS").sum()[full]
        it = _precip_item("precip_power_vs_imerg", power_m, im_m, "IMERG")
        if it:
            items.append(it)
    elif len(pc) and pc["imerg_mm"].notna().any():
        pc.index = pd.to_datetime(pc["month"])
        it = _precip_item("precip_power_vs_imerg", pc["power_mm"], pc["imerg_mm"], "IMERG")
        if it:
            items.append(it)
    if len(pc) and "cocorahs_mm" in pc and pc["cocorahs_mm"].notna().any():
        pc.index = pd.to_datetime(pc["month"])
        it = _precip_item("precip_vs_cocorahs", pc["power_mm"], pc["cocorahs_mm"], "CoCoRaHS")
        if it:
            items.append(it)
    # extra check for METHODS.md only (no contract id): POWER vs PRISM monthly precipitation
    prism = inputs.processed_csv(fid, "prism_daily.csv")
    if prism is not None:
        pm = prism["precip_mm"].resample("MS").sum()
        j = pd.DataFrame({"power": power_m, "prism": pm}).dropna().loc["2000":"2025"]
        if len(j):
            extras["power_vs_prism"] = {"bias_pct": round(100 * (j.power.sum() - j.prism.sum()) / j.prism.sum(), 1),
                                        "r": round(float(np.corrcoef(j.power, j.prism)[0, 1]), 2), "n": int(len(j))}
    return items, extras


def build_validation(fid: str, crops: dict, result: dict) -> tuple[dict, dict]:
    w = result["weather"]["actual"]
    sim, years = actual_run(fid, crops, w)
    items, log = [], {"missing": []}
    for fn, name in ((lambda: et_vs_openet(fid, sim, years), "et_vs_openet"), (lambda: sm_vs_smap(fid, sim), "sm_vs_smap")):
        it = fn()
        if it:
            items.append(it)
        else:
            log["missing"].append(name)
    full_weather = R.et0_mod.load_weather(fid)
    p_items, extras = precip_checks(fid, full_weather)
    items += p_items
    for name in ("precip_power_vs_imerg",):
        if not any(i["id"] == name for i in p_items):
            log["missing"].append(name)
    log["extras"] = extras
    log["items"] = {i["id"]: {**i["_extra"], "value": i["value"], "n": i["n"], "level": i["level"]} for i in items}
    public = [{k: v for k, v in i.items() if k != "_extra"} for i in items]
    return {"_meta": meta("validation@1", "model/validate/run.py"), "field_id": fid, "items": public}, log


def write_validation(fid: str, payload: dict) -> None:
    write_json(config.OUT_DIR / "field" / fid / "validation.json", payload)
