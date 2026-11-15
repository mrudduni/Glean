"""Field Calendar data (handover 5.4): monthly climate-risk odds and crop/bare state per rotation year."""
from __future__ import annotations

import numpy as np
import pandas as pd

from model import config, inputs
from model.contract import meta, write_json
from model.replay.crop_calendar import BARE, DRY, STAGES, Timeline

PATTERN_YEARS = range(2003, 2016)
WINTER_DORMANT_MONTHS = {11, 12, 1, 2}


def climate_risk(fid: str, weather: pd.DataFrame, storm_p: np.ndarray) -> list[dict]:
    df = weather.loc[f"{config.YEAR_FROM}": f"{config.YEAR_TO}"].copy()
    df["storm_p"] = pd.Series(storm_p, index=weather.index).loc[df.index]
    prism = inputs.processed_csv(fid, "prism_daily.csv")
    tmin = df["tmin_c"]
    if prism is not None and "tmin_c" in prism:
        tmin = prism["tmin_c"].reindex(df.index).fillna(df["tmin_c"])
    df["tmin_frost"] = tmin
    years = sorted(set(df.index.year))
    # dry spells: runs of >= CAL_DRY_RUN_DAYS days with rain < CAL_DRY_MM, marked on every day of the run
    dry = (df["precip_mm"] < config.CAL_DRY_MM).to_numpy()
    in_spell = np.zeros(len(dry), dtype=bool)
    i = 0
    while i < len(dry):
        if dry[i]:
            j = i
            while j < len(dry) and dry[j]:
                j += 1
            if j - i >= config.CAL_DRY_RUN_DAYS:
                in_spell[i:j] = True
            i = j
        else:
            i += 1
    df["spell"] = in_spell
    out = []
    for m in range(1, 13):
        d = df[df.index.month == m]
        g = d.groupby(d.index.year)
        heat = (g["tmax_c"].apply(lambda s: (s >= config.CAL_HEAT_TMAX).sum()) >= config.CAL_HEAT_MIN_DAYS).reindex(years, fill_value=False)
        frost = g["tmin_frost"].apply(lambda s: (s <= config.CAL_FROST_TMIN).any()).reindex(years, fill_value=False)
        spell = g["spell"].any().reindex(years, fill_value=False)
        storm = g["storm_p"].apply(lambda s: (s >= config.STORM_MM).sum()).reindex(years, fill_value=0)
        windy = g["ws10m_max_ms"].apply(lambda s: (s >= config.WINDY_MS).sum()).reindex(years, fill_value=0)
        out.append({"month": m, "p_heat": round(float(heat.mean()), 2), "p_frost": round(float(frost.mean()), 2),
                    "p_dry_spell": round(float(spell.mean()), 2), "storm_days": round(float(storm.mean()), 2),
                    "windy_days": round(float(windy.mean()), 2)})
    return out


def _year_signature(tl: Timeline, year: int) -> tuple:
    m = tl.index.year == year
    st = tl.state[m]
    cr = tl.crop[m]
    # sample twice a month so leap years compare cleanly
    idx = np.linspace(0, m.sum() - 1, 24).astype(int)
    return tuple((int(st[i]), cr[i]) for i in idx)


def cycle_years(tl: Timeline, n_steps: int) -> int:
    for p in range(1, 2 * n_steps + 3):
        if all(_year_signature(tl, y) == _year_signature(tl, y + p) for y in PATTERN_YEARS):
            return p
    return n_steps


def first_year(tl: Timeline, period: int, first_crop: str) -> int:
    for y in range(PATTERN_YEARS.start, PATTERN_YEARS.start + period):
        if any(s.crop == first_crop and s.revenue and s.harvest_year == y for s in tl.seasons):
            return y
    return PATTERN_YEARS.start


def month_cells(tl: Timeline, year: int, crops: dict, risk: list[dict]) -> list[dict]:
    cells = []
    for m in range(1, 13):
        mask = (tl.index.year == year) & (tl.index.month == m)
        crop_days = pd.Series([c for c in tl.crop[mask] if c])
        n = mask.sum()
        r = risk[m - 1]
        if len(crop_days) > n / 2 and crop_days.value_counts().index[0] != "fallow":
            crop = crop_days.value_counts().index[0]
            st = tl.stage[mask & (tl.crop == crop)]
            states = tl.state[mask & (tl.crop == crop)]
            grow_st = st[st >= 0]
            if len(grow_st):
                stage = STAGES[int(np.bincount(grow_st).argmax())]
            elif (states == DRY).any():
                stage = "late"
            else:
                stage = None
            c = crops[crop]
            dormant = c["season"] in ("winter", "cover", "perennial") and m in WINTER_DORMANT_MONTHS
            flags = []
            hs = c["heat"].get("stage")
            if hs and (st == STAGES.index(hs)).any() and r["p_heat"] >= config.CAL_FLAG_P:
                flags.append("heat")
            if not dormant and r["p_frost"] >= config.CAL_FLAG_P:
                flags.append("frost")
            if r["p_dry_spell"] >= config.CAL_FLAG_P:
                flags.append("dry")
            cells.append({"state": crop, "stage": stage, "flags": flags})
        else:
            flags = []
            if r["storm_days"] >= config.CAL_STORM_DAYS:
                flags.append("bare_storm")
            if r["windy_days"] >= config.CAL_WINDY_DAYS:
                flags.append("bare_wind")
            cells.append({"state": "bare", "stage": None, "flags": flags})
    return cells


def build_calendar(fid: str, result: dict, rotations: dict, crops: dict) -> dict:
    w = result["weather"]["actual"]
    risk = climate_risk(fid, w.df, w.storm_p)
    rots = []
    for rid, rot in rotations.items():
        tl = result["timelines"][rid][0]
        period = cycle_years(tl, len(rot.steps))
        y0 = first_year(tl, period, rot.steps[0].crop)
        rots.append({"rotation_id": rid, "years": [{"year_index": k + 1, "months": month_cells(tl, y0 + k, crops, risk)}
                                                   for k in range(period)]})
    return {"_meta": meta("calendar@1", "model/calendar/build.py"), "field_id": fid, "climate_risk": risk,
            "rotations": rots}


def write_calendar(fid: str, payload: dict) -> None:
    write_json(config.OUT_DIR / "field" / fid / "calendar.json", payload)
