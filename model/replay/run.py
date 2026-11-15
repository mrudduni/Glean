"""Rotation Replay: every field x rotation x scenario x phase, 2000-2025 -> replay.json."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from model import config, inputs
from model.contract import meta, write_json
from model.library.rotations import Rotation
from model.replay import et0 as et0_mod
from model.replay.crop_calendar import BARE, COVER, GROW, Timeline, build_timeline, place_cycle, profile_depth
from model.replay.economics import season_outcome
from model.replay.exposure import exposure_daily
from model.replay.water_balance import run_bucket

YEARS = list(range(config.YEAR_FROM, config.YEAR_TO + 1))
YEAR_KEYS = ["irrigation_mm", "eta_mm", "etc_mm", "stress_days", "rel_yield", "revenue_usd_ac", "bare_days",
             "water_erosion_idx", "wind_erosion_idx", "heat_days", "frost_events",
             "bare_storm_days", "bare_windy_days", "living_root_days"]


@dataclass
class Weather:
    df: pd.DataFrame          # spin-up start .. YEAR_TO, with et0_mm
    storm_p: np.ndarray       # precip used for storm days (IMERG if available, else POWER)
    storm_source: str


def weather_for(fid: str, field: dict, climate: str) -> Weather:
    df = et0_mod.field_weather(fid, field, climate).loc[config.SPINUP_START: f"{config.YEAR_TO}-12-31"]
    storm = df["precip_mm"].copy()
    src = "POWER"
    imerg = et0_mod.load_imerg(fid)
    if imerg is not None and len(imerg):
        im = imerg.reindex(df.index)
        if climate == "hotdry":
            im = im * config.HOTDRY_P_FACTOR
        storm = im.fillna(storm)
        src = "IMERG"
    return Weather(df, storm.to_numpy(), src)


def practice_for(rot: Rotation, field: dict, cap: str) -> tuple[bool, str]:
    irrigate = bool(field["irrigated"]) and rot.irrigated and cap != "dryland"
    return irrigate, "irrigated" if irrigate else "non_irrigated"


def feasible(rot: Rotation, field: dict, cap: str) -> bool:
    if not field["irrigated"] and rot.min_cap != "dryland":
        return False           # no well on this field
    return rot.feasible(cap)


def simulate(tl: Timeline, w: Weather, field: dict, crops: dict, cap: str, irrigate: bool, practice: str) -> pd.DataFrame:
    """One phase on one weather series -> per-calendar-year table (all years in the timeline)."""
    soil = field["soil"]
    df = w.df
    res = run_bucket(tl, df["et0_mm"].to_numpy(), df["precip_mm"].to_numpy(), soil, config.CAP_MM[cap],
                     irrigate, profile_depth(soil))
    tmax, tmin = df["tmax_c"].to_numpy(), df["tmin_c"].to_numpy()
    year = df.index.year.to_numpy()
    rev_season = np.array([k >= 0 and tl.seasons[k].revenue for k in tl.season.tolist()])
    stress = (tl.state == GROW) & rev_season & (res.ks < config.STRESS_KS)
    living = (tl.state == GROW) | (tl.state == COVER)
    # SSURGO map-unit slope: SRTM 30 m slope is noisy on flat fields (f2 reads 9 % on a 0-1 % soil)
    ex = exposure_daily(tl, crops, w.storm_p, df["ws10m_max_ms"].to_numpy(), soil, soil["slope_pct"])

    daily = pd.DataFrame({
        "year": year, "irrigation_mm": res.irr, "eta_mm": res.eta, "etc_mm": res.etc,
        "stress_days": stress.astype(int), "bare_days": (tl.state == BARE).astype(int),
        "water_erosion_idx": ex["water_idx"].to_numpy(), "wind_erosion_idx": ex["wind_idx"].to_numpy(),
        "bare_storm_days": ex["storm"].to_numpy().astype(int), "bare_windy_days": ex["windy"].to_numpy().astype(int),
        "living_root_days": living.astype(int),
    })
    out = daily.groupby("year").sum()
    out["revenue_usd_ac"] = 0.0
    out["heat_days"] = 0.0
    out["frost_events"] = 0.0
    out["rel_yield"] = np.nan
    out["crop"] = "fallow"
    rel_lists: dict[int, list] = {}
    for k, s in enumerate(tl.seasons):
        if not s.revenue:
            continue
        hy = s.harvest_year
        if hy not in out.index:
            continue
        o = season_outcome(s, k, crops, tl.season, tl.stage, res.eta, res.etc, tmax, tmin, practice, tl.index)
        out.loc[hy, "revenue_usd_ac"] += o["revenue"]
        out.loc[hy, "heat_days"] += o["heat_days"]
        out.loc[hy, "frost_events"] += int(o["frost"])
        rel_lists.setdefault(hy, []).append(o["rel_yield"])
        if out.loc[hy, "crop"] == "fallow":
            out.loc[hy, "crop"] = s.crop
    for hy, v in rel_lists.items():
        out.loc[hy, "rel_yield"] = float(np.mean(v))
    # years with no harvest: name the crop that held the ground longest in the growing season
    for y in out.index:
        if out.loc[y, "crop"] == "fallow":
            m = (year == y) & (df.index.month >= 4) & (df.index.month <= 10)
            names = pd.Series([c for c in tl.crop[m] if c])
            if len(names) and names.value_counts().iloc[0] > m.sum() / 2:
                out.loc[y, "crop"] = names.value_counts().index[0]
    out.attrs["season_irr"] = res.season_irr
    out.attrs["daily"] = res
    return out


def phase_timelines(rot: Rotation, crops: dict, soil: dict, index: pd.DatetimeIndex) -> list[Timeline]:
    start = index[0].date()
    end = index[-1].date()
    return [build_timeline(place_cycle(list(rot.steps), crops, soil, start, end, phase=p), crops, index)
            for p in range(len(rot.steps))]


def average_phases(tables: list[pd.DataFrame]) -> pd.DataFrame:
    yrs = YEARS
    rows = []
    for y in yrs:
        r = {"year": y}
        for k in YEAR_KEYS:
            vals = [t.loc[y, k] for t in tables]
            r[k] = float(np.nanmean(vals)) if k == "rel_yield" and not all(np.isnan(vals)) else (
                0.0 if k == "rel_yield" else float(np.mean(vals)))
        crops_y = [t.loc[y, "crop"] for t in tables]
        r["crop_mix"] = {c: crops_y.count(c) / len(crops_y) for c in dict.fromkeys(crops_y)}
        rows.append(r)
    return pd.DataFrame(rows).set_index("year")


def summarize(avg: pd.DataFrame) -> dict:
    rev = np.sort(avg["revenue_usd_ac"].to_numpy())
    return {
        "irrigation_mm_mean": avg["irrigation_mm"].mean(), "eta_mm_mean": avg["eta_mm"].mean(),
        "stress_days_mean": avg["stress_days"].mean(), "rel_yield_mean": avg["rel_yield"].mean(),
        "revenue_usd_ac_mean": avg["revenue_usd_ac"].mean(), "revenue_usd_ac_worst5": rev[:5].mean(),
        "bare_days_mean": avg["bare_days"].mean(), "bare_storm_days_mean": avg["bare_storm_days"].mean(),
        "bare_windy_days_mean": avg["bare_windy_days"].mean(), "water_erosion_idx": avg["water_erosion_idx"].mean(),
        "wind_erosion_idx": avg["wind_erosion_idx"].mean(), "heat_days_mean": avg["heat_days"].mean(),
        "frost_events_total": avg["frost_events"].sum(),
        # internal (not written to replay.json): used by scoring
        "living_root_days_mean": avg["living_root_days"].mean(),
    }


SUMMARY_ROUND = {"irrigation_mm_mean": 0, "eta_mm_mean": 0, "stress_days_mean": 0, "rel_yield_mean": 2,
                 "revenue_usd_ac_mean": 0, "revenue_usd_ac_worst5": 0, "bare_days_mean": 0,
                 "bare_storm_days_mean": 0, "bare_windy_days_mean": 0, "water_erosion_idx": 2,
                 "wind_erosion_idx": 2, "heat_days_mean": 0, "frost_events_total": 2}
YEAR_ROUND = {"irrigation_mm": 0, "eta_mm": 0, "etc_mm": 0, "stress_days": 0, "rel_yield": 2, "revenue_usd_ac": 0,
              "bare_days": 0, "water_erosion_idx": 2, "wind_erosion_idx": 2, "heat_days": 0, "frost_events": 2}


def _r(x: float, nd: int):
    v = round(float(x), nd)
    return int(v) if nd == 0 else v


def run_json(run: dict) -> dict:
    return {
        "feasible": run["feasible"],
        "summary": {k: _r(run["summary"][k], nd) for k, nd in SUMMARY_ROUND.items()},
        "by_year": [{"year": int(y), "crop_mix": {c: round(v, 2) for c, v in r["crop_mix"].items()},
                     **{k: _r(r[k], nd) for k, nd in YEAR_ROUND.items()}}
                    for y, r in run["years"].iterrows()],
    }


def drought_years(fid: str, w_actual: Weather) -> list[int]:
    df = w_actual.df.loc[f"{config.YEAR_FROM}": f"{config.YEAR_TO}"]
    jja = df[df.index.month.isin([6, 7, 8])]
    g = jja.groupby(jja.index.year)[["precip_mm", "et0_mm"]].sum()
    dry = g[(g.precip_mm <= g.precip_mm.quantile(config.DROUGHT_P_QUANTILE))
            & (g.et0_mm >= g.et0_mm.quantile(config.DROUGHT_ET0_QUANTILE))].index.tolist()
    obs = inputs.observed(fid) or {}
    dry += [d["year"] for d in obs.get("drought_years", []) if d["ndvi_summer_anom_pct"] <= config.DROUGHT_NDVI_ANOM_PCT]
    return sorted({int(y) for y in dry if config.YEAR_FROM <= y <= config.YEAR_TO})


def worst_drought_year(w_actual: Weather, years: list[int]) -> int | None:
    if not years:
        return None
    df = w_actual.df
    jja = df[df.index.month.isin([6, 7, 8])]
    g = jja.groupby(jja.index.year)[["precip_mm", "et0_mm"]].sum()
    deficit = (g.et0_mm - g.precip_mm).loc[years]
    return int(deficit.idxmax())


def run_field(fid: str, rotations: dict[str, Rotation], crops: dict) -> dict:
    """Return {scenario: {rid: run}} with full year tables, plus weather and drought info."""
    field = inputs.field(fid)
    weather = {cl: weather_for(fid, field, cl) for cl in config.CLIMATE_IDS}
    index = weather["actual"].df.index
    tls = {rid: phase_timelines(rot, crops, field["soil"], index) for rid, rot in rotations.items()}
    scen: dict[str, dict] = {}
    for sk in config.SCENARIOS:
        cap, cl = sk.split("|")
        scen[sk] = {}
        for rid, rot in rotations.items():
            irrigate, practice = practice_for(rot, field, cap)
            tables = [simulate(tl, weather[cl], field, crops, cap, irrigate, practice) for tl in tls[rid]]
            avg = average_phases(tables)
            scen[sk][rid] = {"feasible": feasible(rot, field, cap), "years": avg, "summary": summarize(avg),
                             "phases": tables}
    dyears = drought_years(fid, weather["actual"])
    return {"scenarios": scen, "weather": weather, "timelines": tls, "drought_years": dyears,
            "worst_drought_year": worst_drought_year(weather["actual"], dyears)}


def write_replay(fid: str, result: dict) -> None:
    payload = {
        "_meta": meta("replay@1", "model/replay/run.py"), "field_id": fid,
        "years": [config.YEAR_FROM, config.YEAR_TO], "drought_years": result["drought_years"],
        "scenarios": {sk: {rid: run_json(run) for rid, run in runs.items()} for sk, runs in result["scenarios"].items()},
    }
    write_json(config.OUT_DIR / "field" / fid / "replay.json", payload)
