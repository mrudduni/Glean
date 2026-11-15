"""Daily FAO-56 soil-water bucket (handover 5.3) with a two-layer profile.

The profile (depth Zmax) is split into the root zone (depth Zr) and the soil below it. Each layer
keeps its own depletion, so when roots grow they reach soil that carries its own stored water, and
fallow rain stored deep is there for the next crop. On bare days the upper layer is the FAO-56
surface evaporation layer (BARE_EVAP_DEPTH_M): rain wets it first, evaporation draws only from it,
and water that percolates below it stays stored for the next crop.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from model import config
from model.replay.crop_calendar import BARE, COVER, GROW, Timeline


def curve_number(hydgrp: str) -> int:
    letter = hydgrp.split("/")[0].strip().upper()   # dual groups: use the drained letter
    return config.CN_BY_HYDGRP[letter]


def scs_runoff(p: float, cn: float) -> float:
    if p <= 0:
        return 0.0
    s = 25400.0 / cn - 254.0
    ia = config.CN_IA_RATIO * s
    return (p - ia) ** 2 / (p - ia + s) if p > ia else 0.0


@dataclass
class DailyResult:
    eta: np.ndarray
    etc: np.ndarray
    ks: np.ndarray
    irr: np.ndarray
    runoff: np.ndarray
    drain: np.ndarray
    dr: np.ndarray           # root-zone depletion at end of day (mm)
    ds: np.ndarray           # depletion of the soil below the root zone (mm)
    taw_root: np.ndarray
    season_irr: dict         # season index -> applied irrigation (mm)


def run_bucket(tl: Timeline, et0: np.ndarray, precip: np.ndarray, soil: dict, cap_mm: float,
               irrigate: bool, zmax: float) -> DailyResult:
    n = len(et0)
    awc = float(soil["awc_mm_per_m"])
    taw_prof = awc * zmax
    cn_row = curve_number(soil["hydgrp"])
    cn_bare = min(99, cn_row + config.CN_BARE_ADD)
    eff = config.PIVOT_EFFICIENCY
    ze = min(config.BARE_EVAP_DEPTH_M, zmax)
    seasons = tl.seasons

    state, kc, zr_arr, sidx = tl.state.tolist(), tl.kc.tolist(), tl.zr.tolist(), tl.season.tolist()
    pl_frac = tl.p.tolist()
    et0l, pl = et0.tolist(), precip.tolist()
    eta, etc, ksa, irr, ro, dra, dro, tawr, dso = (np.zeros(n) for _ in range(9))
    season_irr: dict[int, float] = {}

    # layer depletions; start at 50 % of the profile
    zr = zr_arr[0] if state[0] != BARE else ze
    d_tot = config.SPINUP_DEPLETION_FRAC * taw_prof
    d_r = d_tot * zr / zmax
    d_s = d_tot - d_r

    for i in range(n):
        st = state[i]
        z_new = zr_arr[i] if st != BARE else ze
        if abs(z_new - zr) > 1e-9:
            # re-split the profile at the new root depth; each slice keeps its own depletion
            if z_new > zr:
                below = zmax - zr
                frac = (z_new - zr) / below if below > 1e-9 else 0.0
                move = d_s * frac
                d_r += move
                d_s -= move
            else:
                frac = (zr - z_new) / zr if zr > 1e-9 else 0.0
                move = d_r * frac
                d_r -= move
                d_s += move
            zr = z_new
        taw_r = awc * zr
        taw_s = taw_prof - taw_r
        p = pl[i]
        e0 = et0l[i]

        q = scs_runoff(p, cn_bare if st == BARE else cn_row)
        p_eff = p - q

        app = 0.0
        if st in (GROW, COVER):
            raw = pl_frac[i] * taw_r
            ks = 1.0 if d_r <= raw else max(0.0, (taw_r - d_r) / (taw_r - raw)) if taw_r > raw else 0.0
            e_c = kc[i] * e0
            k = sidx[i]
            if irrigate and st == GROW and k >= 0 and seasons[k].revenue and d_r > raw:
                used = season_irr.get(k, 0.0)
                want = d_r / eff
                if used + want <= cap_mm:
                    app = want              # refill to field capacity before today's ET
                    season_irr[k] = used + want
                    ks = 1.0
            e_a = ks * e_c
            etc[i] = e_c
            ksa[i] = ks
        else:
            # bare soil or a mature crop standing before harvest: soil evaporation only
            d_cur = d_r
            f = 1.0 if d_cur < config.BARE_STAGE1_MM else max(
                config.BARE_F_MIN, 1.0 - (d_cur - config.BARE_STAGE1_MM) / (config.BARE_DECAY_FRAC * taw_prof))
            e_a = config.BARE_KE * e0 * f
            ksa[i] = 1.0

        d_r = d_r - p_eff - eff * app + e_a
        drain = 0.0
        if d_r < 0:
            d_s += d_r          # excess percolates to the layer below
            d_r = 0.0
            if d_s < 0:
                drain = -d_s
                d_s = 0.0
        if d_r > taw_r:
            e_a -= d_r - taw_r  # cannot dry past wilting point
            d_r = taw_r
        if d_s > taw_s:
            d_s = taw_s
        eta[i] = e_a
        irr[i] = app
        ro[i] = q
        dra[i] = drain
        dro[i] = d_r
        dso[i] = d_s
        tawr[i] = taw_r
    return DailyResult(eta, etc, ksa, irr, ro, dra, dro, dso, tawr, season_irr)


__all__ = ["run_bucket", "scs_runoff", "curve_number", "DailyResult"]
