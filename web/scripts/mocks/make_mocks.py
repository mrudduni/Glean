"""Write README-shaped mock files (mock: true) for every M and U file the web app reads.

Stand-ins only, until role/model and role/content deliver. D's real files must already be in
web/public/data (fields.json, water.json, observed.json, neighbors.json). Daily weather comes from
origin/role/data so climate odds, drought years and heat days follow the real POWER record.

Run from web/:  python scripts/mocks/make_mocks.py  &&  node scripts/mocks/make_cache.mts
"""
from __future__ import annotations

import csv
import io
import json
import math
import subprocess
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

WEB = Path(__file__).resolve().parents[2]
DATA = WEB / "public" / "data"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
FIELDS = ["f1", "f2", "f3"]
CAPS = ["dryland", "cap150", "cap300", "cap450"]
CAP_MM = {"dryland": 0, "cap150": 150, "cap300": 300, "cap450": 450}
CLIMATES = ["actual", "hotdry"]
SCENARIOS = [f"{c}|{k}" for c in CAPS for k in CLIMATES]
YEARS = list(range(2000, 2026))
CRITERIA = ["water_use", "income_mean", "income_worst", "soil_health", "water_erosion", "wind_erosion", "pest_break", "heat_frost_risk"]


def meta(name: str) -> dict:
    return {"schema": f"{name}@1", "mock": True, "generated_at": NOW, "generator": "web/scripts/mocks/make_mocks.py"}


def write(rel: str, payload: dict) -> None:
    path = DATA / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def L(en: str, es: str = "") -> dict:
    return {"en": en, "es": es}


# ---------------------------------------------------------------- crops + rotations
CROPS = {
    # need_mm: seasonal irrigation need at full supply; rev: $/ac irrigated, dry: $/ac rainfed
    "corn": dict(name=L("Corn", "Maíz"), family="poaceae", host="corn", season="summer", need=480, rev=880, dry=240, bare=200, heat=True, forage=False, legume=False, months=(5, 10)),
    "sorghum": dict(name=L("Sorghum", "Sorgo"), family="poaceae", host="sorghum", season="summer", need=230, rev=430, dry=280, bare=220, heat=False, forage=False, legume=False, months=(6, 10)),
    "wheat": dict(name=L("Wheat", "Trigo"), family="poaceae", host="wheat", season="winter", need=150, rev=330, dry=230, bare=160, heat=False, forage=False, legume=False, months=(1, 6)),
    "soybean": dict(name=L("Soybean", "Soya"), family="fabaceae", host="soybean", season="summer", need=380, rev=640, dry=210, bare=220, heat=True, forage=False, legume=True, months=(5, 9)),
    "alfalfa": dict(name=L("Alfalfa", "Alfalfa"), family="fabaceae", host="alfalfa", season="perennial", need=620, rev=980, dry=320, bare=30, heat=False, forage=True, legume=True, months=(1, 12)),
    "triticale": dict(name=L("Triticale (forage)", "Triticale (forraje)"), family="poaceae", host="wheat", season="winter", need=110, rev=300, dry=210, bare=170, heat=False, forage=True, legume=False, months=(1, 5)),
    "rye_cover": dict(name=L("Cereal rye cover", "Centeno de cobertura"), family="poaceae", host="wheat", season="cover", need=0, rev=-30, dry=-30, bare=0, heat=False, forage=False, legume=False, months=(11, 4)),
    "cotton": dict(name=L("Cotton", "Algodón"), family="malvaceae", host="cotton", season="summer", need=260, rev=520, dry=300, bare=230, heat=False, forage=False, legume=False, months=(5, 10)),
    "fallow": dict(name=L("Fallow", "Barbecho"), family="none", host="none", season="none", need=0, rev=0, dry=0, bare=330, heat=False, forage=False, legume=False, months=None),
}


def crops_file() -> dict:
    crops = {}
    for cid, c in CROPS.items():
        none = cid == "fallow"
        crops[cid] = {
            "name": c["name"], "family": c["family"], "host_group": c["host"], "season": c["season"],
            "plant_window": None if none else {"start": "04-20", "end": "05-15"},
            "harvest_window": None if none else {"start": "09-20", "end": "10-31"},
            "stage_days": None if none else {"ini": 25, "dev": 40, "mid": 50, "late": 30},
            "kc": None if none else {"ini": 0.3, "mid": 1.15, "end": 0.4},
            "root_max_m": None if none else 1.2, "p": None if none else 0.55, "ky": None if none else 1.0,
            "heat": {"stage": "mid", "tmax_c": 35} if c["heat"] else None,
            "frost_kill_c": None if none else -2, "requires_irrigation": False, "n_fixing": c["legume"],
            "residue": "low" if cid in ("soybean", "fallow", "cotton") else "high",
            "root_type": "deep_tap" if cid == "alfalfa" else ("tap" if cid in ("soybean", "cotton") else "fibrous"),
            "forage": c["forage"],
            "yield": {"nass_commodity": None if none else cid.upper(), "unit": "bu/ac", "irrigated_default": None, "dryland_default": None},
            "price": {"unit": "usd/bu", "default": None},
            "equipment": ["hay"] if cid == "alfalfa" else (["cotton"] if cid == "cotton" else []),
            "sources": ["FAO-56 Table 12", "K-State Research and Extension"],
        }
    return {"_meta": meta("crops"), "crops": crops}


def S(crop: str, cover: str | None = None) -> dict:
    return {"crop": crop, "cover_after": cover}


ROTATIONS = [
    {"id": "R1", "steps": [S("corn"), S("wheat"), S("sorghum")], "irrigated": True, "min_cap": "cap150", "requires_equipment": [], "needs_forage_market": False, "tier": "must"},
    {"id": "R2", "steps": [S("wheat"), S("sorghum"), S("fallow")], "irrigated": False, "min_cap": "dryland", "requires_equipment": [], "needs_forage_market": False, "tier": "must"},
    {"id": "R3", "steps": [S("wheat"), S("sorghum"), S("triticale")], "irrigated": False, "min_cap": "dryland", "requires_equipment": [], "needs_forage_market": True, "tier": "must"},
    {"id": "R4", "steps": [S("alfalfa")] * 4 + [S("corn"), S("wheat")], "irrigated": True, "min_cap": "cap450", "requires_equipment": ["hay"], "needs_forage_market": True, "tier": "must"},
    {"id": "R5", "steps": [S("corn"), S("soybean"), S("wheat", "rye_cover")], "irrigated": True, "min_cap": "cap300", "requires_equipment": [], "needs_forage_market": False, "tier": "must"},
    {"id": "R6", "steps": [S("cotton"), S("wheat"), S("sorghum")], "irrigated": False, "min_cap": "dryland", "requires_equipment": ["cotton"], "needs_forage_market": False, "tier": "could"},
]
CAP_ORDER = {c: i for i, c in enumerate(CAPS)}


