"""Handover 5.3 sanity checks on D's real data for all three fields, plus bucket unit checks."""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from model import config, inputs
from model.library.load_crops import load_crops
from model.library.rotations import LIBRARY, Rotation, Step, rotations_for_field
from model.replay import run as R
from model.replay.crop_calendar import (BARE, annual_season, build_timeline, kc_curve, next_plant, place_cycle,
                                        profile_depth)
from model.replay.economics import season_outcome
from model.replay.water_balance import run_bucket, scs_runoff

FIELDS = config.FIELD_IDS


@pytest.fixture(scope="module")
def crops():
    return load_crops()[0]


@pytest.fixture(scope="module")
def weather():
    return {fid: {cl: R.weather_for(fid, inputs.field(fid), cl) for cl in config.CLIMATE_IDS} for fid in FIELDS}


def _irrigable(fid: str) -> dict:
    """The field with a well, so irrigation physics can be checked on every soil."""
    return {**inputs.field(fid), "irrigated": True}


def _season_rel(rot_steps, crop, fid, crops, w, field, irrigate=False, cap="dryland"):
    rot = Rotation("T", tuple(rot_steps), irrigated=irrigate, min_cap="dryland")
    rels = []
    for tl in R.phase_timelines(rot, crops, field["soil"], w.df.index):
        df = w.df
        res = run_bucket(tl, df.et0_mm.to_numpy(), df.precip_mm.to_numpy(), field["soil"], config.CAP_MM[cap],
                         irrigate, profile_depth(field["soil"]))
        for k, s in enumerate(tl.seasons):
            if s.crop == crop and s.revenue and config.YEAR_FROM <= s.harvest_year <= config.YEAR_TO:
                o = season_outcome(s, k, crops, tl.season, tl.stage, res.eta, res.etc, df.tmax_c.to_numpy(),
                                   df.tmin_c.to_numpy(), "non_irrigated")
                rels.append(o["rel_yield"])
    return float(np.mean(rels))


@pytest.mark.parametrize("fid", FIELDS)
def test_et0_annual_range(fid, weather):
    df = weather[fid]["actual"].df.loc["2000":"2025"]
    annual = df.groupby(df.index.year)["et0_mm"].sum().mean()
    assert 1200 <= annual <= 1600, annual


@pytest.mark.parametrize("fid", FIELDS)
def test_irrigated_continuous_corn_cap450(fid, crops, weather):
    field = _irrigable(fid)
    rot = Rotation("T", (Step("corn"),), irrigated=True, min_cap="cap150")
    tables = [R.simulate(tl, weather[fid]["actual"], field, crops, "cap450", True, "irrigated")
              for tl in R.phase_timelines(rot, crops, field["soil"], weather[fid]["actual"].df.index)]
    irr = R.average_phases(tables)["irrigation_mm"].mean()
    assert 250 <= irr <= 500, f"{fid}: {irr:.0f} mm/yr"


def _double_crop_seasons(crops, soil, start, end):
    """Wheat, then sorghum planted MIN_GAP_DAYS after wheat harvest (no fallow window)."""
    seasons, cursor = [], start
    while cursor < end:
        wh = annual_season("wheat", crops, soil, next_plant("wheat", crops, cursor), "grain")
        so = annual_season("sorghum", crops, soil, wh.harvest + timedelta(days=config.MIN_GAP_DAYS), "grain")
        seasons += [wh, so]
        cursor = so.harvest + timedelta(days=config.MIN_GAP_DAYS)
    return seasons


def _rel_from_timeline(tl, crop, crops, w, field):
    df = w.df
    res = run_bucket(tl, df.et0_mm.to_numpy(), df.precip_mm.to_numpy(), field["soil"], 0.0, False,
                     profile_depth(field["soil"]))
    rels = [season_outcome(s, k, crops, tl.season, tl.stage, res.eta, res.etc, df.tmax_c.to_numpy(),
                           df.tmin_c.to_numpy(), "non_irrigated")["rel_yield"]
            for k, s in enumerate(tl.seasons)
            if s.crop == crop and s.revenue and config.YEAR_FROM <= s.harvest_year <= config.YEAR_TO]
    return float(np.mean(rels))


