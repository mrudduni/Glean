"""Build field/{fid}/assistant_context.json (README 8.4) from model, data and content outputs.

Usage: python context.py [--model-web DIR] [--out DIR] [--standins]
Every fact is one English sentence with its number, a value, a unit and a source tag.
Facts with no number (glossary, yes/no) carry value null; the number check skips them.
"""
from __future__ import annotations

import argparse
import json
import statistics
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from paths import CONTENT_DIR, DATA_WEB, FIELDS, OUT_WEB, SCENARIO

CAPS = {"dryland": 0, "cap150": 150, "cap300": 300, "cap450": 450}
ROT_IDS = ["R0", "R1", "R2", "R3", "R4", "R5"]
DROUGHT_PICKS = 2  # drought years listed per rotation, 2012 first
NEIGHBOR_NAMES = {
    "wsf": "wheat, sorghum, fallow", "corn_wheat_sorghum": "corn, wheat, sorghum", "corn_soy": "corn, soybean",
    "continuous_corn": "continuous corn", "wheat_fallow": "wheat, fallow", "alfalfa": "alfalfa",
    "mixed": "mixed crops",
}


def load(p: Path):
    return json.loads(p.read_text(encoding="utf8"))


def crops_phrase(crops: list[str]) -> str:
    names = [c.replace("_", " ") for c in crops]
    if len(names) == 1:
        return f"continuous {names[0]}"
    return ", ".join(names)


def scenario_label(key: str) -> str:
    cap, clim = key.split("|")
    water = ("no irrigation (dryland)" if cap == "dryland"
             else f"up to {CAPS[cap]} mm ({CAPS[cap] / 25.4:.0f} in) of irrigation per season")
    weather = ("past weather as it happened" if clim == "actual"
               else "a hotter, drier climate (1.5 °C warmer, 15% less rain)")
    return f"{water}, {weather}"