# ---------------------------------------------------------------- weather
def weather(fid: str) -> list[dict]:
    text = subprocess.run(
        ["git", "show", f"origin/role/data:data-pipeline/out/processed/{fid}/weather_daily.csv"],
        capture_output=True, text=True, check=True, cwd=WEB,
    ).stdout
    rows = []
    for r in csv.DictReader(io.StringIO(text)):
        d = date.fromisoformat(r["date"])
        num = lambda k: float(r[k]) if r[k] not in ("", None) else None
        rows.append({"d": d, "tmax": num("tmax_c"), "tmin": num("tmin_c"), "tmean": num("tmean_c"), "p": num("precip_mm") or 0.0, "wmax": num("ws10m_max_ms") or 0.0})
    return rows


def climate_stats(rows: list[dict], y0: int, y1: int) -> dict:
    by_year = defaultdict(list)
    for r in rows:
        if y0 <= r["d"].year <= y1:
            by_year[r["d"].year].append(r)
    ff, last, first, gdd, precip, hot, et0 = [], [], [], [], [], [], []
    for year, rs in by_year.items():
        spring = [r["d"] for r in rs if r["tmin"] is not None and r["tmin"] <= 0 and r["d"].month < 7]
        fall = [r["d"] for r in rs if r["tmin"] is not None and r["tmin"] <= 0 and r["d"].month >= 7]
        if spring and fall:
            last.append(spring[-1].timetuple().tm_yday)
            first.append(fall[0].timetuple().tm_yday)
            ff.append(fall[0].timetuple().tm_yday - spring[-1].timetuple().tm_yday)
        gdd.append(sum(max(0.0, min(30, r["tmax"]) / 2 + max(10, r["tmin"]) / 2 - 10) for r in rs if r["tmax"] is not None and r["tmin"] is not None))
        precip.append(sum(r["p"] for r in rs))
        hot.append(sum(1 for r in rs if r["tmax"] is not None and r["tmax"] >= 35))
        et0.append(sum(0.0023 * 15 * (r["tmean"] + 17.8) * math.sqrt(max(0.0, r["tmax"] - r["tmin"])) for r in rs if r["tmax"] is not None and r["tmin"] is not None and r["tmean"] is not None))
    mean = lambda xs: sum(xs) / len(xs) if xs else 0
    doy = lambda n: (date(2001, 1, 1).toordinal() + round(n) - 1)
    md = lambda n: date.fromordinal(doy(n)).strftime("%m-%d")
    return {
        "frost_free_days": round(mean(ff)), "last_spring_frost": md(mean(last)), "first_fall_frost": md(mean(first)),
        "gdd_base10_c": round(mean(gdd)), "precip_mm_yr": round(mean(precip)), "days_tmax_ge_35": round(mean(hot)),
        "et0_mm_yr": round(mean(et0)),
    }


def climate_risk(rows: list[dict]) -> list[dict]:
    cells = defaultdict(list)
    for r in rows:
        if 2000 <= r["d"].year <= 2025:
            cells[(r["d"].year, r["d"].month)].append(r)
    out = []
    for m in range(1, 13):
        yrs = [cells[(y, m)] for y in YEARS if cells[(y, m)]]
        n = len(yrs)
        out.append({
            "month": m,
            "p_heat": round(sum(1 for rs in yrs if sum(1 for r in rs if (r["tmax"] or 0) >= 35) >= 3) / n, 2),
            "p_frost": round(sum(1 for rs in yrs if any((r["tmin"] if r["tmin"] is not None else 9) <= -2 for r in rs)) / n, 2) if m in (3, 4, 5, 9, 10, 11) else (1.0 if m in (1, 2, 12) else 0.0),
            "p_dry_spell": round(sum(1 for rs in yrs if sum(r["p"] for r in rs) < 10) / n, 2),
            "storm_days": round(sum(sum(1 for r in rs if r["p"] >= 25) for rs in yrs) / n),
            "windy_days": round(sum(sum(1 for r in rs if r["wmax"] >= 12) for rs in yrs) / n),
        })
    return out


def yearly(rows: list[dict]) -> dict[int, dict]:
    out = {}
    for y in YEARS:
        rs = [r for r in rows if r["d"].year == y]
        grow = [r for r in rs if 5 <= r["d"].month <= 9]
        out[y] = {
            "precip": sum(r["p"] for r in rs),
            "grow_p": sum(r["p"] for r in grow),
            "hot": sum(1 for r in grow if (r["tmax"] or 0) >= 35),
            "frost": sum(1 for r in rs if r["d"].month in (4, 5, 10) and (r["tmin"] if r["tmin"] is not None else 9) <= -2),
            "storm": sum(1 for r in rs if r["p"] >= 25),
            "windy": sum(1 for r in rs if r["wmax"] >= 12 and r["d"].month in (2, 3, 4, 5)),
        }
    return out


# ---------------------------------------------------------------- replay model (toy, deterministic)
def rotation_steps(fid: str, field: dict) -> dict[str, list[dict]]:
    r0 = [S(c) for c in field["detected"]["sequence"]]
    return {"R0": r0, **{r["id"]: r["steps"] for r in ROTATIONS}}


