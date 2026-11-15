"""Raw criteria per field x scenario x rotation, and 0-100 normalisation (handover 5.5)."""
from __future__ import annotations

from model import config
from model.library.rotations import Rotation

LOWER_IS_BETTER = {"water_use", "water_erosion", "wind_erosion", "pest_break", "heat_frost_risk"}
UNITS = {"water_use": "mm", "income_mean": "usd_ac", "income_worst": "usd_ac", "soil_health": "index",
         "water_erosion": "index", "wind_erosion": "index", "pest_break": "years", "heat_frost_risk": "days"}


def cycle_crops(rot: Rotation) -> list[str]:
    """Main crops and covers in one cycle (fallow excluded)."""
    out = []
    for s in rot.steps:
        if s.crop != "fallow":
            out.append(s.crop)
        if s.cover_after:
            out.append(s.cover_after)
    return out


def max_host_run(rot: Rotation, crops: dict) -> int:
    """Longest run of the same host_group in the cycled main-crop sequence (fallow breaks a run), cap 8."""
    groups = [crops[s.crop]["host_group"] if s.crop != "fallow" else None for s in rot.steps]
    if len(set(groups)) == 1 and groups[0] is not None:
        return config.PEST_RUN_CAP
    seq = groups * 3
    best = run = 0
    prev = object()
    for g in seq:
        run = run + 1 if g is not None and g == prev else (1 if g is not None else 0)
        prev = g
        best = max(best, run)
    return min(best, config.PEST_RUN_CAP)


def legume_years(rot: Rotation, crops: dict) -> int:
    return sum(1 for s in rot.steps if s.crop != "fallow" and crops[s.crop]["n_fixing"])


def soil_health(rot: Rotation, crops: dict, summary: dict) -> dict:
    steps = rot.steps
    residue = [config.RESIDUE_SCORE["none" if s.crop == "fallow" else crops[s.crop]["residue"]] for s in steps]
    families = {crops[c]["family"] for c in cycle_crops(rot) if crops[c]["family"]}
    living = summary["living_root_days_mean"]
    bare = summary["bare_days_mean"]
    w = config.SOIL_W
    score = (w["living_root"] * min(1.0, living / 365) + w["residue"] * sum(residue) / len(residue)
             + w["legume"] * legume_years(rot, crops) / len(steps)
             + w["families"] * min(1.0, len(families) / config.FAMILIES_FULL)
             + w["not_bare"] * max(0.0, 1 - bare / 365))
    return {"score": score, "living_root_days": living, "legume_years": legume_years(rot, crops),
            "families": len(families)}


def raw_criteria(rot: Rotation, crops: dict, summary: dict) -> dict:
    sh = soil_health(rot, crops, summary)
    return {
        "water_use": summary["irrigation_mm_mean"],
        "income_mean": summary["revenue_usd_ac_mean"],
        "income_worst": summary["revenue_usd_ac_worst5"],
        "soil_health": sh["score"],
        "water_erosion": summary["water_erosion_idx"],
        "wind_erosion": summary["wind_erosion_idx"],
        "pest_break": float(max_host_run(rot, crops)),
        "heat_frost_risk": summary["heat_days_mean"] + config.FROST_WEIGHT * summary["frost_events_total"] / config.N_YEARS,
    }, sh


def normalise(raws: dict[str, dict], feasible: dict[str, bool]) -> dict[str, dict]:
    """norm 0-100 per criterion across feasible rotations; infeasible ones get the norm they'd have had."""
    out = {rid: {} for rid in raws}
    for k in config.CRITERIA:
        pool = [raws[r][k] for r in raws if feasible[r]] or [raws[r][k] for r in raws]
        hi, lo = max(pool), min(pool)
        best, worst = (lo, hi) if k in LOWER_IS_BETTER else (hi, lo)
        for rid, raw in raws.items():
            if abs(best - worst) < 1e-9:
                n = 50.0
            else:
                n = 100.0 * (raw[k] - worst) / (best - worst)
            out[rid][k] = max(0.0, min(100.0, n))
    return out


def default_score(norms: dict[str, float], weights: dict[str, float] | None = None) -> float:
    """README 8.7 score under slider weights (default 3 each)."""
    weights = weights or config.SLIDER_DEFAULT
    wk = {c: 0.0 for c in config.CRITERIA}
    for slider, val in weights.items():
        for c, share in config.SLIDER_SHARES[slider].items():
            wk[c] += val * share
    tot = sum(wk.values()) or 1.0
    return sum(wk[c] * norms[c] for c in config.CRITERIA) / tot
