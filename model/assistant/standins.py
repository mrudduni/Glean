"""README-shaped stand-ins for model-core files, used until the real ones land.

Writes summary, replay, strategies, validation and rotations with _meta.mock = true.
Numbers are plausible but invented. Never ship them as results.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CAPS = {"dryland": 0, "cap150": 150, "cap300": 300, "cap450": 450}
CLIMATES = ["actual", "hotdry"]
ROT = {
    "R1": ["corn", "wheat", "sorghum"],
    "R2": ["wheat", "sorghum", "fallow"],
    "R3": ["wheat", "sorghum", "triticale"],
    "R4": ["alfalfa", "corn", "wheat"],
    "R5": ["corn", "soybean", "wheat"],
}
BASE_IRR = {"R0": 260, "R1": 240, "R2": 60, "R3": 90, "R4": 420, "R5": 230}
BASE_REV = {"R0": 520, "R1": 480, "R2": 210, "R3": 260, "R4": 560, "R5": 430}
META = {"mock": True, "generator": "model/assistant/standins.py", "generated_at": "2026-11-15T00:00:00Z"}


def meta(name):
    return {"schema": f"{name}@1", **META}


def write(path: Path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf8")


def make(out: Path, fields: dict[str, bool]):
    write(out / "rotations.json", {"_meta": meta("rotations"), "rotations": [
        {"id": r, "steps": [{"crop": c, "cover_after": None} for c in s],
         "irrigated": r in ("R1", "R4", "R5"), "min_cap": "cap150" if r in ("R1", "R4", "R5") else "dryland",
         "requires_equipment": ["hay"] if r == "R4" else [], "needs_forage_market": r in ("R3", "R4"),
         "tier": "must"} for r, s in ROT.items()]})
    for fid, irrigated in fields.items():
        d = out / "field" / fid
        scen = {}
        strat = {}
        for cap, capmm in CAPS.items():
            for cl in CLIMATES:
                k = f"{cap}|{cl}"
                hot = cl == "hotdry"
                runs, entries = {}, []
                for r in ["R0", *ROT]:
                    feas = not (capmm == 0 and r in ("R1", "R4", "R5", "R0") and irrigated is True and r != "R0")
                    if capmm == 0 and r in ("R1", "R4", "R5"):
                        feas = False
                    irr = min(BASE_IRR[r], capmm) * (1.08 if hot else 1) if feas else 0
                    rev = BASE_REV[r] * (0.82 if hot else 1) * (0.7 + 0.3 * min(1, capmm / 300 + 0.4))
                    if not irrigated:
                        rev *= 0.75
                    runs[r] = {"feasible": feas, "summary": {
                        "irrigation_mm_mean": round(irr), "eta_mm_mean": round(430 + irr * 0.8),
                        "stress_days_mean": round((18 if r != "R2" else 9) * (1.5 if hot else 1) * (1.4 - capmm / 900)),
                        "rel_yield_mean": 0.8, "revenue_usd_ac_mean": round(rev),
                        "revenue_usd_ac_worst5": round(rev * 0.55),
                        "bare_days_mean": 120 if r == "R2" else 60, "bare_storm_days_mean": 3,
                        "bare_windy_days_mean": 14 if r == "R2" else 6, "water_erosion_idx": 0.3, "wind_erosion_idx": 0.4,
                        "heat_days_mean": 12 if not hot else 22, "frost_events_total": 6}, "by_year": [
                        {"year": y, "irrigation_mm": round(irr * (1.3 if y == 2012 else 1)),
                         "revenue_usd_ac": round(rev * (0.5 if y == 2012 else 1)), "stress_days": 30 if y == 2012 else 12}
                        for y in (2002, 2011, 2012, 2022)]}
                    entries.append({"rotation_id": r, "feasible": feas,
                                    "infeasible_reason_id": None if feas else "needs_irrigation",
                                    "criteria": {"soil_health": {"raw": 62 if r in ("R5", "R4") else 41, "unit": "index", "norm": 60, "vars": {}}}})
                scen[k] = runs
                strat[k] = entries
        write(d / "replay.json", {"_meta": meta("replay"), "field_id": fid, "years": [2000, 2025],
                                  "drought_years": [2002, 2011, 2012, 2022], "scenarios": scen})
        write(d / "strategies.json", {"_meta": meta("strategies"), "field_id": fid, "scenarios": strat})
        write(d / "validation.json", {"_meta": meta("validation"), "field_id": fid, "items": [
            {"id": "et_vs_openet", "metric": "bias_pct", "value": -7, "n": 72, "level": "good", "vars": {}, "sources": ["OpenET", "FAO56"]},
            {"id": "sm_vs_smap", "metric": "r", "value": 0.61, "n": 900, "level": "fair", "vars": {}, "sources": ["SMAP"]},
            {"id": "precip_power_vs_imerg", "metric": "r", "value": 0.83, "n": 300, "level": "good", "vars": {}, "sources": ["POWER", "IMERG"]}]})
        write(d / "summary.json", {"_meta": meta("summary"), "field_id": fid,
            "current_rotation": {"steps": [{"crop": c, "cover_after": None} for c in (["corn"] if irrigated else ["wheat", "sorghum", "fallow"])],
                                 "rotation_class": "continuous_corn" if irrigated else "wsf", "years": [2016, 2024]},
            "climate": {"normal": {"frost_free_days": 178, "last_spring_frost": "04-18", "first_fall_frost": "10-14", "gdd_base10_c": 2650, "precip_mm_yr": 485, "days_tmax_ge_35": 38, "et0_mm_yr": 1620},
                        "recent": {"frost_free_days": 184, "last_spring_frost": "04-14", "first_fall_frost": "10-16", "gdd_base10_c": 2760, "precip_mm_yr": 470, "days_tmax_ge_35": 45, "et0_mm_yr": 1680},
                        "normal_period": "1991-2020", "recent_period": "2016-2025", "sources": ["PRISM", "POWER"]},
            "water": {"grace_trend_cm_per_yr": -0.86, "wells_trend_m_per_yr": -0.4, "outlook": "declining"}, "headline_facts": []})


if __name__ == "__main__":
    make(Path(sys.argv[1]), {"f1": True, "f2": False, "f3": True})