def run_rotation(steps: list[dict], cap: str, climate: str, yr: dict[int, dict], soil: dict, irrigated_field: bool) -> dict:
    cap_mm = CAP_MM[cap] if irrigated_field or cap == "dryland" else min(CAP_MM[cap], 150)
    grow_mean = sum(v["grow_p"] for v in yr.values()) / len(yr)
    awc_factor = 0.75 + soil["aws_0_100_mm"] / 400
    wei = (soil["wei_t_ac_yr"] or 48) / 100
    kfact = soil["k_factor"] or 0.2
    by_year = []
    n = len(steps)
    for y in YEARS:
        v = yr[y]
        rain = v["grow_p"] * (0.85 if climate == "hotdry" else 1.0)
        dryness = max(0.0, (grow_mean - rain) / grow_mean)
        acc = defaultdict(float)
        mix = defaultdict(float)
        for s in steps:
            c = CROPS[s["crop"]]
            mix[s["crop"]] += 1 / n
            need = c["need"] * (1 + 0.9 * dryness + (0.12 if climate == "hotdry" else 0)) / awc_factor
            irr = min(need, cap_mm)
            unmet = need - irr
            rel = 1.0 if need == 0 else max(0.25, 1 - 0.75 * unmet / max(need, 1) * (0.6 + dryness))
            base = c["dry"] + (c["rev"] - c["dry"]) * (irr / need if need else 0)
            rev = base * rel if c["need"] else c["rev"]
            bare = c["bare"] - (110 if s["cover_after"] else 0)
            if s["cover_after"]:
                rev += CROPS[s["cover_after"]]["rev"]
            hot = v["hot"] + (8 if climate == "hotdry" else 0)
            acc["irr"] += irr / n
            acc["etc"] += (c["need"] + rain * 0.8) / n
            acc["eta"] += (c["need"] + rain * 0.8 - unmet) / n
            acc["stress"] += (unmet / max(need, 1) * 45 if need else 0) / n
            acc["rel"] += rel / n
            acc["rev"] += rev / n
            acc["bare"] += bare / n
            acc["werr"] += bare / 365 * v["storm"] * kfact * (1 + soil["slope_pct"] / 5) / n
            acc["wind"] += bare / 365 * v["windy"] * wei / 10 / n
            acc["heat"] += (hot if c["heat"] else hot * 0.3) / n
            acc["frost"] += v["frost"] * (0.5 if c["season"] == "summer" else 0.2) / n
        by_year.append({
            "year": y, "crop_mix": {k: round(x, 2) for k, x in mix.items()},
            "irrigation_mm": round(acc["irr"]), "eta_mm": round(acc["eta"]), "etc_mm": round(acc["etc"]),
            "stress_days": round(acc["stress"]), "rel_yield": round(acc["rel"], 2),
            "revenue_usd_ac": round(acc["rev"]), "bare_days": round(acc["bare"]),
            "water_erosion_idx": round(acc["werr"], 2), "wind_erosion_idx": round(acc["wind"], 2),
            "heat_days": round(acc["heat"]), "frost_events": round(acc["frost"]),
        })
    mean = lambda k: sum(b[k] for b in by_year) / len(by_year)
    worst5 = sorted(b["revenue_usd_ac"] for b in by_year)[:5]
    bare_mean = mean("bare_days")
    storm_mean = sum(yr[y]["storm"] for y in YEARS) / len(YEARS)
    windy_mean = sum(yr[y]["windy"] for y in YEARS) / len(YEARS)
    summary = {
        "irrigation_mm_mean": round(mean("irrigation_mm")), "eta_mm_mean": round(mean("eta_mm")),
        "stress_days_mean": round(mean("stress_days")), "rel_yield_mean": round(mean("rel_yield"), 2),
        "revenue_usd_ac_mean": round(mean("revenue_usd_ac")), "revenue_usd_ac_worst5": round(sum(worst5) / 5),
        "bare_days_mean": round(bare_mean), "bare_storm_days_mean": round(bare_mean / 365 * storm_mean * 3),
        "bare_windy_days_mean": round(bare_mean / 365 * windy_mean * 2),
        "water_erosion_idx": round(mean("water_erosion_idx"), 2), "wind_erosion_idx": round(mean("wind_erosion_idx"), 2),
        "heat_days_mean": round(mean("heat_days")), "frost_events_total": sum(b["frost_events"] for b in by_year),
    }
    return {"summary": summary, "by_year": by_year}


def max_run(steps: list[dict]) -> int:
    hosts = [CROPS[s["crop"]]["host"] for s in steps]
    if len(set(hosts)) == 1:
        return 8 if hosts[0] != "none" else 0
    best, run = 1, 1
    seq = hosts + hosts
    for a, b in zip(seq, seq[1:]):
        run = run + 1 if a == b and a != "none" else 1
        best = max(best, min(run, len(hosts)))
    return best


def soil_score(steps: list[dict]) -> tuple[int, int, int]:
    n = len(steps)
    living = sum((365 - CROPS[s["crop"]]["bare"]) + (110 if s["cover_after"] else 0) for s in steps) / n
    legumes = sum(1 for s in steps if CROPS[s["crop"]]["legume"])
    families = len({CROPS[s["crop"]]["family"] for s in steps if s["crop"] != "fallow"})
    score = min(100, round(living / 3.65 * 0.6 + legumes / n * 25 + families * 6))
    return score, round(living), legumes


# ---------------------------------------------------------------- per field
def norm_scale(values: dict[str, float], higher_better: bool) -> dict[str, float]:
    lo, hi = min(values.values()), max(values.values())
    out = {}
    for k, x in values.items():
        t = 0.5 if hi == lo else (x - lo) / (hi - lo)
        out[k] = round(15 + 85 * (t if higher_better else 1 - t))
    return out


GAPS = {
    "R0": ["costs_not_modelled", "prices_constant", "model_simplified"],
    "R1": ["costs_not_modelled", "prices_constant", "county_yields"],
    "R2": ["costs_not_modelled", "county_yields", "openet_record_short"],
    "R3": ["crop_params_generic", "prices_constant", "county_yields"],
    "R4": ["crop_params_generic", "costs_not_modelled", "no_pest_data"],
    "R5": ["county_yields", "crop_params_generic", "neighbors_observational"],
    "R6": ["crop_params_generic", "county_yields", "model_simplified"],
}
RISKS = {
    "R0": ["water_rights", "crop_insurance"],
    "R1": ["herbicide_carryover", "crop_insurance"],
    "R2": ["fallow_wind", "herbicide_carryover"],
    "R3": ["buyer_availability", "new_crop_learning"],
    "R4": ["alfalfa_stand_water", "equipment_access", "buyer_availability"],
    "R5": ["cover_establishment", "seed_availability"],
    "R6": ["equipment_access", "buyer_availability", "new_crop_learning"],
}
CONFIDENCE = {"R0": "good", "R1": "good", "R2": "good", "R3": "fair", "R4": "limited", "R5": "fair", "R6": "limited"}


