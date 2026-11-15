"""Season timing on a continuous daily timeline, plus daily Kc, root depth and ground state.

Each rotation step becomes one dated season. Planting uses the middle of plant_window (or the first
day after the previous harvest + MIN_GAP_DAYS if that is still inside the window, otherwise next
year). Grain crops grow over FAO-56 stage_days, stretched so maturity falls DRYDOWN_DAYS before the
middle of harvest_window; the mature crop then stands until harvest. Forage cuts and covers end at
the middle of harvest_window. Fallow lasts until FALLOW_END_MMDD of the following year. Alfalfa is
fall-seeded once, then each alfalfa step is one production season with a dormant stand between.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

import numpy as np
import pandas as pd

from model import config

# daily ground state codes
BARE, GROW, COVER, DRY = 0, 1, 2, 3
STAGES = ("ini", "dev", "mid", "late")
DRYDOWN_DAYS = 14


@dataclass
class Season:
    crop: str
    kind: str                     # grain | forage | cover | alfalfa | estab | fallow
    plant: date
    end_growth: date              # day after the last growing day
    harvest: date                 # day after the last day in the ground
    stage_ends: tuple[date, date, date, date] = ()
    revenue: bool = False
    zr_start: float = config.ROOT_INIT_M
    zr_max: float = config.ROOT_INIT_M
    root_full: date | None = None  # date roots reach zr_max
    phase_crops: list = field(default_factory=list)

    @property
    def harvest_year(self) -> int:
        return (self.harvest - timedelta(days=1)).year


def _md(year: int, mmdd: str) -> date:
    m, d = map(int, mmdd.split("-"))
    return date(year, m, d)


def _mid(year: int, win: dict) -> date:
    a, b = _md(year, win["start"]), _md(year, win["end"])
    return a + (b - a) / 2


def crop_timing(crop: str, crops: dict) -> dict:
    """plant_window, harvest_window and stage_days used by the replay (spring triticale override)."""
    c = crops[crop]
    if crop == "triticale":
        return dict(config.TRITICALE_SPRING)
    return {"plant_window": c["plant_window"], "harvest_window": c["harvest_window"], "stage_days": c["stage_days"]}


def next_plant(crop: str, crops: dict, earliest: date) -> date:
    win = crop_timing(crop, crops)["plant_window"]
    for y in (earliest.year, earliest.year + 1, earliest.year + 2):
        mid, end = _mid(y, win), _md(y, win["end"])
        if earliest <= mid:
            return mid
        if earliest <= end:
            return earliest
    raise ValueError(f"no planting date for {crop} after {earliest}")


def season_length(crop: str, crops: dict) -> int:
    t = crop_timing(crop, crops)
    y = 2001
    p, h = _mid(y, t["plant_window"]), _mid(y, t["harvest_window"])
    if h <= p:
        h = _mid(y + 1, t["harvest_window"])
    return (h - p).days


def _stage_ends(start: date, days: int, stage_days: dict) -> tuple:
    total = sum(stage_days[s] for s in STAGES) or 1
    ends, acc = [], 0.0
    for s in STAGES:
        acc += stage_days[s] * days / total
        ends.append(start + timedelta(days=round(acc)))
    ends[-1] = start + timedelta(days=days)
    return tuple(ends)


def _root_max(crop: str, crops: dict, soil: dict) -> float:
    z = crops[crop]["root_max_m"] or config.ROOT_INIT_M
    zmax = profile_depth(soil)
    return min(z, zmax)


def profile_depth(soil: dict) -> float:
    r = soil.get("restrictive_depth_cm")
    return min(config.ZMAX_M, r / 100) if r else config.ZMAX_M


def annual_season(crop: str, crops: dict, soil: dict, plant: date, kind: str) -> Season:
    t = crop_timing(crop, crops)
    L = season_length(crop, crops)
    total = sum(t["stage_days"][s] for s in STAGES)
    grow = L if kind in ("forage", "cover") else max(total, L - DRYDOWN_DAYS)
    harvest_after = max(L, grow)
    ends = _stage_ends(plant, grow, t["stage_days"])
    zr_max = _root_max(crop, crops, soil)
    return Season(crop, kind, plant, plant + timedelta(days=grow), plant + timedelta(days=harvest_after), ends,
                  revenue=kind in ("grain", "forage"), zr_max=zr_max, root_full=ends[1])


def alfalfa_block(n: int, crops: dict, soil: dict, cursor: date) -> list[Season]:
    """Fall establishment, then n production seasons. Returns seasons in order."""
    c = crops["alfalfa"]
    sd = c["stage_days"]
    total = sum(sd[s] for s in STAGES)
    plant = next_plant("alfalfa", crops, cursor)
    zr_max = _root_max("alfalfa", crops, soil)
    y = plant.year + 1
    greenup = _md(y, c["harvest_window"]["start"]) - timedelta(days=sd["ini"] + sd["dev"])
    seasons = [Season("alfalfa", "estab", plant, greenup, greenup, (greenup,) * 4, zr_max=zr_max,
                      root_full=greenup + timedelta(days=sd["ini"] + sd["dev"]))]
    for k in range(n):
        g = _md(y + k, c["harvest_window"]["start"]) - timedelta(days=sd["ini"] + sd["dev"])
        ends = _stage_ends(g, total, sd)
        seasons.append(Season("alfalfa", "alfalfa", g, ends[-1], ends[-1], ends, revenue=True,
                              zr_start=zr_max, zr_max=zr_max, root_full=g))
    return seasons


def kind_of(crop: str, crops: dict) -> str:
    if crop == "fallow":
        return "fallow"
    if crop == "rye_cover" or crops[crop]["season"] == "cover":
        return "cover"
    return "forage" if crops[crop]["forage"] else "grain"


def place_cycle(steps: list, crops: dict, soil: dict, start: date, end: date, phase: int = 0) -> list[Season]:
    """Lay the cycled rotation steps (starting at index `phase`) on the timeline until `end`."""
    L = len(steps)
    seasons: list[Season] = []
    cursor, i = start, phase
    while cursor < end:
        st = steps[i % L]
        if st.crop == "alfalfa":
            n = 0
            while n < L and steps[(i + n) % L].crop == "alfalfa":
                n += 1
            block = alfalfa_block(n, crops, soil, cursor)
            seasons.extend(block)
            cursor = block[-1].harvest + timedelta(days=config.MIN_GAP_DAYS)
            i += n
            continue
        if st.crop == "fallow":
            fend = _md(cursor.year + 1, config.FALLOW_END_MMDD)
            seasons.append(Season("fallow", "fallow", cursor, cursor, fend))
            cursor = fend
        else:
            s = annual_season(st.crop, crops, soil, next_plant(st.crop, crops, cursor), kind_of(st.crop, crops))
            seasons.append(s)
            cursor = s.harvest + timedelta(days=config.MIN_GAP_DAYS)
        if st.cover_after:
            cv = annual_season(st.cover_after, crops, soil, next_plant(st.cover_after, crops, cursor), "cover")
            seasons.append(cv)
            cursor = cv.harvest + timedelta(days=config.MIN_GAP_DAYS)
        i += 1
    return seasons


def place_history(history: list[dict], crops: dict, soil: dict, start: date) -> list[Season]:
    """Seasons for the field's actual CDL crop history (year = harvest year). Fallow/other = bare."""
    seasons: list[Season] = []
    cursor = start
    prev = None
    for row in history:
        crop, y = row["crop"], row["year"]
        if crop in ("fallow", "other"):
            prev = crop
            continue
        if crop == "alfalfa":
            if prev == "alfalfa" and seasons and seasons[-1].crop == "alfalfa":
                blk = alfalfa_block(1, crops, soil, cursor)[1:]
                g = blk[0]
                # shift the production season to year y
                sd = crops["alfalfa"]["stage_days"]
                gp = _md(y, crops["alfalfa"]["harvest_window"]["start"]) - timedelta(days=sd["ini"] + sd["dev"])
                ends = _stage_ends(gp, sum(sd.values()), sd)
                g = Season("alfalfa", "alfalfa", gp, ends[-1], ends[-1], ends, revenue=True,
                           zr_start=g.zr_max, zr_max=g.zr_max, root_full=gp)
                seasons.append(g)
            else:
                blk = alfalfa_block(1, crops, soil, max(cursor, date(y - 1, 7, 1)))
                seasons.extend(blk)
            cursor = seasons[-1].harvest + timedelta(days=config.MIN_GAP_DAYS)
        else:
            earliest = date(y - 1, 7, 1) if crops[crop]["season"] == "winter" else date(y, 1, 1)
            s = annual_season(crop, crops, soil, next_plant(crop, crops, max(cursor, earliest)), kind_of(crop, crops))
            seasons.append(s)
            cursor = s.harvest + timedelta(days=config.MIN_GAP_DAYS)
        prev = crop
    return seasons


