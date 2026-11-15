"""Daily bare-soil exposure and relative water and wind erosion indices (handover 5.3).

These are relative indices for comparing rotations on the same field, not tons of soil.
"""
from __future__ import annotations

import math
from datetime import timedelta

import numpy as np
import pandas as pd

from model import config
from model.replay.crop_calendar import BARE, Timeline


def residue_multiplier(tl: Timeline, crops: dict) -> np.ndarray:
    """1.0 on bare days, x residue factor for RESIDUE_DAYS after each harvest or termination."""
    n = len(tl.index)
    t0 = tl.index[0].date()
    mult = np.ones(n)
    for s in tl.seasons:
        if s.kind == "fallow" or s.kind == "estab":
            continue
        a = (s.harvest - t0).days
        b = (s.harvest + timedelta(days=config.RESIDUE_DAYS) - t0).days
        a, b = max(0, a), min(n, b)
        if a < b:
            f = config.RESIDUE_FACTOR[crops[s.crop]["residue"]]
            mult[a:b] = np.minimum(mult[a:b], f)
    return mult


def slope_factor(slope_pct: float) -> float:
    return 10.8 * math.sin(math.atan(slope_pct / 100.0)) + 0.03


def exposure_daily(tl: Timeline, crops: dict, storm_p: np.ndarray, ws10m_max: np.ndarray, soil: dict,
                   slope_pct: float) -> pd.DataFrame:
    bare = tl.state == BARE
    mult = residue_multiplier(tl, crops)
    storm = bare & (storm_p >= config.STORM_MM)
    windy = bare & (ws10m_max >= config.WINDY_MS)
    k = soil.get("k_factor") or 0.0
    wei = soil.get("wei_t_ac_yr") or 0.0
    water = np.where(storm, mult * storm_p / 25.4 * k * slope_factor(slope_pct), 0.0)
    wind = np.where(windy, mult * wei / config.WEI_MAX, 0.0)
    return pd.DataFrame({"bare": bare, "storm": storm, "windy": windy, "water_idx": water, "wind_idx": wind},
                        index=tl.index)