def build_field(fid: str, field: dict, rows: list[dict]) -> None:
    yr = yearly(rows)
    steps = rotation_steps(fid, field)
    neighbors = json.loads((DATA / f"field/{fid}/neighbors.json").read_text(encoding="utf-8"))
    water = json.loads((DATA / f"field/{fid}/water.json").read_text(encoding="utf-8"))
    observed = json.loads((DATA / f"field/{fid}/observed.json").read_text(encoding="utf-8"))
    precip_sorted = sorted(YEARS, key=lambda y: yr[y]["grow_p"])
    drought_years = sorted(set(precip_sorted[:4]) | ({2012, 2022} & set(precip_sorted[:8])))

    # replay
    replay = {s: {} for s in SCENARIOS}
    for s in SCENARIOS:
        cap, clim = s.split("|")
        for rid, st in steps.items():
            run = run_rotation(st, cap, clim, yr, field["soil"], field["irrigated"])
            rot = next((r for r in ROTATIONS if r["id"] == rid), None)
            feasible = rid == "R0" or CAP_ORDER[cap] >= CAP_ORDER[rot["min_cap"]]
            replay[s][rid] = {"feasible": feasible, **run}
    write(f"field/{fid}/replay.json", {"_meta": meta("replay"), "field_id": fid, "years": [2000, 2025], "drought_years": drought_years, "scenarios": replay})

    # strategies
    group_by_rot = {g["matches_rotation"]: g for g in neighbors["groups"] if g["matches_rotation"]}
    current_group = next((g for g in neighbors["groups"] if g["is_current"]), None)
    openet_years = defaultdict(float)
    for m in observed["openet_monthly"]:
        openet_years[m["month"][:4]] += m["et_mm"]
    openet_mean = sum(openet_years.values()) / len(openet_years) if openet_years else None
    strategies = {}
    worst_drought = min(drought_years, key=lambda y: yr[y]["grow_p"])
    for s in SCENARIOS:
        runs = {rid: replay[s][rid]["summary"] for rid in steps}
        r0 = runs["R0"]
        raw = {
            "water_use": {k: v["irrigation_mm_mean"] for k, v in runs.items()},
            "income_mean": {k: v["revenue_usd_ac_mean"] for k, v in runs.items()},
            "income_worst": {k: v["revenue_usd_ac_worst5"] for k, v in runs.items()},
            "soil_health": {k: soil_score(steps[k])[0] for k in runs},
            "water_erosion": {k: v["bare_storm_days_mean"] for k, v in runs.items()},
            "wind_erosion": {k: v["bare_windy_days_mean"] for k, v in runs.items()},
            "pest_break": {k: max_run(steps[k]) for k in runs},
            "heat_frost_risk": {k: v["heat_days_mean"] for k, v in runs.items()},
        }
        better = {"water_use": False, "income_mean": True, "income_worst": True, "soil_health": True, "water_erosion": False, "wind_erosion": False, "pest_break": False, "heat_frost_risk": False}
        units = {"water_use": "mm", "income_mean": "usd_ac", "income_worst": "usd_ac", "soil_health": "score", "water_erosion": "days", "wind_erosion": "days", "pest_break": "years", "heat_frost_risk": "days"}
        norms = {k: norm_scale(raw[k], better[k]) for k in CRITERIA}
        entries = []
        for rid in steps:
            v = runs[rid]
            score, living, legumes = soil_score(steps[rid])
            cvars = {
                "water_use": {"irrigation_mm": v["irrigation_mm_mean"], "saved_mm": r0["irrigation_mm_mean"] - v["irrigation_mm_mean"]},
                "income_mean": {"revenue_usd_ac": v["revenue_usd_ac_mean"], "diff_usd_ac": v["revenue_usd_ac_mean"] - r0["revenue_usd_ac_mean"]},
                "income_worst": {"worst5_usd_ac": v["revenue_usd_ac_worst5"], "r0_worst5_usd_ac": r0["revenue_usd_ac_worst5"]},
                "soil_health": {"score": score, "living_root_days": living, "legume_years": legumes},
                "water_erosion": {"bare_storm_days": v["bare_storm_days_mean"], "r0_bare_storm_days": r0["bare_storm_days_mean"]},
                "wind_erosion": {"bare_windy_days": v["bare_windy_days_mean"], "r0_bare_windy_days": r0["bare_windy_days_mean"]},
                "pest_break": {"max_run_years": max_run(steps[rid]), "r0_max_run_years": max_run(steps["R0"])},
                "heat_frost_risk": {"heat_days": v["heat_days_mean"], "r0_heat_days": r0["heat_days_mean"]},
            }
            rot = next((r for r in ROTATIONS if r["id"] == rid), None)
            feasible = replay[s][rid]["feasible"]
            benefits = []
            if rid != "R0":
                saved = cvars["water_use"]["saved_mm"]
                if saved > 30:
                    benefits.append({"text_id": "water_saved", "vars": {"saved_mm": saved}})
                bare_diff = r0["bare_days_mean"] - v["bare_days_mean"]
                if bare_diff > 20:
                    benefits.append({"text_id": "bare_days_reduced", "vars": {"days": bare_diff}})
                if legumes:
                    benefits.append({"text_id": "legume_added", "vars": {"legume_years": legumes, "cycle_years": len(steps[rid])}})
                gain = v["revenue_usd_ac_worst5"] - r0["revenue_usd_ac_worst5"]
                if gain > 10:
                    benefits.append({"text_id": "income_steadier", "vars": {"worst5_gain_usd_ac": gain}})
                if max_run(steps[rid]) < max_run(steps["R0"]):
                    benefits.append({"text_id": "pest_cycle_broken", "vars": {"max_run_years": max_run(steps[rid])}})
                forage = next((st["crop"] for st in steps[rid] if CROPS[st["crop"]]["forage"]), None)
                if forage:
                    benefits.append({"text_id": "forage_income", "vars": {"forage_crop": forage}})
            drought_irr = next(b for b in replay[s][rid]["by_year"] if b["year"] == worst_drought)["irrigation_mm"]
            r0_drought_irr = next(b for b in replay[s]["R0"]["by_year"] if b["year"] == worst_drought)["irrigation_mm"]
            evidence = [
                {"text_id": "replay_avg", "vars": {"years_from": 2000, "years_to": 2025, "irrigation_mm": v["irrigation_mm_mean"], "revenue_usd_ac": v["revenue_usd_ac_mean"]}, "sources": ["POWER", "SSURGO", "FAO56", "NASS"]},
                {"text_id": "replay_drought", "vars": {"year": worst_drought, "irrigation_mm": drought_irr, "r0_irrigation_mm": r0_drought_irr}, "sources": ["POWER", "FAO56"]},
            ]
            group = group_by_rot.get(rid)
            if group and group["et_mm_yr_median"] is not None:
                r0_et = current_group["et_mm_yr_median"] if current_group and current_group["et_mm_yr_median"] is not None else round(openet_mean or 0)
                evidence.append({"text_id": "neighbors", "vars": {"n": group["n"], "et_mm": group["et_mm_yr_median"], "r0_et_mm": r0_et}, "sources": ["OpenET", "CSB", "SSURGO"]})
            if rid == "R0" and openet_mean:
                bias = round((replay["cap300|actual"]["R0"]["summary"]["eta_mm_mean"] - openet_mean) / openet_mean * 100)
                evidence.append({"text_id": "validation_et", "vars": {"bias_pct": bias}, "sources": ["OpenET", "MODEL"]})
            no_market = [st["crop"] for st in steps[rid] if st["crop"] in ("cotton", "triticale")]
            entries.append({
                "rotation_id": rid, "feasible": feasible,
                "infeasible_reason_id": None if feasible else "needs_more_water",
                "criteria": {k: {"raw": raw[k][rid], "unit": units[k], "norm": norms[k][rid], "vars": cvars[k]} for k in CRITERIA},
                "requires_equipment": rot["requires_equipment"] if rot else [],
                "needs_forage_market": rot["needs_forage_market"] if rot else False,
                "crops_without_local_market": sorted(set(no_market)),
                "benefits": benefits, "evidence": evidence,
                "gap_ids": GAPS[rid], "risk_ids": RISKS[rid], "confidence": CONFIDENCE[rid],
            })
        strategies[s] = entries
    write(f"field/{fid}/strategies.json", {"_meta": meta("strategies"), "field_id": fid, "scenarios": strategies})

    # calendar
    risk = climate_risk(rows)
    cal_rots = []
    for rid, st in steps.items():
        cal_rots.append({"rotation_id": rid, "years": calendar_years(st, risk)})
    write(f"field/{fid}/calendar.json", {"_meta": meta("calendar"), "field_id": fid, "climate_risk": risk, "rotations": cal_rots})

    # summary
    normal = climate_stats(rows, 1991, 2020)
    recent = climate_stats(rows, 2016, 2025)
    wells = [w["trend_m_per_yr"] for w in water["wells"] if w["trend_m_per_yr"] is not None]
    well_trend = round(sum(wells) / len(wells), 2) if wells else None
    grace = water["grace"]["trend_cm_per_yr"]
    outlook = "declining" if grace < -0.3 or (well_trend or 0) > 0.3 else ("rising" if grace > 0.3 else "stable")
    years = field["detected"]["years"]
    write(f"field/{fid}/summary.json", {
        "_meta": meta("summary"), "field_id": fid,
        "current_rotation": {"steps": steps["R0"], "rotation_class": field["detected"]["rotation_class"], "years": years},
        "climate": {"normal": normal, "recent": recent, "normal_period": "1991-2020", "recent_period": "2016-2025", "sources": ["POWER"]},
        "water": {"grace_trend_cm_per_yr": grace, "wells_trend_m_per_yr": well_trend, "outlook": outlook},
        "headline_facts": [
            {"text_id": "grace_trend", "vars": {"cm_per_yr": grace}, "sources": ["GRACE"]},
            {"text_id": "heat_days_change", "vars": {"days": recent["days_tmax_ge_35"] - normal["days_tmax_ge_35"]}, "sources": ["POWER"]},
            {"text_id": "current_rotation", "vars": {"years_from": years[0], "years_to": years[1]}, "sources": ["CSB"]},
        ],
    })

    # validation
    items = []
    if openet_mean:
        eta = replay["cap300|actual"]["R0"]["summary"]["eta_mm_mean"]
        bias = round((eta - openet_mean) / openet_mean * 100)
        items.append({"id": "et_vs_openet", "metric": "bias_pct", "value": bias, "n": len(openet_years), "level": "good" if abs(bias) <= 10 else ("fair" if abs(bias) <= 25 else "limited"), "vars": {"bias_pct": bias}, "sources": ["OpenET", "MODEL"]})
    items.append({"id": "sm_vs_smap", "metric": "r", "value": 0.62, "n": 120, "level": "fair", "vars": {"r": 0.62}, "sources": ["SMAP", "MODEL"]})
    write(f"field/{fid}/validation.json", {"_meta": meta("validation"), "field_id": fid, "items": items})

    # assistant context
    facts = []
    soil = field["soil"]
    facts += [
        {"id": "field.soil.aws_0_100_mm", "text": f"The soil stores about {soil['aws_0_100_mm']} mm of plant-available water in the top metre.", "value": soil["aws_0_100_mm"], "unit": "mm", "source": "SSURGO"},
        {"id": "field.soil.om_pct", "text": f"Surface organic matter is {soil['om_pct']}%.", "value": soil["om_pct"], "unit": "pct", "source": "SSURGO"},
        {"id": "water.grace_trend_cm_per_yr", "text": f"GRACE shows total water storage changing by {grace} cm per year.", "value": grace, "unit": "cm_per_yr", "source": "GRACE"},
        {"id": "climate.recent.days_tmax_ge_35", "text": f"Recent years (2016-2025) average {recent['days_tmax_ge_35']} days at or above 35 °C.", "value": recent["days_tmax_ge_35"], "unit": "days", "source": "POWER"},
        {"id": "climate.normal.days_tmax_ge_35", "text": f"The 1991-2020 normal is {normal['days_tmax_ge_35']} days at or above 35 °C.", "value": normal["days_tmax_ge_35"], "unit": "days", "source": "POWER"},
        {"id": "climate.recent.precip_mm_yr", "text": f"Recent annual rainfall averages {recent['precip_mm_yr']} mm.", "value": recent["precip_mm_yr"], "unit": "mm", "source": "POWER"},
        {"id": "climate.recent.frost_free_days", "text": f"The recent frost-free season is {recent['frost_free_days']} days.", "value": recent["frost_free_days"], "unit": "days", "source": "POWER"},
    ]
    if well_trend is not None:
        facts.append({"id": "water.wells_trend_m_per_yr", "text": f"Nearby wells show depth to water growing by {well_trend} m per year.", "value": well_trend, "unit": "m_per_yr", "source": "USGS"})
    for g in neighbors["groups"]:
        if g["et_mm_yr_median"] is not None:
            facts.append({"id": f"neighbors.{g['rotation_class']}.et_mm_yr_median", "text": f"{g['n']} similar nearby fields in the {g['rotation_class']} class use a median {g['et_mm_yr_median']} mm of water per year (OpenET).", "value": g["et_mm_yr_median"], "unit": "mm", "source": "OpenET", **({"rotation_id": g["matches_rotation"]} if g["matches_rotation"] else {})})
    for s in SCENARIOS:
        for rid in steps:
            v = replay[s][rid]["summary"]
            facts.append({"id": f"replay.{rid}.{s}.irrigation_mm_mean", "text": f"Under {s}, {rid} needs on average {v['irrigation_mm_mean']} mm of irrigation per year (2000-2025).", "value": v["irrigation_mm_mean"], "unit": "mm", "source": "MODEL", "scenario": s, "rotation_id": rid})
            facts.append({"id": f"replay.{rid}.{s}.revenue_usd_ac_mean", "text": f"Under {s}, {rid} earns on average ${v['revenue_usd_ac_mean']}/ac per year.", "value": v["revenue_usd_ac_mean"], "unit": "usd_ac", "source": "MODEL", "scenario": s, "rotation_id": rid})
            if s == "cap300|actual":
                facts.append({"id": f"replay.{rid}.{s}.revenue_usd_ac_worst5", "text": f"Under {s}, {rid} earns ${v['revenue_usd_ac_worst5']}/ac on average in its 5 worst years.", "value": v["revenue_usd_ac_worst5"], "unit": "usd_ac", "source": "MODEL", "scenario": s, "rotation_id": rid})
    write(f"field/{fid}/assistant_context.json", {"_meta": meta("assistant_context"), "field_id": fid, "field_name": field["name"]["en"], "facts": facts})


