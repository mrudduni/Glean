"""Card facts per field x scenario x rotation -> strategies.json (handover 5.5, CONTRACT 8.4)."""
from __future__ import annotations

from model import config
from model.contract import BENEFIT_VARS, EVIDENCE_VARS, GAP_IDS, RISK_IDS, WHY_VARS, meta, write_json
from model.library.load_crops import yields_not_county
from model.library.rotations import Rotation
from model.scoring.criteria import (UNITS, cycle_crops, default_score, legume_years, max_host_run, normalise,
                                    raw_criteria)

RAW_ROUND = {"water_use": 0, "income_mean": 0, "income_worst": 0, "soil_health": 2, "water_erosion": 2,
             "wind_erosion": 2, "pest_break": 0, "heat_frost_risk": 2}


def _i(x) -> int:
    return int(round(float(x)))


def _num(x, nd):
    v = round(float(x), nd)
    return int(v) if nd == 0 else v


def neighbor_groups(nb: dict | None) -> tuple[dict, dict | None]:
    if not nb:
        return {}, None
    by_rot = {g["matches_rotation"]: g for g in nb["groups"] if g["matches_rotation"]}
    current = next((g for g in nb["groups"] if g["is_current"]), None)
    return by_rot, current


def why_vars(rid: str, s: dict, r0: dict, sh: dict, run: int, r0_run: int) -> dict:
    v = {
        "water_use": {"irrigation_mm": _i(s["irrigation_mm_mean"]), "saved_mm": _i(r0["irrigation_mm_mean"]) - _i(s["irrigation_mm_mean"])},
        "income_mean": {"revenue_usd_ac": _i(s["revenue_usd_ac_mean"]), "diff_usd_ac": _i(s["revenue_usd_ac_mean"]) - _i(r0["revenue_usd_ac_mean"])},
        "income_worst": {"worst5_usd_ac": _i(s["revenue_usd_ac_worst5"]), "r0_worst5_usd_ac": _i(r0["revenue_usd_ac_worst5"])},
        "soil_health": {"score": round(sh["score"], 1), "living_root_days": _i(sh["living_root_days"]), "legume_years": sh["legume_years"]},
        "water_erosion": {"bare_storm_days": _i(s["bare_storm_days_mean"]), "r0_bare_storm_days": _i(r0["bare_storm_days_mean"])},
        "wind_erosion": {"bare_windy_days": _i(s["bare_windy_days_mean"]), "r0_bare_windy_days": _i(r0["bare_windy_days_mean"])},
        "pest_break": {"max_run_years": run, "r0_max_run_years": r0_run},
        "heat_frost_risk": {"heat_days": _i(s["heat_days_mean"]), "r0_heat_days": _i(r0["heat_days_mean"])},
    }
    for k in v:
        assert list(v[k]) == WHY_VARS[k], k
    return v


def benefits(rot: Rotation, r0_rot: Rotation, s: dict, r0: dict, crops: dict) -> list[dict]:
    if rot.id == "R0":
        return []
    out = []
    saved = _i(r0["irrigation_mm_mean"]) - _i(s["irrigation_mm_mean"])
    if saved >= config.BENEFIT_WATER_MM:
        out.append({"text_id": "water_saved", "vars": {"saved_mm": saved}})
    fewer_bare = _i(r0["bare_days_mean"]) - _i(s["bare_days_mean"])
    if fewer_bare >= config.BENEFIT_BARE_DAYS:
        out.append({"text_id": "bare_days_reduced", "vars": {"days": fewer_bare}})
    if legume_years(rot, crops) > legume_years(r0_rot, crops):
        out.append({"text_id": "legume_added", "vars": {"legume_years": legume_years(rot, crops), "cycle_years": len(rot.steps)}})
    gain = _i(s["revenue_usd_ac_worst5"]) - _i(r0["revenue_usd_ac_worst5"])
    if gain >= config.BENEFIT_WORST5_USD:
        out.append({"text_id": "income_steadier", "vars": {"worst5_gain_usd_ac": gain}})
    run = max_host_run(rot, crops)
    if run < max_host_run(r0_rot, crops):
        out.append({"text_id": "pest_cycle_broken", "vars": {"max_run_years": run}})
    forage = next((c for c in cycle_crops(rot) if crops[c]["forage"]), None)
    if forage:
        out.append({"text_id": "forage_income", "vars": {"forage_crop": forage}})
    for b in out:
        assert list(b["vars"]) == BENEFIT_VARS[b["text_id"]]
    return out