class Builder:
    def __init__(self, fid: str, model_web: Path):
        self.fid = fid
        self.facts: list[dict] = []
        self.mock = False
        self.mw = model_web
        self.dw = DATA_WEB

    def add(self, id, text, value, unit, source, scenario=None, rotation_id=None):
        f = {"id": id, "text": text, "value": value, "unit": unit, "source": source}
        if scenario:
            f["scenario"] = scenario
        if rotation_id:
            f["rotation_id"] = rotation_id
        self.facts.append(f)

    def read_model(self, name: str):
        d = load(self.mw / "field" / self.fid / name)
        self.mock = self.mock or d["_meta"].get("mock", False)
        return d

    def field_basics(self, fld: dict):
        s = fld["soil"]
        self.add("field.area_ac", f"The field covers {fld['area_ac']} acres.", fld["area_ac"], "ac", "CSB")
        self.add("field.irrigation",
                 "The field is irrigated." if fld["irrigated"] else "The field is not irrigated (dryland).",
                 None, None, "CSB")
        self.add("field.soil_texture", f"The main soil is {s['texture']} ({s['component']}).", None, None, "SSURGO")
        self.add("field.water_storage_mm",
                 f"The soil can hold about {s['aws_0_100_mm']} mm of plant-available water in the top 1 m.",
                 s["aws_0_100_mm"], "mm", "SSURGO")
        self.add("field.organic_matter_pct", f"Soil organic matter is {s['om_pct']}%.", s["om_pct"], "pct", "SSURGO")
        self.add("field.weg", f"The wind erodibility group is {s['weg']} (1 is the most erodible, 8 the least).",
                 float(s["weg"]), None, "SSURGO")
        self.add("field.wei_t_ac_yr", f"The wind erodibility index is {s['wei_t_ac_yr']} tons per acre per year.",
                 s["wei_t_ac_yr"], "t_ac_yr", "SSURGO")
        self.add("field.slope_pct", f"The slope is {s['slope_pct']}%.", s["slope_pct"], "pct", "SSURGO")
        det = fld["detected"]
        self.add("field.detected_rotation",
                 f"Crop maps show this field grew {crops_phrase(det['sequence'])} from {det['years'][0]} to {det['years'][1]}.",
                 det["years"][1] - det["years"][0] + 1, "years", "CSB")

    def climate(self, summ: dict):
        c = summ["climate"]
        for which, label in (("normal", "1991 to 2020"), ("recent", "2016 to 2025")):
            x = c[which]
            src = "PRISM" if which == "normal" else "POWER"
            rows = [
                ("frost_free_days", f"The average frost-free season in {label} is {x['frost_free_days']} days.", "days"),
                ("precip_mm_yr", f"Average rain and snow in {label} is {x['precip_mm_yr']} mm per year.", "mm"),
                ("days_tmax_ge_35",
                 f"The average number of days at or above 35 °C in {label} is {x['days_tmax_ge_35']} days per year.", "days"),
                ("et0_mm_yr", f"Reference evapotranspiration in {label} is {x['et0_mm_yr']} mm per year.", "mm"),
                ("gdd_base10_c", f"Growing degree days (base 10 °C) in {label} total {x['gdd_base10_c']} per year.", None),
            ]
            for key, text, unit in rows:
                self.add(f"climate.{which}.{key}", text, x[key], unit, src)

    def water(self):
        w = load(self.dw / "field" / self.fid / "water.json")
        g = w["grace"]["trend_cm_per_yr"]
        if g is not None:
            self.add("water.grace_trend_cm_per_yr",
                     f"Satellite gravity data show regional groundwater storage {'falling' if g < 0 else 'rising'} "
                     f"by about {abs(g)} cm of water per year.", g, "cm_per_yr", "GRACE")
        trends = [x["trend_m_per_yr"] for x in w["wells"] if x.get("trend_m_per_yr") is not None]
        if trends:
            t = round(statistics.median(trends), 2)
            self.add("water.wells_trend_m_per_yr",
                     f"Across {len(trends)} nearby monitoring wells the depth to water is "
                     f"{'getting deeper' if t > 0 else 'getting shallower'} by a median of {abs(t)} m per year.",
                     t, "m_per_yr", "USGS")

    def neighbors(self):
        n = load(self.dw / "field" / self.fid / "neighbors.json")
        for g in n["groups"]:
            cls = g["rotation_class"]
            nm = NEIGHBOR_NAMES.get(cls, cls)
            self.add(f"neighbors.{cls}.n", f"{g['n']} similar nearby fields grew {nm}.", g["n"], None, "CSB")
            if g.get("et_mm_yr_median") is not None:
                self.add(f"neighbors.{cls}.et_mm_yr_median",
                         f"Similar nearby fields growing {nm} used a median of {g['et_mm_yr_median']} mm of water per year (satellite estimate).",
                         g["et_mm_yr_median"], "mm", "OpenET")
            for yr in (2012, 2022):
                v = g.get(f"ndvi_drop_{yr}_pct")
                if v is not None:
                    self.add(f"neighbors.{cls}.ndvi_drop_{yr}_pct",
                             f"In {yr}, similar nearby fields growing {nm} were {v}% less green than usual.", v, "pct", "MODIS")

    def validation(self):
        v = self.read_model("validation.json")
        phr = {
            "et_vs_openet": ("Model water use differed from OpenET satellite estimates by {x}%.", "pct"),
            "sm_vs_smap": ("Model soil moisture and SMAP satellite soil moisture correlate at r = {x}.", None),
            "precip_power_vs_imerg": ("POWER and IMERG rainfall correlate at r = {x}.", None),
            "precip_vs_cocorahs": ("Model rainfall and CoCoRaHS gauge rainfall correlate at r = {x}.", None),
        }
        for it in v["items"]:
            t, unit = phr[it["id"]]
            self.add(f"validation.{it['id']}", t.format(x=it["value"]) + f" Confidence is {it['level']}.",
                     it["value"], unit, it["sources"][0])

    def glossary(self):
        p = CONTENT_DIR / "glossary.json"
        if not p.exists():
            return
        for t in load(p)["terms"]:
            self.add(f"glossary.{t['id']}", t["short"]["en"], None, None, "MODEL")

    def replay(self, rot_names: dict[str, str]):
        rep = self.read_model("replay.json")
        strat = self.read_model("strategies.json")
        soil = {}
        for key, entries in strat["scenarios"].items():
            for e in entries:
                c = e["criteria"].get("soil_health")
                soil[(key, e["rotation_id"])] = c["raw"] if c else None
        for key, runs in rep["scenarios"].items():
            cap, clim = key.split("|")
            if cap != "dryland":
                self.add(f"scenario.{key}.cap_mm", f"The irrigation limit in this scenario is {CAPS[cap]} mm per season.",
                         CAPS[cap], "mm", "MODEL", scenario=key)
            if clim == "hotdry":
                self.add(f"scenario.{key}.warming_c", "The hotter, drier scenario adds 1.5 °C of warming.", 1.5, "c",
                         "MODEL", scenario=key)
                self.add(f"scenario.{key}.rain_cut_pct", "The hotter, drier scenario cuts rain by 15%.", 15, "pct",
                         "MODEL", scenario=key)
            for rid in ROT_IDS:
                run = runs.get(rid)
                if not run:
                    continue
                nm = rot_names[rid]
                pre = f"replay.{rid}.{key}"
                if not run["feasible"]:
                    self.add(f"{pre}.feasible", f"The {nm} rotation is not feasible with this water limit.",
                             None, None, "MODEL", key, rid)
                    continue
                s = run["summary"]
                lead = f"The {nm} rotation, replayed over 2000 to 2025, "
                rows = [
                    ("irrigation_mm_mean", f"{lead}used an average of {s['irrigation_mm_mean']} mm of irrigation per year.",
                     s["irrigation_mm_mean"], "mm"),
                    ("revenue_usd_ac_mean", f"{lead}earned an average of ${s['revenue_usd_ac_mean']}/ac per year.",
                     s["revenue_usd_ac_mean"], "usd_ac"),
                    ("revenue_usd_ac_worst5",
                     f"{lead}earned an average of ${s['revenue_usd_ac_worst5']}/ac in its 5 worst years.",
                     s["revenue_usd_ac_worst5"], "usd_ac"),
                    ("stress_days_mean", f"{lead}had {s['stress_days_mean']} days per year of crop water stress.",
                     s["stress_days_mean"], "days"),
                    ("bare_windy_days_mean",
                     f"{lead}had {s['bare_windy_days_mean']} days per year with bare soil and strong wind.",
                     s["bare_windy_days_mean"], "days"),
                ]
                sh = soil.get((key, rid))
                if sh is not None:
                    rows.append(("soil_health_score", f"The {nm} rotation has a soil health score of {sh} out of 100.",
                                 sh, None))
                for k, text, val, unit in rows:
                    self.add(f"{pre}.{k}", text, val, unit, "MODEL", key, rid)
        runs = rep["scenarios"].get(SCENARIO, {})
        years = sorted(rep["drought_years"], key=lambda y: (y != 2012, -y))[:DROUGHT_PICKS]
        for rid in ROT_IDS:
            run = runs.get(rid)
            if not run or not run["feasible"]:
                continue
            by = {y["year"]: y for y in run["by_year"]}
            for y in years:
                if y not in by:
                    continue
                r = by[y]
                nm = rot_names[rid]
                self.add(f"drought.{y}.{rid}.revenue_usd_ac",
                         f"In the drought year {y}, the {nm} rotation would have earned about ${r['revenue_usd_ac']}/ac.",
                         r["revenue_usd_ac"], "usd_ac", "MODEL", SCENARIO, rid)
                self.add(f"drought.{y}.{rid}.stress_days",
                         f"In {y}, the {nm} rotation would have had about {r['stress_days']} days of crop water stress.",
                         r["stress_days"], "days", "MODEL", SCENARIO, rid)