MONTH_STAGE = {"ini": 0, "dev": 1, "mid": 2, "late": 3}


def calendar_years(steps: list[dict], risk: list[dict]) -> list[dict]:
    n = len(steps)
    grid = [[{"state": "bare", "stage": None, "flags": []} for _ in range(12)] for _ in range(n)]

    def put(year: int, month: int, crop: str, stage: str | None):
        cell = grid[year % n][month - 1]
        if cell["state"] == "bare" or crop != "rye_cover":
            grid[year % n][month - 1] = {"state": crop, "stage": stage, "flags": []}

    for i, s in enumerate(steps):
        crop = s["crop"]
        c = CROPS[crop]
        if crop == "fallow":
            continue
        if crop == "alfalfa":
            for m in range(1, 13):
                put(i, m, crop, "mid" if 5 <= m <= 9 else ("dev" if m in (3, 4) else None))
            continue
        if c["season"] == "winter":
            for m in (10, 11, 12):
                put(i - 1, m, crop, "ini")
            end = c["months"][1]
            for m in range(1, end + 1):
                put(i, m, crop, "dev" if m <= 3 else ("mid" if m < end else "late"))
        else:
            a, b = c["months"]
            span = list(range(a, b + 1))
            for k, m in enumerate(span):
                stage = "ini" if k == 0 else ("dev" if k == 1 else ("late" if k >= len(span) - 2 else "mid"))
                put(i, m, crop, stage)
        if s["cover_after"]:
            for m in (11, 12):
                put(i, m, s["cover_after"], None)
            for m in (1, 2, 3):
                put(i + 1, m, s["cover_after"], None)
    out = []
    for i in range(n):
        months = []
        for m, cell in enumerate(grid[i]):
            r = risk[m]
            flags = []
            if cell["state"] == "bare":
                if r["storm_days"] >= 1:
                    flags.append("bare_storm")
                if r["windy_days"] >= 4:
                    flags.append("bare_wind")
            else:
                if cell["stage"] == "mid" and r["p_heat"] >= 0.3:
                    flags.append("heat")
                if cell["stage"] in ("ini", "dev") and 0.15 <= r["p_frost"] < 1:
                    flags.append("frost")
                if cell["stage"] in ("mid", "late") and r["p_dry_spell"] >= 0.2:
                    flags.append("dry")
            months.append({**cell, "flags": flags})
        out.append({"year_index": i + 1, "months": months})
    return out