def risks(rot: Rotation, r0_rot: Rotation, crops: dict, market: dict) -> tuple[list[str], list[str]]:
    ids: list[str] = []
    seq = [s.crop for s in rot.steps]
    pairs = list(zip(seq, seq[1:] + seq[:1]))
    if ("wheat", "sorghum") in pairs:
        ids.append("herbicide_carryover")
    no_market = sorted({c for c in seq if c in market and not market[c]})
    if no_market:
        ids.append("buyer_availability")
    r0_crops = set(cycle_crops(r0_rot))
    new = [c for c in cycle_crops(rot) if c not in r0_crops]
    if new:
        ids.append("seed_availability")
        if any(crops[c]["season"] != "cover" for c in new):
            ids.append("crop_insurance")
        if "cotton" in new:
            ids.append("new_crop_learning")
    if "alfalfa" in seq:
        ids.append("alfalfa_stand_water")
    if "fallow" in seq:
        ids.append("fallow_wind")
    if "rye_cover" in cycle_crops(rot):
        ids.append("cover_establishment")
    if rot.irrigated:
        ids.append("water_rights")
    if rot.requires_equipment:
        ids.append("equipment_access")
    assert all(i in RISK_IDS for i in ids)
    return ids, no_market


def build_strategies(fid: str, result: dict, rotations: dict[str, Rotation], crops: dict, prov: dict,
                     nb: dict | None, validation: dict) -> dict:
    by_rot, current = neighbor_groups(nb)
    et_item = next((i for i in validation["items"] if i["id"] == "et_vs_openet"), None)
    r0_rot = rotations["R0"]
    wdy = result["worst_drought_year"]
    scen_out = {}
    for sk, runs in result["scenarios"].items():
        raws, shs, feas = {}, {}, {}
        for rid, rot in rotations.items():
            raws[rid], shs[rid] = raw_criteria(rot, crops, runs[rid]["summary"])
            feas[rid] = runs[rid]["feasible"]
        norms = normalise(raws, feas)
        r0 = runs["R0"]["summary"]
        r0_run = max_host_run(r0_rot, crops)
        entries = []
        for rid, rot in rotations.items():
            run = runs[rid]
            s = run["summary"]
            vars_ = why_vars(rid, s, r0, shs[rid], max_host_run(rot, crops), r0_run)
            criteria = {k: {"raw": _num(raws[rid][k], RAW_ROUND[k]), "unit": UNITS[k], "norm": round(norms[rid][k], 2),
                            "vars": vars_[k]} for k in config.CRITERIA}
            evidence = [{"text_id": "replay_avg", "vars": {"years_from": config.YEAR_FROM, "years_to": config.YEAR_TO,
                                                           "irrigation_mm": _i(s["irrigation_mm_mean"]),
                                                           "revenue_usd_ac": _i(s["revenue_usd_ac_mean"])},
                         "sources": ["MODEL", "POWER", "SSURGO", "NASS"]}]
            if wdy is not None:
                yr = run["years"].loc[wdy]
                r0y = runs["R0"]["years"].loc[wdy]
                evidence.append({"text_id": "replay_drought", "vars": {"year": wdy, "irrigation_mm": _i(yr["irrigation_mm"]),
                                                                       "r0_irrigation_mm": _i(r0y["irrigation_mm"])},
                                 "sources": ["MODEL", "POWER"]})
            grp = current if rid == "R0" else by_rot.get(rid)
            has_nb = bool(grp and current and grp["n"] >= config.NEIGHBOR_MIN_N
                          and grp["et_mm_yr_median"] is not None and current["et_mm_yr_median"] is not None)
            if has_nb:
                evidence.append({"text_id": "neighbors", "vars": {"n": grp["n"], "et_mm": _i(grp["et_mm_yr_median"]),
                                                                  "r0_et_mm": _i(current["et_mm_yr_median"])},
                                 "sources": ["OpenET", "CSB"]})
            if et_item:
                evidence.append({"text_id": "validation_et", "vars": {"bias_pct": et_item["vars"]["bias_pct"]},
                                 "sources": ["MODEL", "OpenET"]})
            for e in evidence:
                assert list(e["vars"]) == EVIDENCE_VARS[e["text_id"]]

            gaps = ["model_simplified", "costs_not_modelled", "prices_constant", "crop_params_generic"]
            wk_norm = _why_rank(norms[rid])
            if "pest_break" in wk_norm:
                gaps.append("no_pest_data")
            if yields_not_county(prov, [c for c in cycle_crops(rot)]):
                gaps.append("county_yields")
            if et_item:
                gaps.append("openet_record_short")
            if has_nb:
                gaps.append("neighbors_observational")
            assert all(g in GAP_IDS for g in gaps)

            risk_ids, no_market = risks(rot, r0_rot, crops, prov["local_market"])
            et_good = bool(et_item and et_item["level"] == "good")
            confidence = "good" if (et_good and has_nb) else "fair" if (et_good or has_nb) else "limited"
            entries.append({
                "rotation_id": rid, "feasible": run["feasible"],
                "infeasible_reason_id": None if run["feasible"] else "needs_more_water",
                "criteria": criteria,
                "requires_equipment": list(rot.requires_equipment), "needs_forage_market": rot.needs_forage_market,
                "crops_without_local_market": no_market,
                "benefits": benefits(rot, r0_rot, s, r0, crops), "evidence": evidence,
                "gap_ids": gaps, "risk_ids": risk_ids, "confidence": confidence,
            })
        scen_out[sk] = entries
    return {"_meta": meta("strategies@1", "model/scoring/facts.py"), "field_id": fid, "scenarios": scen_out}