def rotation_names(rotations: dict, current: dict) -> dict[str, str]:
    names = {r["id"]: crops_phrase([s["crop"] for s in r["steps"]]) for r in rotations["rotations"]}
    names["R0"] = crops_phrase([s["crop"] for s in current["steps"]]) + " (current)"
    return names


def build_field(fid: str, model_web: Path) -> dict:
    b = Builder(fid, model_web)
    fld = next(f for f in load(DATA_WEB / "fields.json")["fields"] if f["id"] == fid)
    summ = b.read_model("summary.json")
    names = rotation_names(load(model_web / "rotations.json"), summ["current_rotation"])
    b.field_basics(fld)
    b.climate(summ)
    b.water()
    b.neighbors()
    b.validation()
    b.replay(names)
    b.glossary()
    ids = [f["id"] for f in b.facts]
    assert len(ids) == len(set(ids)), "duplicate fact ids"
    return {
        "_meta": {"schema": "assistant_context@1", "mock": b.mock,
                  "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                  "generator": "model/assistant/context.py"},
        "field_id": fid,
        "field_name": fld["name"]["en"],
        "rotation_names": names,
        "facts": b.facts,
    }


def facts_for(doc: dict, scenario: str) -> list[dict]:
    return [f for f in doc["facts"] if f.get("scenario") in (None, scenario)]


def facts_block(facts: list[dict]) -> str:
    return "\n".join(f"- ({f['id']}) {f['text']} [{f['source']}]" for f in facts)


def est_tokens(doc: dict, scenario: str) -> int:
    return len(facts_block(facts_for(doc, scenario))) // 4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-web", type=Path, default=OUT_WEB)
    ap.add_argument("--out", type=Path, default=OUT_WEB)
    ap.add_argument("--standins", action="store_true", help="use README-shaped stand-ins for model-core files")
    a = ap.parse_args()
    if a.standins:
        import standins
        tmp = Path(tempfile.mkdtemp(prefix="fs_standins_"))
        standins.make(tmp, {"f1": True, "f2": False, "f3": True})
        a.model_web = tmp
    for fid in FIELDS:
        doc = build_field(fid, a.model_web)
        out = a.out / "field" / fid / "assistant_context.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf8")
        worst = max(est_tokens(doc, f"{c}|{k}") for c in CAPS for k in ("actual", "hotdry"))
        print(f"{fid}: {len(doc['facts'])} facts, ~{est_tokens(doc, SCENARIO)} tokens at {SCENARIO}, "
              f"worst ~{worst}, mock={doc['_meta']['mock']}")


if __name__ == "__main__":
    main()