# ---------------------------------------------------------------- content (U) and prompt (M)
def card_text() -> dict:
    return {
        "_meta": meta("card_text"),
        "rotations": {
            "R0": {"name": L("Your current rotation"), "tagline": L("What the field has grown in recent years")},
            "R1": {"name": L("Corn, wheat, sorghum"), "tagline": L("Limited irrigation, three crops")},
            "R2": {"name": L("Wheat, sorghum, fallow"), "tagline": L("The dryland classic")},
            "R3": {"name": L("Wheat, sorghum, forage triticale"), "tagline": L("Flex fallow: forage instead of bare ground")},
            "R4": {"name": L("Alfalfa, then corn and wheat"), "tagline": L("Forage, deep roots, high water use")},
            "R5": {"name": L("Corn, soybean, wheat with rye cover"), "tagline": L("Soil health and nitrogen")},
            "R6": {"name": L("Cotton, wheat, sorghum"), "tagline": L("An option for a warmer climate")},
        },
        "criteria_labels": {
            "water_use": L("Water use"), "income_mean": L("Average income"), "income_worst": L("Income in bad years"),
            "soil_health": L("Soil health"), "water_erosion": L("Water erosion"), "wind_erosion": L("Wind erosion"),
            "pest_break": L("Pest break"), "heat_frost_risk": L("Heat and frost risk"),
        },
        "why": {
            "water_use": L("Needs about {irrigation_mm} of irrigation a year, {saved_mm} less than your current rotation."),
            "income_mean": L("Averages {revenue_usd_ac} a year, {diff_usd_ac} compared with your current rotation."),
            "income_worst": L("In its 5 worst years it still averages {worst5_usd_ac}, against {r0_worst5_usd_ac} now."),
            "soil_health": L("Soil health score {score}, with {living_root_days} days of living roots and {legume_years} legume years."),
            "water_erosion": L("Bare soil meets heavy rain on about {bare_storm_days} days a year, against {r0_bare_storm_days} now."),
            "wind_erosion": L("Bare soil meets strong wind on about {bare_windy_days} days a year, against {r0_bare_windy_days} now."),
            "pest_break": L("The same host crop runs at most {max_run_years} years in a row, against {r0_max_run_years} now."),
            "heat_frost_risk": L("Sensitive crop stages meet about {heat_days} hot days a year, against {r0_heat_days} now."),
        },
        "benefits": {
            "water_saved": L("Saves about {saved_mm} of irrigation a year."),
            "bare_days_reduced": L("About {days} fewer bare-soil days a year."),
            "legume_added": L("Adds {legume_years} legume years in a {cycle_years}-year cycle."),
            "income_steadier": L("Bad years pay about {worst5_gain_usd_ac} more."),
            "pest_cycle_broken": L("Breaks pest cycles: no host crop runs more than {max_run_years} years."),
            "forage_income": L("Adds forage income from {forage_crop}."),
        },
        "evidence": {
            "replay_avg": L("Replayed on this field's weather {years_from} to {years_to}: {irrigation_mm} of irrigation and {revenue_usd_ac} a year on average."),
            "replay_drought": L("In {year} it needed {irrigation_mm} of irrigation, against {r0_irrigation_mm} for your current rotation."),
            "neighbors": L("{n} similar nearby fields that grow this use about {et_mm} of water a year, against {r0_et_mm} for fields like yours."),
            "validation_et": L("Our water model is within {bias_pct} of satellite ET for this field."),
        },
        "gaps": {
            "no_pest_data": L("We have no local pest or disease data."),
            "costs_not_modelled": L("Input and machinery costs are not modelled."),
            "prices_constant": L("Prices are held constant across years."),
            "openet_record_short": L("The OpenET record starts in 2016."),
            "smap_coarse": L("SMAP soil moisture is a 9 km average, coarser than the field."),
            "county_yields": L("Yields are county averages, not this field's."),
            "neighbors_observational": L("Neighbour comparisons are observational, not experiments."),
            "model_simplified": L("The water model is a simplified daily budget."),
            "crop_params_generic": L("Crop parameters are generic, not tuned to local varieties."),
        },
        "risks": {
            "herbicide_carryover": L("Check herbicide carryover between crops."),
            "buyer_availability": L("Check that a local buyer will take this crop."),
            "crop_insurance": L("Check crop insurance rules for this rotation."),
            "water_rights": L("Check your water right and any local limits."),
            "equipment_access": L("Check access to the equipment this rotation needs."),
            "cover_establishment": L("Cover crops can be hard to establish in a dry fall."),
            "alfalfa_stand_water": L("Alfalfa stands need water every year to stay productive."),
            "fallow_wind": L("Fallow ground can blow in windy springs."),
            "new_crop_learning": L("A new crop takes time to learn."),
            "seed_availability": L("Check seed availability for this crop."),
        },
        "infeasible": {
            "needs_more_water": L("Needs more water than your irrigation limit."),
            "needs_equipment": L("Needs equipment you do not have."),
            "no_local_market": L("Needs a local buyer for forage or a crop with no county market."),
        },
        "headline": {
            "grace_trend": L("Satellite gravity data show the regional water store changing by {cm_per_yr}."),
            "well_trend": L("Nearby wells show the water table changing by {m_per_yr}."),
            "frost_free_change": L("The frost-free season has changed by {days} days."),
            "heat_days_change": L("Recent summers bring {days} more days above 35 °C than the 1991 to 2020 normal."),
            "current_rotation": L("USDA crop maps show this rotation from {years_from} to {years_to}."),
        },
        "validation": {
            "et_vs_openet": L("Modelled water use is within {bias_pct} of OpenET satellite estimates."),
            "sm_vs_smap": L("Modelled soil moisture tracks SMAP with a correlation of {r}."),
            "precip_power_vs_imerg": L("POWER rainfall differs from IMERG by {bias_pct}."),
            "precip_vs_cocorahs": L("POWER rainfall differs from local rain gauges by {bias_pct}."),
        },
    }