@pytest.mark.parametrize("fid", FIELDS)
def test_sorghum_better_after_fallow_than_after_wheat(fid, crops, weather):
    """Dryland W-S-F sorghum (planted after the 11-month fallow on wheat stubble) must clearly beat
    sorghum planted straight after wheat harvest, and must not lose to continuous sorghum."""
    field = inputs.field(fid)
    w = weather[fid]["actual"]
    wsf = _season_rel(list(LIBRARY["R2"].steps), "sorghum", fid, crops, w, field)
    dc = build_timeline(_double_crop_seasons(crops, field["soil"], date(1999, 10, 1), date(2025, 12, 31)), crops,
                        w.df.index)
    after_wheat = _rel_from_timeline(dc, "sorghum", crops, w, field)
    continuous = _season_rel([Step("sorghum")], "sorghum", fid, crops, w, field)
    print(fid, "wsf", round(wsf, 3), "double-crop", round(after_wheat, 3), "continuous", round(continuous, 3))
    # fallow storage pays most on soils that hold water; sands (f3, about 105 mm in 1.5 m) store little
    holds_water = field["soil"]["awc_mm_per_m"] >= 100
    assert wsf >= after_wheat + (0.05 if holds_water else 0.02), (wsf, after_wheat)
    assert wsf >= continuous + (0.03 if holds_water else 0.0), (wsf, continuous)


@pytest.mark.parametrize("fid", FIELDS)
def test_hotdry_raises_need_and_cuts_dryland_yield(fid, crops, weather):
    field = _irrigable(fid)
    for rid, rot in rotations_for_field(inputs.field(fid)).items():
        tls = R.phase_timelines(rot, crops, field["soil"], weather[fid]["actual"].df.index)
        out = {}
        for cl in config.CLIMATE_IDS:
            w = weather[fid][cl]
            dry = R.average_phases([R.simulate(tl, w, field, crops, "dryland", False, "non_irrigated") for tl in tls])
            out[cl] = dry["rel_yield"].mean()
            if rot.irrigated:
                # irrigation need: crop water demand left after rain, with no cap
                need = []
                for tl in tls:
                    res = run_bucket(tl, w.df.et0_mm.to_numpy(), w.df.precip_mm.to_numpy(), field["soil"], 1e9, True,
                                     profile_depth(field["soil"]))
                    need.append(res.irr.sum())
                out[cl + "_need"] = np.mean(need)
        assert out["hotdry"] < out["actual"], f"{fid} {rid} dryland rel_yield {out}"
        if rot.irrigated:
            for cap in ("cap150", "cap300", "cap450"):
                applied = {cl: R.average_phases([R.simulate(tl, weather[fid][cl], field, crops, cap, True, "irrigated")
                                                 for tl in tls])["irrigation_mm"].mean() for cl in config.CLIMATE_IDS}
                # at a binding cap both climates use it all; allow 1 mm (below output rounding)
                assert applied["hotdry"] >= applied["actual"] - 1.0, f"{fid} {rid} {cap} applied {applied}"
        if rot.irrigated:
            assert out["hotdry_need"] > out["actual_need"], f"{fid} {rid} need {out}"


def test_scs_runoff():
    assert scs_runoff(0, 85) == 0
    assert scs_runoff(5, 67) == 0                    # below initial abstraction
    q = scs_runoff(50.8, 85)                         # 2 in on CN 85: NEH 630 gives about 0.8 in
    assert 15 < q < 25, q


def test_kc_curve_shape():
    kc = {"ini": 0.3, "mid": 1.2, "end": 0.35}
    ends = [25, 65, 110, 140]
    assert kc_curve(0, ends, kc) == 0.3
    assert kc_curve(45, ends, kc) == pytest.approx(0.75)
    assert kc_curve(80, ends, kc) == 1.2
    assert kc_curve(139, ends, kc) == pytest.approx(0.35, abs=0.03)


@pytest.mark.parametrize("fid", FIELDS)
def test_bucket_mass_balance(fid, crops, weather):
    field = _irrigable(fid)
    w = weather[fid]["actual"]
    tl = R.phase_timelines(LIBRARY["R5"], crops, field["soil"], w.df.index)[0]
    zmax = profile_depth(field["soil"])
    p = w.df.precip_mm.to_numpy()
    res = run_bucket(tl, w.df.et0_mm.to_numpy(), p, field["soil"], 300, True, zmax)
    taw = field["soil"]["awc_mm_per_m"] * zmax
    water_in = (p - res.runoff).sum() + config.PIVOT_EFFICIENCY * res.irr.sum()
    water_out = res.eta.sum() + res.drain.sum()
    # storage change is bounded by the profile capacity
    assert abs(water_in - water_out) <= taw + 1e-6


def test_timeline_wsf_has_fallow_window(crops):
    soil = inputs.field("f2")["soil"]
    idx = pd.date_range(config.SPINUP_START, "2006-12-31")
    seasons = place_cycle(list(LIBRARY["R2"].steps), crops, soil, date(1999, 10, 1), date(2006, 12, 31))
    tl = build_timeline(seasons, crops, idx)
    crops_seq = [s.crop for s in seasons if s.kind != "fallow"][:4]
    assert crops_seq == ["wheat", "sorghum", "wheat", "sorghum"]
    # 3-year cycle: wheat harvest years step by 3
    wh = [s.harvest_year for s in seasons if s.crop == "wheat"]
    assert np.diff(wh[:3]).tolist() == [3, 3]
    assert (tl.state == BARE).mean() > 0.4
