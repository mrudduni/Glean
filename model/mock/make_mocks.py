"""Write schema-exact mock JSON (README 8.4) for every M file, f1-f3, with _meta.mock = true.

Run: python model/mock/make_mocks.py   (writes into model/out/web/)
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    _here = Path(__file__).resolve().parent
    sys.path[:] = [p for p in sys.path if Path(p or ".").resolve() != _here]
    sys.path.insert(0, str(_here.parents[1]))

from model import config
from model.contract import EVIDENCE_VARS, WHY_VARS, meta, write_json
from model.library.rotations import LIBRARY, Step

GEN = "model/mock/make_mocks.py"
ROT_IDS = ["R0", "R1", "R2", "R3", "R4", "R5"]
R0_STEPS = {"f1": [Step("corn")], "f2": [Step("wheat"), Step("sorghum"), Step("fallow")],
            "f3": [Step("corn"), Step("wheat"), Step("sorghum")]}
R0_CLASS = {"f1": "continuous_corn", "f2": "wsf", "f3": "corn_wheat_sorghum"}
CROP_NAMES = {
    "corn": ("Corn", "Maíz"), "sorghum": ("Sorghum", "Sorgo"), "wheat": ("Winter wheat", "Trigo de invierno"),
    "soybean": ("Soybean", "Soya"), "alfalfa": ("Alfalfa", "Alfalfa"), "triticale": ("Triticale (forage)", "Triticale (forraje)"),
    "rye_cover": ("Cereal rye cover", "Centeno de cobertura"), "cotton": ("Cotton", "Algodón"), "fallow": ("Fallow", "Barbecho"),
}


def m(schema: str) -> dict:
    return meta(schema, GEN, mock=True)


def mock_crops() -> dict:
    crops = {}
    for cid, (en, es) in CROP_NAMES.items():
        crops[cid] = {
            "name": {"en": en, "es": es}, "family": "poaceae", "host_group": cid, "season": "summer",
            "plant_window": {"start": "05-01", "end": "05-20"}, "harvest_window": {"start": "09-20", "end": "10-20"},
            "stage_days": {"ini": 25, "dev": 40, "mid": 45, "late": 30}, "kc": {"ini": 0.3, "mid": 1.1, "end": 0.4},
            "root_max_m": 1.5, "p": 0.55, "ky": 1.0, "heat": {"stage": "mid", "tmax_c": 35}, "frost_kill_c": -2,
            "requires_irrigation": False, "n_fixing": cid in ("soybean", "alfalfa"), "residue": "medium",
            "root_type": "fibrous", "forage": cid in ("alfalfa", "triticale"),
            "yield": {"nass_commodity": cid.upper(), "unit": "bu/ac", "irrigated_default": 100, "dryland_default": 50},
            "price": {"unit": "usd/bu", "default": 5.0}, "equipment": [], "sources": ["FAO-56 Table 12"],
        }
    return {"_meta": m("crops@1"), "crops": crops}


def mock_rotations() -> dict:
    return {"_meta": m("rotations@1"), "rotations": [r.as_json() for r in LIBRARY.values()]}


def mock_summary(fid: str) -> dict:
    stats = lambda d: {"frost_free_days": 170 + d, "last_spring_frost": "04-25", "first_fall_frost": "10-12",
                       "gdd_base10_c": 1950 + 10 * d, "precip_mm_yr": 480 - d, "days_tmax_ge_35": 18 + d,
                       "et0_mm_yr": 1450 + d}
    return {
        "_meta": m("summary@1"), "field_id": fid,
        "current_rotation": {"steps": [s.as_json() for s in R0_STEPS[fid]], "rotation_class": R0_CLASS[fid],
                             "years": [2018, 2025]},
        "climate": {"normal": stats(0), "recent": stats(6), "normal_period": "1991-2020",
                    "recent_period": "2016-2025", "sources": ["PRISM", "POWER"]},
        "water": {"grace_trend_cm_per_yr": -0.9, "wells_trend_m_per_yr": 0.5, "outlook": "declining"},
        "headline_facts": [
            {"text_id": "grace_trend", "vars": {"cm_per_yr": -0.9}, "sources": ["GRACE"]},
            {"text_id": "heat_days_change", "vars": {"days": 6}, "sources": ["PRISM"]},
            {"text_id": "current_rotation", "vars": {"years_from": 2018, "years_to": 2025}, "sources": ["CSB"]},
        ],
    }


def mock_calendar(fid: str, rng: random.Random) -> dict:
    risk = [{"month": mo, "p_heat": round(0.8 if mo in (6, 7, 8) else 0.0, 2),
             "p_frost": round(0.9 if mo in (1, 2, 3, 4, 10, 11, 12) else 0.0, 2),
             "p_dry_spell": round(rng.uniform(0.2, 0.6), 2), "storm_days": round(1.5 if 5 <= mo <= 8 else 0.3, 2),
             "windy_days": round(6.0 if mo in (3, 4, 5) else 2.5, 2)} for mo in range(1, 13)]
    rots = []
    for rid in ROT_IDS + ["R6"]:
        steps = R0_STEPS[fid] if rid == "R0" else list(LIBRARY[rid].steps)
        years = []
        for i, st in enumerate(steps):
            cells = []
            for mo in range(1, 13):
                grow = 5 <= mo <= 9 and st.crop != "fallow"
                cells.append({"state": st.crop if grow else "bare",
                              "stage": ["ini", "dev", "mid", "mid", "late"][mo - 5] if grow else None,
                              "flags": (["heat"] if grow and mo == 7 else []) + ([] if grow else ["bare_wind"] if mo in (3, 4) else [])})
            years.append({"year_index": i + 1, "months": cells})
        rots.append({"rotation_id": rid, "years": years})
    return {"_meta": m("calendar@1"), "field_id": fid, "climate_risk": risk, "rotations": rots}


def _run(rng: random.Random, irrig: float, rev: float, feasible: bool) -> dict:
    by_year = []
    for y in range(config.YEAR_FROM, config.YEAR_TO + 1):
        dry = y in (2002, 2011, 2012, 2022)
        by_year.append({
            "year": y, "crop_mix": {"corn": 0.5, "wheat": 0.5},
            "irrigation_mm": round(irrig * (1.3 if dry else rng.uniform(0.8, 1.1))),
            "eta_mm": round(rng.uniform(450, 650)), "etc_mm": round(rng.uniform(600, 750)),
            "stress_days": round(rng.uniform(5, 40) * (2 if dry else 1)),
            "rel_yield": round(rng.uniform(0.5, 0.95) * (0.6 if dry else 1), 2),
            "revenue_usd_ac": round(rev * (0.5 if dry else rng.uniform(0.85, 1.1))),
            "bare_days": round(rng.uniform(120, 220)), "water_erosion_idx": round(rng.uniform(0, 3), 2),
            "wind_erosion_idx": round(rng.uniform(0, 8), 2), "heat_days": round(rng.uniform(0, 8)),
            "frost_events": int(rng.random() < 0.1),
        })
    revs = sorted(r["revenue_usd_ac"] for r in by_year)
    mean = lambda k: sum(r[k] for r in by_year) / len(by_year)
    summary = {
        "irrigation_mm_mean": round(mean("irrigation_mm")), "eta_mm_mean": round(mean("eta_mm")),
        "stress_days_mean": round(mean("stress_days")), "rel_yield_mean": round(mean("rel_yield"), 2),
        "revenue_usd_ac_mean": round(mean("revenue_usd_ac")), "revenue_usd_ac_worst5": round(sum(revs[:5]) / 5),
        "bare_days_mean": round(mean("bare_days")), "bare_storm_days_mean": round(rng.uniform(2, 8)),
        "bare_windy_days_mean": round(rng.uniform(10, 50)), "water_erosion_idx": round(mean("water_erosion_idx"), 2),
        "wind_erosion_idx": round(mean("wind_erosion_idx"), 2), "heat_days_mean": round(mean("heat_days")),
        "frost_events_total": sum(r["frost_events"] for r in by_year),
    }
    return {"feasible": feasible, "summary": summary, "by_year": by_year}


BASE = {"R0": (380, 520), "R1": (220, 430), "R2": (0, 210), "R3": (0, 260), "R4": (520, 610), "R5": (260, 450)}
MIN_CAP = {"R0": "cap150", "R1": "cap150", "R2": "dryland", "R3": "dryland", "R4": "cap300", "R5": "dryland"}


def mock_replay(fid: str, rng: random.Random) -> dict:
    scen = {}
    for sk in config.SCENARIOS:
        cap = sk.split("|")[0]
        frac = config.CAP_MM[cap] / 450
        scen[sk] = {rid: _run(rng, BASE[rid][0] * frac, BASE[rid][1], config.CAP_IDS.index(cap) >= config.CAP_IDS.index(MIN_CAP[rid]))
                    for rid in ROT_IDS}
    return {"_meta": m("replay@1"), "field_id": fid, "years": [config.YEAR_FROM, config.YEAR_TO],
            "drought_years": [2002, 2011, 2012, 2022], "scenarios": scen}


def mock_strategies(fid: str, replay: dict) -> dict:
    scen = {}
    for sk, runs in replay["scenarios"].items():
        r0 = runs["R0"]["summary"]
        entries = []
        for rid in ROT_IDS:
            s = runs[rid]["summary"]
            vals = {
                "water_use": {"irrigation_mm": s["irrigation_mm_mean"], "saved_mm": r0["irrigation_mm_mean"] - s["irrigation_mm_mean"]},
                "income_mean": {"revenue_usd_ac": s["revenue_usd_ac_mean"], "diff_usd_ac": s["revenue_usd_ac_mean"] - r0["revenue_usd_ac_mean"]},
                "income_worst": {"worst5_usd_ac": s["revenue_usd_ac_worst5"], "r0_worst5_usd_ac": r0["revenue_usd_ac_worst5"]},
                "soil_health": {"score": 55, "living_root_days": 190, "legume_years": 0},
                "water_erosion": {"bare_storm_days": s["bare_storm_days_mean"], "r0_bare_storm_days": r0["bare_storm_days_mean"]},
                "wind_erosion": {"bare_windy_days": s["bare_windy_days_mean"], "r0_bare_windy_days": r0["bare_windy_days_mean"]},
                "pest_break": {"max_run_years": 1 if rid != "R0" else 8, "r0_max_run_years": 8},
                "heat_frost_risk": {"heat_days": s["heat_days_mean"], "r0_heat_days": r0["heat_days_mean"]},
            }
            assert set(vals) == set(WHY_VARS)
            criteria = {k: {"raw": float(list(v.values())[0]), "unit": "mock", "norm": round(50 + 7 * ROT_IDS.index(rid) % 50, 2), "vars": v}
                        for k, v in vals.items()}
            feasible = runs[rid]["feasible"]
            ev = {"replay_avg": {"years_from": 2000, "years_to": 2025, "irrigation_mm": s["irrigation_mm_mean"],
                                 "revenue_usd_ac": s["revenue_usd_ac_mean"]}}
            assert set(ev["replay_avg"]) == set(EVIDENCE_VARS["replay_avg"])
            rot = LIBRARY.get(rid)
            entries.append({
                "rotation_id": rid, "feasible": feasible,
                "infeasible_reason_id": None if feasible else "needs_more_water",
                "criteria": criteria,
                "requires_equipment": list(rot.requires_equipment) if rot else [],
                "needs_forage_market": rot.needs_forage_market if rot else False,
                "crops_without_local_market": ["triticale"] if rid == "R3" else [],
                "benefits": [] if rid == "R0" else [{"text_id": "water_saved", "vars": {"saved_mm": 120}}],
                "evidence": [{"text_id": "replay_avg", "vars": ev["replay_avg"], "sources": ["MODEL", "POWER", "SSURGO"]}],
                "gap_ids": ["model_simplified", "costs_not_modelled", "prices_constant", "crop_params_generic"],
                "risk_ids": ["water_rights"] if rot and rot.irrigated else [],
                "confidence": "limited",
            })
        scen[sk] = entries
    return {"_meta": m("strategies@1"), "field_id": fid, "scenarios": scen}


def mock_validation(fid: str) -> dict:
    return {"_meta": m("validation@1"), "field_id": fid, "items": [
        {"id": "et_vs_openet", "metric": "bias_pct", "value": -12.0, "n": 56, "level": "fair",
         "vars": {"bias_pct": -12.0}, "sources": ["MODEL", "OpenET"]},
        {"id": "precip_power_vs_imerg", "metric": "bias_pct", "value": 6.0, "n": 300, "level": "good",
         "vars": {"bias_pct": 6.0}, "sources": ["POWER", "IMERG"]},
    ]}


def mock_context(fid: str) -> dict:
    return {"_meta": m("assistant_context@1"), "field_id": fid, "field_name": f"Mock field {fid}", "facts": [
        {"id": "field.area_ac", "text": "The field covers about 130 acres.", "value": 130, "unit": "ac", "source": "CSB"},
        {"id": "replay.R0.cap300|actual.irrigation_mm_mean", "text": "Under the current rotation the model estimates 380 mm of irrigation a year.",
         "value": 380, "unit": "mm", "source": "MODEL", "scenario": "cap300|actual", "rotation_id": "R0"},
    ]}


def mock_cache(fid: str) -> dict:
    ans = {"answer_md": "This is a mock answer. The model estimates 380 mm of irrigation a year [MODEL].",
           "citations": [{"tag": "MODEL", "name": "Field Shift model", "url": "https://github.com/mrudduni/Team-Brackets"}],
           "numbers": [{"text": "380 mm", "value": 380, "unit": "mm", "verified": True,
                        "fact_id": "replay.R0.cap300|actual.irrigation_mm_mean"}],
           "cached": True, "provider": "cache", "model": None}
    return {"_meta": m("assistant_cache@1"), "field_id": fid, "scenario": "cap300|actual",
            "answers": {f"q{i}": {"en": ans, "es": ans} for i in range(1, 7)}}


def mock_prompt() -> dict:
    return {"_meta": m("prompt@1"), "version": "mock-1",
            "system": "Mock prompt for {field_name} in {lang_name}. Scenario: {scenario_label}. Top: {top_rotations}.\nFACTS:\n{facts_block}",
            "temperature": 0.2, "max_tokens": 600}


def main(out: Path = config.OUT_DIR, include_assistant: bool = True) -> None:
    rng = random.Random(7)
    write_json(out / "crops.json", mock_crops())
    write_json(out / "rotations.json", mock_rotations())
    if include_assistant:
        write_json(out / "assistant" / "prompt.json", mock_prompt())
    for fid in config.FIELD_IDS:
        d = out / "field" / fid
        replay = mock_replay(fid, rng)
        write_json(d / "summary.json", mock_summary(fid))
        write_json(d / "calendar.json", mock_calendar(fid, rng))
        write_json(d / "replay.json", replay)
        write_json(d / "strategies.json", mock_strategies(fid, replay))
        write_json(d / "validation.json", mock_validation(fid))
        if include_assistant:
            write_json(d / "assistant_context.json", mock_context(fid))
            write_json(d / "assistant_cache.json", mock_cache(fid))
    print(f"mocks written to {out}")


if __name__ == "__main__":
    main()