COPY = {
    "app.name": "Glean", "app.tagline": "Compare crop rotations for your field with NASA data",
    "disclaimer.main": "This tool supports your judgement. It does not replace it. Check water, markets and equipment with your local extension agent.",
    "banner.mock": "Mock data: some numbers on this page are placeholders.", "lang.en": "English", "lang.es": "Español",
    "nav.overview": "Overview", "nav.calendar": "Calendar", "nav.plan": "Plan", "nav.replay": "Replay", "nav.neighbors": "Farms like yours", "nav.trust": "How we know",
    "pick.title": "Pick a field", "pick.subtitle": "Three real fields in Finney County, Kansas. Pick one to see its conditions and compare rotations.", "pick.open_field": "Open field",
    "overview.current_rotation": "Current rotation", "overview.detected_from": "Detected from USDA crop history, {years_from} to {years_to}",
    "overview.soil": "Soil", "overview.climate_shift": "Climate shift", "overview.water_outlook": "Water outlook",
    "overview.outlook.declining": "Declining", "overview.outlook.stable": "Stable", "overview.outlook.rising": "Rising",
    "priorities.title": "Your priorities", "priorities.save_water": "Save water", "priorities.income": "Income", "priorities.steady_income": "Steady income", "priorities.soil_health": "Soil health", "priorities.erosion": "Erosion control",
    "constraints.title": "Your limits", "constraints.water_cap": "Irrigation limit per season",
    "constraints.cap.dryland": "Dryland", "constraints.cap.cap150": "150 mm (6 in)", "constraints.cap.cap300": "300 mm (12 in)", "constraints.cap.cap450": "450 mm (18 in)",
    "constraints.hay_equipment": "I have hay equipment", "constraints.cotton_equipment": "I have cotton equipment", "constraints.forage_buyer": "I have a forage buyer",
    "climate.title": "Climate", "climate.actual": "Actual weather", "climate.hotdry": "Hotter and drier",
    "card.why": "Why", "card.evidence": "Evidence", "card.benefits": "Benefits", "card.gaps": "Information gaps", "card.risks": "Risks to check locally",
    "card.current_badge": "Current", "card.score": "Score", "card.confidence": "Confidence", "card.hidden_count": "{n} strategies hidden",
    "calendar.title": "Field calendar", "calendar.subtitle": "When the field is bare and when crops are vulnerable, month by month.", "calendar.bare": "Bare soil",
    "calendar.flag.heat": "Heat", "calendar.flag.frost": "Frost", "calendar.flag.dry": "Dry spell", "calendar.flag.bare_storm": "Storm on bare soil", "calendar.flag.bare_wind": "Wind on bare soil",
    "replay.title": "Rotation replay", "replay.subtitle": "Each rotation run on this field's real weather, 2000 to 2025.",
    "replay.metric.irrigation": "Irrigation", "replay.metric.revenue": "Revenue", "replay.metric.stress": "Stress days", "replay.metric.bare": "Bare days", "replay.drought_marker": "Drought year",
    "neighbors.title": "Farms like yours", "neighbors.subtitle": "Nearby fields on similar soil that already grow other rotations.",
    "neighbors.disclaimer": "These are similar fields observed from orbit, not experiments. They show what is possible, not proof.",
    "neighbors.n_fields": "Fields", "neighbors.water_use": "Water use", "neighbors.drought_greenness": "Greenness drop in drought",
    "trust.title": "How we know", "trust.subtitle": "Where every number comes from and how far to trust it.",
    "trust.level.good": "Good", "trust.level.fair": "Fair", "trust.level.limited": "Limited", "trust.sources": "Sources", "trust.glossary": "Glossary",
    "assistant.title": "Field assistant", "assistant.placeholder": "Ask about this field", "assistant.send": "Send", "assistant.suggested": "Suggested questions",
    "assistant.verified": "Verified against field data", "assistant.unverified": "unverified", "assistant.using_cache": "Saved answer for the default scenario (300 mm, actual weather).",
    "assistant.error": "The assistant is not available right now. Try a suggested question.",
}