def _why_rank(norm: dict) -> list[str]:
    """CONTRACT 8.7 why bullets under default weights: top 3 by w_k x norm_k with norm >= 50."""
    wk = {c: 0.0 for c in config.CRITERIA}
    for slider, val in config.SLIDER_DEFAULT.items():
        for c, share in config.SLIDER_SHARES[slider].items():
            wk[c] += val * share
    ranked = sorted((c for c in config.CRITERIA if norm[c] >= 50), key=lambda c: -wk[c] * norm[c])
    return ranked[:3]


def top3(strategies_entries: list[dict], rotations: dict[str, Rotation], owned=(), forage_buyer=False) -> list[tuple[str, float]]:
    """CONTRACT 8.7 'shown' set under default sliders, excluding R0. Used for acceptance checks."""
    scored = []
    for e in strategies_entries:
        rid = e["rotation_id"]
        if rid == "R0":
            continue
        rot = rotations[rid]
        excluded = (not e["feasible"]) or not set(rot.requires_equipment) <= set(owned) or (rot.needs_forage_market and not forage_buyer)
        if excluded:
            continue
        norms = {k: v["norm"] for k, v in e["criteria"].items()}
        scored.append((rid, default_score(norms), e["criteria"]["water_use"]["raw"]))
    scored.sort(key=lambda t: (-t[1], t[2]))
    return [(r, round(float(s), 1)) for r, s, _ in scored[:3]]


def write_strategies(fid: str, payload: dict) -> None:
    write_json(config.OUT_DIR / "field" / fid / "strategies.json", payload)