@dataclass
class Timeline:
    """Daily arrays aligned to `index`."""
    index: pd.DatetimeIndex
    state: np.ndarray        # BARE / GROW / COVER / DRY
    kc: np.ndarray
    zr: np.ndarray
    season: np.ndarray       # index into seasons, -1 if none
    stage: np.ndarray        # 0..3 on growing days of a season, -1 otherwise
    crop: np.ndarray         # crop name in the ground ("" if bare)
    p: np.ndarray            # FAO-56 depletion fraction of the crop in the ground
    seasons: list[Season]


def kc_curve(day: int, ends_off: list[int], kc: dict) -> float:
    """FAO-56 piecewise-linear Kc for day offset `day` from planting."""
    e_ini, e_dev, e_mid, e_late = ends_off
    if day < e_ini:
        return kc["ini"]
    if day < e_dev:
        return kc["ini"] + (kc["mid"] - kc["ini"]) * (day - e_ini) / max(1, e_dev - e_ini)
    if day < e_mid:
        return kc["mid"]
    return kc["mid"] + (kc["end"] - kc["mid"]) * (day - e_mid) / max(1, e_late - e_mid)


def build_timeline(seasons: list[Season], crops: dict, index: pd.DatetimeIndex) -> Timeline:
    n = len(index)
    t0 = index[0].date()
    state = np.zeros(n, dtype=np.int8)
    kc = np.zeros(n)
    zr = np.full(n, config.ROOT_INIT_M)
    sidx = np.full(n, -1, dtype=np.int32)
    stage = np.full(n, -1, dtype=np.int8)
    crop = np.full(n, "", dtype=object)
    pf = np.full(n, 0.55)

    def off(d: date) -> int:
        return (d - t0).days

    for k, s in enumerate(seasons):
        if s.kind == "fallow":
            continue
        a, g, h = max(0, off(s.plant)), min(n, off(s.end_growth)), min(n, off(s.harvest))
        if a >= n or h <= 0:
            continue
        c = crops[s.crop]
        crop[a:h] = s.crop
        pf[a:h] = c["p"] or 0.55
        if s.kind == "estab":
            state[a:h] = GROW
            kc[a:h] = c["kc"]["ini"]
            span = max(1, off(s.root_full) - off(s.plant))
            for i in range(a, h):
                zr[i] = min(s.zr_max, s.zr_start + (s.zr_max - s.zr_start) * (i - off(s.plant)) / span)
            continue
        ends_off = [off(e) - off(s.plant) for e in s.stage_ends]
        full = max(1, off(s.root_full) - off(s.plant))
        code = COVER if s.kind == "cover" else GROW
        for i in range(a, g):
            d = i - off(s.plant)
            state[i] = code
            kc[i] = kc_curve(d, ends_off, c["kc"])
            zr[i] = min(s.zr_max, s.zr_start + (s.zr_max - s.zr_start) * min(1.0, d / full))
            sidx[i] = k
            stage[i] = next((j for j, e in enumerate(ends_off) if d < e), 3)
        state[g:h] = DRY
        zr[g:h] = s.zr_max
        sidx[g:h] = -1
    # dormant alfalfa between production seasons (stand stays in the ground)
    for k, s in enumerate(seasons[:-1]):
        nxt = seasons[k + 1]
        if s.crop == "alfalfa" and nxt.crop == "alfalfa" and nxt.kind == "alfalfa":
            a, b = max(0, off(s.harvest)), min(n, off(nxt.plant))
            if a < b:
                state[a:b] = GROW
                kc[a:b] = config.ALFALFA_DORMANT_KC
                zr[a:b] = s.zr_max
                crop[a:b] = "alfalfa"
                pf[a:b] = crops["alfalfa"]["p"]
    return Timeline(index, state, kc, zr, sidx, stage, crop, pf, seasons)