GLOSSARY = [
    ("et", "Evapotranspiration (ET)", "Water leaving the field through plants and soil."),
    ("et0", "Reference ET", "How much water a short grass crop would use in this weather."),
    ("ndvi", "NDVI", "A satellite greenness index: higher means more living plants."),
    ("soil_moisture_anomaly", "Soil moisture anomaly", "How wet the soil is compared with normal for that month."),
    ("root_zone", "Root zone", "The soil layer roots can reach, about the top metre."),
    ("frost_risk", "Frost risk", "The chance of a damaging frost while a crop is young."),
    ("gdd", "Growing degree days", "Accumulated warmth that drives crop growth."),
    ("water_balance", "Water balance", "Rain and irrigation in, crop use and drainage out."),
    ("evaporative_stress", "Evaporative stress", "When crops use less water than the weather demands."),
    ("aquifer", "Aquifer", "The underground water store wells pump from: here, the Ogallala."),
    ("rotation", "Rotation", "The order of crops grown on a field across years."),
    ("cover_crop", "Cover crop", "A crop grown to protect and feed the soil, not to sell."),
    ("fallow", "Fallow", "A season with no crop to store soil water."),
    ("nitrogen_fixing", "Nitrogen fixing", "Legumes that add nitrogen to the soil."),
    ("wind_erosion", "Wind erosion", "Soil blown away from bare, dry ground."),
    ("water_erosion", "Water erosion", "Soil washed away by heavy rain on bare ground."),
    ("satellite_vs_ground", "Satellite versus ground", "We compare satellite readings with ground records to see how far to trust them."),
    ("model_estimate", "Model estimate", "A number we calculate from data, not one we measured on the field."),
]

QUESTIONS = [
    ("q1", "Which rotation saves the most water on my field?"),
    ("q2", "How did my current rotation do in the 2012 drought?"),
    ("q3", "Why not alfalfa?"),
    ("q4", "Is my aquifer declining?"),
    ("q5", "How hot are summers getting here?"),
    ("q6", "What should I check with the K-State extension agent?"),
]

PROMPT_SYSTEM = (
    "You are the Glean assistant for {field_name}, a field in Finney County, Kansas. "
    "Answer in {lang_name}, in plain language a farmer would use. The scenario is {scenario_label}. "
    "The rotations on screen, best first, are {top_rotations}.\n\n"
    "Only use numbers from the facts below. After each number, add its source tag in square brackets, for example [POWER]. "
    "If the facts do not answer the question, say so and suggest what to check with the K-State extension agent. "
    "Never give financial or legal advice.\n\nFacts:\n{facts_block}"
)


def main() -> None:
    fields = json.loads((DATA / "fields.json").read_text(encoding="utf-8"))["fields"]
    write("crops.json", crops_file())
    write("rotations.json", {"_meta": meta("rotations"), "rotations": ROTATIONS})
    write("content/card_text.json", card_text())
    write("content/copy.json", {"_meta": meta("copy"), "strings": {k: L(v) for k, v in COPY.items()}})
    write("content/glossary.json", {"_meta": meta("glossary"), "terms": [{"id": i, "term": L(t), "short": L(s), "long": L(s)} for i, t, s in GLOSSARY]})
    write("content/assistant_questions.json", {"_meta": meta("assistant_questions"), "questions": [{"id": i, "text": L(t)} for i, t in QUESTIONS]})
    write("assistant/prompt.json", {"_meta": meta("prompt"), "version": "mock-1", "system": PROMPT_SYSTEM, "temperature": 0.2, "max_tokens": 700})
    for f in fields:
        build_field(f["id"], f, weather(f["id"]))
        print("wrote", f["id"])


if __name__ == "__main__":
    main()
