"""Check web/public/data against the README data contract (handover 5.9). Exit 1 on any error.

Usage: python scripts/check_contract.py [--data-dir web/public/data] [--allow-mock] [--only-model]
  --allow-mock  mock files are warnings instead of errors
  --only-model  check only the files M produces (useful before D's and U's files are synced);
                text keys fall back to the README 8.6 catalog if card_text.json is absent
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELD_IDS = ["f1", "f2", "f3"]
CROP_IDS = {"corn", "sorghum", "wheat", "soybean", "alfalfa", "triticale", "rye_cover", "cotton", "fallow"}
ROTATION_IDS = {"R0", "R1", "R2", "R3", "R4", "R5", "R6"}
REQUIRED_ROTATIONS = ["R0", "R1", "R2", "R3", "R4", "R5"]
SCENARIOS = [f"{c}|{k}" for c in ("dryland", "cap150", "cap300", "cap450") for k in ("actual", "hotdry")]
SOURCE_TAGS = {"POWER", "IMERG", "SMAP", "MODIS", "HLS", "ECOSTRESS", "GRACE", "SRTM", "SSURGO", "CSB", "NASS",
               "OpenET", "PRISM", "USGS", "CoCoRaHS", "GAEZ", "AMS", "FAO56", "MODEL"}
CRITERIA = ["water_use", "income_mean", "income_worst", "soil_health", "water_erosion", "wind_erosion",
            "pest_break", "heat_frost_risk"]
MAX_BYTES = 2 * 1024 * 1024

D_FILES = ["fields.json", "sources.json"] + [f"field/{{fid}}/{n}.json" for n in ("water", "observed", "neighbors")]
M_FILES = ["crops.json", "rotations.json", "assistant/prompt.json"] + [
    f"field/{{fid}}/{n}.json" for n in ("summary", "calendar", "replay", "strategies", "validation",
                                        "assistant_context", "assistant_cache")]
U_FILES = [f"content/{n}.json" for n in ("card_text", "copy", "glossary", "assistant_questions")]

# README 8.6, used only when card_text.json is not available (--only-model)
CATALOG = {
    "why": {k: [] for k in CRITERIA},
    "benefits": {k: [] for k in ("water_saved", "bare_days_reduced", "legume_added", "income_steadier",
                                 "pest_cycle_broken", "forage_income")},
    "evidence": {k: [] for k in ("replay_avg", "replay_drought", "neighbors", "validation_et")},
    "gaps": {k: [] for k in ("no_pest_data", "costs_not_modelled", "prices_constant", "openet_record_short",
                             "smap_coarse", "county_yields", "neighbors_observational", "model_simplified",
                             "crop_params_generic")},
    "risks": {k: [] for k in ("herbicide_carryover", "buyer_availability", "crop_insurance", "water_rights",
                              "equipment_access", "cover_establishment", "alfalfa_stand_water", "fallow_wind",
                              "new_crop_learning", "seed_availability")},
    "infeasible": {k: [] for k in ("needs_more_water", "needs_equipment", "no_local_market")},
    "headline": {k: [] for k in ("grace_trend", "well_trend", "frost_free_change", "heat_days_change", "current_rotation")},
    "validation": {k: [] for k in ("et_vs_openet", "sm_vs_smap", "precip_power_vs_imerg", "precip_vs_cocorahs")},
}
PLACEHOLDER = re.compile(r"\{([a-zA-Z0-9_]+)\}")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def _reject_constant(name: str):
    raise ValueError(f"non-JSON constant {name}")


def load(path: Path, rep: Report, rel: str, allow_mock: bool) -> dict | None:
    if not path.exists():
        rep.err(f"missing file: {rel}")
        return None
    size = path.stat().st_size
    if size > MAX_BYTES:
        rep.err(f"{rel}: {size / 1e6:.1f} MB is over the 2 MB limit")
    try:
        data = json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)
    except ValueError as e:
        rep.err(f"{rel}: invalid JSON ({e})")
        return None
    if not isinstance(data, dict) or "_meta" not in data:
        rep.err(f"{rel}: no _meta block")
        return data
    if next(iter(data)) != "_meta":
        rep.warn(f"{rel}: _meta is not the first key")
    if data["_meta"].get("mock"):
        (rep.warn if allow_mock else rep.err)(f"{rel}: _meta.mock is true")
    return data


def walk(obj, path="$"):
    yield path, obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")


def check_templates(section: str, key: str, vars_: dict, text: dict, rep: Report, where: str) -> None:
    sec = text.get(section, {})
    if key not in sec:
        rep.err(f"{where}: text id '{section}.{key}' has no entry in card_text.json")
        return
    tpl = sec[key]
    if not isinstance(tpl, dict):
        return
    for lang, s in tpl.items():
        if not isinstance(s, str):
            continue
        for ph in PLACEHOLDER.findall(s):
            if ph not in vars_:
                rep.err(f"{where}: card_text.{section}.{key}.{lang} uses {{{ph}}} but vars has {sorted(vars_)}")


def check_ids(rel: str, data: dict, rep: Report) -> None:
    for path, v in walk(data):
        last = path.rsplit(".", 1)[-1]
        if last == "field_id" and v not in FIELD_IDS:
            rep.err(f"{rel} {path}: unknown FieldId {v!r}")
        if last == "rotation_id" and v not in ROTATION_IDS:
            rep.err(f"{rel} {path}: unknown RotationId {v!r}")
        if last in ("crop", "cover_after") and v is not None and v not in CROP_IDS:
            rep.err(f"{rel} {path}: unknown CropId {v!r}")
        if last == "state" and isinstance(v, str) and v != "bare" and v not in CROP_IDS:
            rep.err(f"{rel} {path}: unknown calendar state {v!r}")
        if last == "crop_mix" and isinstance(v, dict):
            for c in v:
                if c not in CROP_IDS:
                    rep.err(f"{rel} {path}: unknown CropId {c!r} in crop_mix")
        if last == "crops_without_local_market":
            for c in v:
                if c not in CROP_IDS:
                    rep.err(f"{rel} {path}: unknown CropId {c!r}")


def collect_tags(data: dict) -> set[str]:
    tags = set()
    for path, v in walk(data):
        last = path.rsplit(".", 1)[-1]
        if last == "sources" and isinstance(v, list):
            tags |= {t for t in v if isinstance(t, str)}
        if last in ("source", "tag") and isinstance(v, str):
            tags.add(v)
    return tags


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", type=Path, default=ROOT / "web" / "public" / "data")
    ap.add_argument("--allow-mock", action="store_true")
    ap.add_argument("--only-model", action="store_true")
    a = ap.parse_args(argv)
    base = a.data_dir.resolve()
    rep = Report()

    def files(templates):
        out = []
        for t in templates:
            out += [t.format(fid=f) for f in FIELD_IDS] if "{fid}" in t else [t]
        return out

    wanted = files(M_FILES) if a.only_model else files(D_FILES) + files(M_FILES) + U_FILES
    docs = {rel: load(base / rel, rep, rel, a.allow_mock) for rel in wanted}

    card_path = base / "content" / "card_text.json"
    if card_path.exists():
        text = docs.get("content/card_text.json") or json.loads(card_path.read_text(encoding="utf-8"))
    else:
        if not a.only_model:
            rep.err("content/card_text.json missing: text keys cannot be checked")
        else:
            rep.warn("content/card_text.json not found: checking text ids against the README 8.6 catalog only")
        text = CATALOG
    sources_path = base / "sources.json"
    known_tags = None
    if sources_path.exists():
        src = json.loads(sources_path.read_text(encoding="utf-8"))
        known_tags = {s["tag"] for s in src.get("sources", [])}
    elif not a.only_model:
        rep.err("sources.json missing: source tags cannot be resolved")
    else:
        rep.warn("sources.json not found: source tags checked against README 7.2 only")

    if "rotations" in text:
        for rid in sorted(ROTATION_IDS):
            if rid not in text["rotations"]:
                rep.err(f"card_text.rotations lacks {rid}")

    used_tags: set[str] = set()
    for rel, d in docs.items():
        if not d:
            continue
        check_ids(rel, d, rep)
        if rel != "crops.json":          # CropTraits.sources are free-text citations, not SourceTags
            used_tags |= collect_tags(d)

    for fid in FIELD_IDS:
        rp = docs.get(f"field/{fid}/replay.json")
        if rp:
            for sk in SCENARIOS:
                if sk not in rp.get("scenarios", {}):
                    rep.err(f"replay {fid}: missing scenario {sk}")
                    continue
                for rid in REQUIRED_ROTATIONS:
                    if rid not in rp["scenarios"][sk]:
                        rep.err(f"replay {fid} {sk}: missing {rid}")
            for sk in rp.get("scenarios", {}):
                if sk not in SCENARIOS:
                    rep.err(f"replay {fid}: unknown scenario key {sk}")
        st = docs.get(f"field/{fid}/strategies.json")
        if st:
            for sk in SCENARIOS:
                entries = st.get("scenarios", {}).get(sk)
                if entries is None:
                    rep.err(f"strategies {fid}: missing scenario {sk}")
                    continue
                ids = [e["rotation_id"] for e in entries]
                for rid in REQUIRED_ROTATIONS:
                    if rid not in ids:
                        rep.err(f"strategies {fid} {sk}: missing {rid}")
                for e in entries:
                    w = f"strategies {fid} {sk} {e['rotation_id']}"
                    for c in CRITERIA:
                        if c not in e["criteria"]:
                            rep.err(f"{w}: missing criterion {c}")
                            continue
                        n = e["criteria"][c]["norm"]
                        if not 0 <= n <= 100:
                            rep.err(f"{w}: {c} norm {n} outside 0-100")
                        check_templates("why", c, e["criteria"][c]["vars"], text, rep, w)
                    for b in e["benefits"]:
                        check_templates("benefits", b["text_id"], b["vars"], text, rep, w)
                    for ev in e["evidence"]:
                        check_templates("evidence", ev["text_id"], ev["vars"], text, rep, w)
                    for g in e["gap_ids"]:
                        check_templates("gaps", g, {}, text, rep, w)
                    for r in e["risk_ids"]:
                        check_templates("risks", r, {}, text, rep, w)
                    if e["infeasible_reason_id"]:
                        check_templates("infeasible", e["infeasible_reason_id"], {}, text, rep, w)
        sm = docs.get(f"field/{fid}/summary.json")
        if sm:
            if len(sm.get("headline_facts", [])) != 3:
                rep.err(f"summary {fid}: expected 3 headline_facts")
            for h in sm.get("headline_facts", []):
                check_templates("headline", h["text_id"], h["vars"], text, rep, f"summary {fid}")
        va = docs.get(f"field/{fid}/validation.json")
        if va:
            for it in va.get("items", []):
                check_templates("validation", it["id"], it["vars"], text, rep, f"validation {fid}")
        cal = docs.get(f"field/{fid}/calendar.json")
        if cal:
            if len(cal.get("climate_risk", [])) != 12:
                rep.err(f"calendar {fid}: climate_risk must have 12 months")
            for r in cal.get("rotations", []):
                for y in r["years"]:
                    if len(y["months"]) != 12:
                        rep.err(f"calendar {fid} {r['rotation_id']} year {y['year_index']}: need 12 months")
        ca = docs.get(f"field/{fid}/assistant_cache.json")
        if ca:
            for q in (f"q{i}" for i in range(1, 7)):
                for lang in ("en", "es"):
                    if lang not in ca.get("answers", {}).get(q, {}):
                        rep.err(f"assistant_cache {fid}: missing {q} {lang}")

    for t in sorted(used_tags):
        if t not in SOURCE_TAGS:
            rep.err(f"source tag {t!r} is not a README 7.2 SourceTag")
        elif known_tags is not None and t not in known_tags:
            rep.err(f"source tag {t!r} is used but missing from sources.json")

    for w in rep.warnings:
        print(f"WARN  {w}")
    for e in rep.errors:
        print(f"FAIL  {e}")
    checked = sum(1 for d in docs.values() if d is not None)
    print(f"\n{checked}/{len(docs)} files read from {base}; {len(rep.errors)} errors, {len(rep.warnings)} warnings")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
