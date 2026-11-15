"""Per-season yield response (FAO-33 Ky with heat and frost factors) and revenue."""
from __future__ import annotations

import numpy as np
import pandas as pd

from model import config
from model.replay.crop_calendar import STAGES, Season


def season_outcome(s: Season, k: int, crops: dict, sidx: np.ndarray, stage: np.ndarray, eta: np.ndarray,
                   etc: np.ndarray, tmax: np.ndarray, tmin: np.ndarray, practice: str,
                   dates: pd.DatetimeIndex) -> dict:
    """rel_yield, revenue and the stress counts for one revenue season (index k)."""
    c = crops[s.crop]
    mask = sidx == k
    s_eta, s_etc = float(eta[mask].sum()), float(etc[mask].sum())
    ratio = s_eta / s_etc if s_etc > 0 else 1.0
    ky = c["ky"] if c["ky"] is not None else 1.0
    water = max(0.0, 1.0 - ky * (1.0 - ratio))

    heat_days = 0
    if (c["heat"] or {}).get("stage") and c["heat"].get("tmax_c") is not None:
        hs = STAGES.index(c["heat"]["stage"])
        window = np.flatnonzero((stage == hs) & mask)[: config.HEAT_WINDOW_DAYS]
        heat_days = int((tmax[window] > c["heat"]["tmax_c"]).sum())
    heat_f = max(config.HEAT_FACTOR_MIN, 1.0 - config.HEAT_LOSS_PER_DAY * heat_days)

    frost = False
    if c["frost_kill_c"] is not None:
        first = 2 if c["season"] == "winter" else 1      # winter crops: heading onward; others: from dev
        frost = bool(((stage >= first) & mask & (tmin <= c["frost_kill_c"])).any())
    if c["season"] in config.SPRING_FREEZE_SEASONS:
        # after green-up the hardiness is gone: a spring freeze at boot/heading counts as a frost event
        mmdd = dates.strftime("%m-%d")
        spring = mask & (dates.year == s.harvest_year) & (mmdd >= config.SPRING_FREEZE_START)
        frost = frost or bool((spring & (tmin <= config.SPRING_FREEZE_C)).any())
    frost_f = config.FROST_FACTOR if frost else 1.0

    rel = water * heat_f * frost_f
    ym = c["yield"]["irrigated_default"] if practice == "irrigated" else c["yield"]["dryland_default"]
    revenue = rel * float(ym) * float(c["price"]["default"]) if s.revenue else 0.0
    return {"rel_yield": rel, "revenue": revenue, "heat_days": heat_days, "frost": frost,
            "eta": s_eta, "etc": s_etc}
