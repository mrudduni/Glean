"""Daily weather loading, the hotdry transform, and FAO-56 Penman-Monteith ET0 via pyet."""
from __future__ import annotations

import math

import pandas as pd
import pyet

from model import config

WEATHER_COLS = ["tmax_c", "tmin_c", "tmean_c", "rh_pct", "ws2m_ms", "ws10m_ms", "ws10m_max_ms", "rs_mj_m2", "precip_mm"]


def load_weather(fid: str) -> pd.DataFrame:
    """POWER daily weather for one field, indexed by date, gaps filled by time interpolation."""
    path = config.DATA_DIR / "processed" / fid / "weather_daily.csv"
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    df = df.loc[: f"{config.YEAR_TO}-12-31"]
    df = df.reindex(pd.date_range(df.index[0], df.index[-1], freq="D"))
    df["precip_mm"] = df["precip_mm"].fillna(0.0).clip(lower=0)
    df[WEATHER_COLS] = df[WEATHER_COLS].interpolate("time", limit_direction="both")
    return df


def load_imerg(fid: str) -> pd.Series | None:
    path = config.DATA_DIR / "processed" / fid / "precip_imerg_daily.csv"
    if not path.exists():
        return None
    s = pd.read_csv(path, parse_dates=["date"]).set_index("date")["precip_mm"].sort_index()
    return s.dropna()


def apply_climate(df: pd.DataFrame, climate: str) -> pd.DataFrame:
    if climate == "actual":
        return df
    out = df.copy()
    for c in ("tmax_c", "tmin_c", "tmean_c"):
        out[c] = out[c] + config.HOTDRY_DT_C
    out["precip_mm"] = out["precip_mm"] * config.HOTDRY_P_FACTOR
    return out


def et0_fao56(df: pd.DataFrame, elev_m: float, lat_deg: float) -> pd.Series:
    """FAO-56 PM reference ET (mm/day). RH and wind are kept as observed in every climate."""
    et0 = pyet.pm_fao56(
        df["tmean_c"], df["ws2m_ms"], rs=df["rs_mj_m2"], tmax=df["tmax_c"], tmin=df["tmin_c"],
        rh=df["rh_pct"], elevation=elev_m, lat=math.radians(lat_deg),
    )
    return et0.clip(lower=0).fillna(0.0).rename("et0_mm")


def field_weather(fid: str, field: dict, climate: str) -> pd.DataFrame:
    """Weather with et0_mm for one field and climate, covering the replay period plus spin-up."""
    df = apply_climate(load_weather(fid), climate)
    df["et0_mm"] = et0_fao56(df, field["terrain"]["elev_m"], field["centroid"][1])
    return df
