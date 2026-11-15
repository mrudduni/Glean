#!/usr/bin/env python3
"""Check U-role files against the Glean contract (README 7.4, 8.5, 8.6).

Run from the repo root:  python content/validate.py
Needs: pyyaml (only for crops.yaml).  Exit code 1 if any error.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []
warnings: list[str] = []


def err(msg):
    errors.append(msg)


def load(path):
    p = ROOT / path
    if not p.exists():
        err(f"{path}: missing")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err(f"{path}: bad JSON ({e})")
        return None


# ---------- key catalog (README 8.6) ----------
ROT = [f"R{i}" for i in range(7)]
CRITERIA = ["water_use", "income_mean", "income_worst", "soil_health",
            "water_erosion", "wind_erosion", "pest_break", "heat_frost_risk"]
WHY_VARS = {
    "water_use": {"irrigation_mm", "saved_mm"},
    "income_mean": {"revenue_usd_ac", "diff_usd_ac"},
    "income_worst": {"worst5_usd_ac", "r0_worst5_usd_ac"},
    "soil_health": {"score", "living_root_days", "legume_years"},
    "water_erosion": {"bare_storm_days", "r0_bare_storm_days"},
    "wind_erosion": {"bare_windy_days", "r0_bare_windy_days"},
    "pest_break": {"max_run_years", "r0_max_run_years"},
    "heat_frost_risk": {"heat_days", "r0_heat_days"},
}
# The catalog lists `irrigation_mm` and `saved_mm` only for water_use, but the
# README example for heat_frost_risk also uses `heat_days`. Vars stay as listed.
SECTIONS = {
    "benefits": {
        "water_saved": {"saved_mm"}, "bare_days_reduced": {"days"},
        "legume_added": {"legume_years", "cycle_years"},
        "income_steadier": {"worst5_gain_usd_ac"},
        "pest_cycle_broken": {"max_run_years"}, "forage_income": {"forage_crop"},
    },
    "evidence": {
        "replay_avg": {"years_from", "years_to", "irrigation_mm", "revenue_usd_ac"},
        "replay_drought": {"year", "irrigation_mm", "r0_irrigation_mm"},
        "neighbors": {"n", "et_mm", "r0_et_mm"},
        "validation_et": {"bias_pct"},
    },
    "gaps": {k: set() for k in
             "no_pest_data costs_not_modelled prices_constant openet_record_short smap_coarse "
             "county_yields neighbors_observational model_simplified crop_params_generic".split()},
    "risks": {k: set() for k in
              "herbicide_carryover buyer_availability crop_insurance water_rights equipment_access "
              "cover_establishment alfalfa_stand_water fallow_wind new_crop_learning seed_availability".split()},
    "infeasible": {k: set() for k in "needs_more_water needs_equipment no_local_market".split()},
    "headline": {
        "grace_trend": {"cm_per_yr"}, "well_trend": {"m_per_yr"},
        "frost_free_change": {"days"}, "heat_days_change": {"days"},
        "current_rotation": {"years_from", "years_to"},
    },
    "validation": {
        "et_vs_openet": {"bias_pct"}, "sm_vs_smap": {"r"},
        "precip_power_vs_imerg": {"bias_pct"}, "precip_vs_cocorahs": {"bias_pct"},
    },
}
COPY_KEYS = """
app.name app.tagline disclaimer.main banner.mock lang.en lang.es
nav.overview nav.calendar nav.plan nav.replay nav.neighbors nav.trust
pick.title pick.subtitle pick.open_field
overview.current_rotation overview.detected_from overview.soil overview.climate_shift overview.water_outlook
overview.outlook.declining overview.outlook.stable overview.outlook.rising
priorities.title priorities.save_water priorities.income priorities.steady_income priorities.soil_health priorities.erosion
constraints.title constraints.water_cap constraints.cap.dryland constraints.cap.cap150 constraints.cap.cap300 constraints.cap.cap450
constraints.hay_equipment constraints.cotton_equipment constraints.forage_buyer
climate.title climate.actual climate.hotdry
card.why card.evidence card.benefits card.gaps card.risks card.current_badge card.score card.confidence card.hidden_count
calendar.title calendar.subtitle calendar.bare calendar.flag.heat calendar.flag.frost calendar.flag.dry calendar.flag.bare_storm calendar.flag.bare_wind
replay.title replay.subtitle replay.metric.irrigation replay.metric.revenue replay.metric.stress replay.metric.bare replay.drought_marker
neighbors.title neighbors.subtitle neighbors.disclaimer neighbors.n_fields neighbors.water_use neighbors.drought_greenness
trust.title trust.subtitle trust.level.good trust.level.fair trust.level.limited trust.sources trust.glossary
assistant.title assistant.placeholder assistant.send assistant.suggested assistant.verified assistant.unverified assistant.using_cache assistant.error
""".split()
# README gives no var list for copy keys. Only these two use a placeholder.
COPY_VARS = {"card.hidden_count": {"n"}, "neighbors.n_fields": {"n"}, "calendar.odds": {"risk", "count"},
             "years.range": {"years_from", "years_to"}, "card.shown_at": {"cap"},
             "card.unlock_tick": {"option"}, "card.unlock_cap": {"option"}}
GLOSSARY_IDS = """et et0 ndvi soil_moisture_anomaly root_zone frost_risk gdd water_balance evaporative_stress
aquifer rotation cover_crop fallow nitrogen_fixing wind_erosion water_erosion satellite_vs_ground model_estimate""".split()
CROPS = "corn sorghum wheat soybean alfalfa triticale rye_cover cotton fallow".split()

# ---------- text rules ----------
BANNED_EN = re.compile(r"\b(will|guaranteed?|guarantees|proven|prove|proves|best)\b", re.I)
BANNED_ES = re.compile(r"\b(garantiz\w*|comprobado|demostrado|el mejor|la mejor|los mejores|las mejores)\b", re.I)
EM_DASH = "—"
PLACEHOLDER = re.compile(r"\{([a-z0-9_]+)\}")
UNIT_AFTER = re.compile(r"\{[a-z0-9_]+\}\s?(mm|in|inches|cm|m|ft|ac|acres|bu|%|°C|°F|usd|dollars)\b", re.I)
UNIT_BEFORE = re.compile(r"(\$|US\$)\s?\{")
SKIP_UNIT_CHECK = set()


def check_text(where, loc, allowed):
    """loc is a Localized dict. Checks both languages."""
    if not isinstance(loc, dict) or "en" not in loc or "es" not in loc:
        err(f"{where}: needs en and es")
        return
    en, es = loc["en"], loc["es"]
    if not en.strip():
        err(f"{where}: empty en")
    if not es.strip():
        warnings.append(f"{where}: empty es (falls back to en)")
    for lang, s in (("en", en), ("es", es)):
        if EM_DASH in s:
            err(f"{where}.{lang}: em dash")
        used = set(PLACEHOLDER.findall(s))
        bad = used - allowed
        if bad:
            err(f"{where}.{lang}: placeholder(s) not allowed here: {sorted(bad)}")
        if re.search(r"\{[^a-z0-9_}]|\{\}|[^{]\}[a-z]", s) and not used:
            pass
        if UNIT_AFTER.search(s) or UNIT_BEFORE.search(s):
            err(f"{where}.{lang}: unit next to placeholder: {s[:70]}")
        if s.count("{") != s.count("}"):
            err(f"{where}.{lang}: unbalanced braces")
    if es.strip():
        if set(PLACEHOLDER.findall(en)) != set(PLACEHOLDER.findall(es)):
            warnings.append(f"{where}: en and es use different placeholders")
    m = BANNED_EN.search(en)
    if m:
        err(f"{where}.en: banned word '{m.group(0)}'")
    m = BANNED_ES.search(es)
    if m:
        err(f"{where}.es: banned word '{m.group(0)}'")


def check_meta(name, d, schema):
    m = d.get("_meta", {})
    if m.get("schema") != schema or m.get("mock") is not False or not m.get("generated_at") or not m.get("generator"):
        err(f"{name}: bad _meta (want schema {schema}, mock false, generated_at, generator)")


def check_keys(name, got, want, extra_ok=False):
    got, want = set(got), set(want)
    for k in sorted(want - got):
        err(f"{name}: missing key {k}")
    if not extra_ok:
        for k in sorted(got - want):
            err(f"{name}: unexpected key {k}")


def check_card_text():
    d = load("content/card_text.json")
    if d is None:
        return
    check_meta("card_text", d, "card_text@1")
    check_keys("card_text", [k for k in d if k != "_meta"],
              ["rotations", "criteria_labels", "why", *SECTIONS])
    check_keys("card_text.rotations", d.get("rotations", {}), ROT)
    for r, v in d.get("rotations", {}).items():
        check_keys(f"card_text.rotations.{r}", v, ["name", "tagline"])
        for f in ("name", "tagline"):
            check_text(f"card_text.rotations.{r}.{f}", v.get(f), set())
    check_keys("card_text.criteria_labels", d.get("criteria_labels", {}), CRITERIA)
    for k, v in d.get("criteria_labels", {}).items():
        check_text(f"card_text.criteria_labels.{k}", v, set())
    check_keys("card_text.why", d.get("why", {}), CRITERIA)
    for k, v in d.get("why", {}).items():
        check_text(f"card_text.why.{k}", v, WHY_VARS.get(k, set()))
    for sec, keys in SECTIONS.items():
        check_keys(f"card_text.{sec}", d.get(sec, {}), keys)
        for k, v in d.get(sec, {}).items():
            check_text(f"card_text.{sec}.{k}", v, keys.get(k, set()))


def check_copy():
    d = load("content/copy.json")
    if d is None:
        return
    check_meta("copy", d, "copy@1")
    s = d.get("strings", {})
    check_keys("copy.strings", s, COPY_KEYS, extra_ok=True)
    for k, v in s.items():
        check_text(f"copy.{k}", v, COPY_VARS.get(k, set()))
    if s.get("app.name", {}).get("en") != "Glean":
        err("copy: app.name must be 'Glean'")


def check_glossary():
    d = load("content/glossary.json")
    if d is None:
        return
    check_meta("glossary", d, "glossary@1")
    ids = [t.get("id") for t in d.get("terms", [])]
    check_keys("glossary", ids, GLOSSARY_IDS, extra_ok=True)
    if len(ids) != len(set(ids)):
        err("glossary: duplicate ids")
    for t in d.get("terms", []):
        for f in ("term", "short", "long"):
            check_text(f"glossary.{t.get('id')}.{f}", t.get(f), set())
        sentences = len(re.findall(r"[.!?](\s|$)", t.get("short", {}).get("en", "")))
        if sentences != 1:
            warnings.append(f"glossary.{t.get('id')}.short: should be one sentence (found {sentences})")


def check_questions():
    d = load("content/assistant_questions.json")
    if d is None:
        return
    check_meta("assistant_questions", d, "assistant_questions@1")
    qs = d.get("questions", [])
    check_keys("assistant_questions", [q.get("id") for q in qs], [f"q{i}" for i in range(1, 7)])
    for q in qs:
        check_text(f"assistant_questions.{q.get('id')}", q.get("text"), set())


def check_crops():
    try:
        import yaml
    except ImportError:
        err("crops.yaml: pyyaml not installed, cannot check")
        return
    p = ROOT / "content/crops.yaml"
    if not p.exists():
        err("content/crops.yaml: missing")
        return
    text = p.read_text(encoding="utf-8")
    d = yaml.safe_load(text)
    check_keys("crops.yaml", d, CROPS)
    fields = ["name", "family", "host_group", "season", "plant_window", "harvest_window", "stage_days", "kc",
              "root_max_m", "p", "ky", "heat", "frost_kill_c", "requires_irrigation", "n_fixing", "residue",
              "root_type", "forage", "yield", "price", "equipment", "sources"]
    for c, v in (d or {}).items():
        check_keys(f"crops.{c}", v, fields)
        if not v.get("sources"):
            err(f"crops.{c}: sources empty")
        if v.get("season") not in ("summer", "winter", "perennial", "cover", "none"):
            err(f"crops.{c}: bad season")
        if v.get("residue") not in ("low", "medium", "high"):
            err(f"crops.{c}: bad residue")
        if v.get("root_type") not in ("fibrous", "tap", "deep_tap") and c != "fallow":
            err(f"crops.{c}: bad root_type")
        n = v.get("name", {})
        if not (n.get("en") and n.get("es")):
            err(f"crops.{c}: name en/es")
        if c != "fallow":
            kc = v.get("kc") or {}
            for k in ("ini", "mid", "end"):
                if kc.get(k) is None:
                    err(f"crops.{c}: kc.{k} null")
        for w in ("plant_window", "harvest_window"):
            for e in ("start", "end"):
                val = (v.get(w) or {}).get(e)
                if val is not None and not re.fullmatch(r"\d\d-\d\d", str(val)):
                    err(f"crops.{c}.{w}.{e}: want MM-DD, got {val}")
        if "—" in text:
            pass
    if "—" in text:
        err("crops.yaml: em dash")
    # every number-bearing crop should name a source containing FAO or K-State
    todo = text.count("# verify")
    if todo:
        warnings.append(f"crops.yaml: {todo} values marked '# verify'")


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lum(rgb):
    def f(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = lum(hex_to_rgb(a)), lum(hex_to_rgb(b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


TOKEN_GROUPS = {
    "color": "bg surface fg muted border accent good fair limited".split(),
    "crop": "corn sorghum wheat soybean alfalfa triticale rye_cover cotton fallow bare".split(),
    "rot": ROT,
    "risk": "heat frost dry storm wind".split(),
    "font": "display body mono".split(),
}


def check_tokens():
    tj = load("design/tokens.json")
    p = ROOT / "design/tokens.css"
    if tj is None or not p.exists():
        if not p.exists():
            err("design/tokens.css: missing")
        return
    css = p.read_text(encoding="utf-8")
    blocks = re.split(r"(?=^\s*[:\[][^{]*\{)", css, flags=re.M)
    root_decl, dark_decl = {}, {}
    for b in blocks:
        m = re.match(r"\s*([^{]+)\{(.*?)\}", b, re.S)
        if not m:
            continue
        sel, body = m.group(1).strip(), m.group(2)
        decl = dict(re.findall(r"--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);", body))
        decl = {k: v.strip() for k, v in decl.items()}
        if sel == ":root":
            root_decl.update(decl)
        elif 'data-theme="dark"' in sel:
            dark_decl.update(decl)
    need = [f"{g}-{k}" for g in ("color", "crop", "rot", "risk", "font") for k in TOKEN_GROUPS[g]] + ["radius"]
    for n in need:
        if n not in root_decl:
            err(f"tokens.css: missing --{n}")
    for g, keys in TOKEN_GROUPS.items():
        for k in keys:
            jv = (tj.get(g) or {}).get(k)
            if jv is None:
                err(f"tokens.json: missing {g}.{k}")
            elif root_decl.get(f"{g}-{k}") is not None and root_decl[f"{g}-{k}"].lower() != str(jv).lower():
                err(f"tokens: --{g}-{k} css '{root_decl[f'{g}-{k}']}' != json '{jv}'")
    # contrast (light)
    c = tj.get("color", {})
    pairs = [("fg", "bg", 4.5), ("fg", "surface", 4.5), ("muted", "bg", 4.5), ("muted", "surface", 4.5),
             ("accent", "bg", 4.5), ("accent", "surface", 4.5)]
    for a, b, need_ratio in pairs:
        if a in c and b in c and contrast(c[a], c[b]) < need_ratio:
            err(f"tokens: contrast {a} on {b} = {contrast(c[a], c[b]):.2f} (< {need_ratio})")
    for lvl in ("good", "fair", "limited"):
        if lvl in c and "surface" in c and contrast(c[lvl], c["surface"]) < 4.5:
            err(f"tokens: trust colour {lvl} on surface = {contrast(c[lvl], c['surface']):.2f} (< 4.5)")
    # dark theme, if present, must carry the same colour names that matter for text
    if dark_decl:
        for n in ("color-bg", "color-surface", "color-fg", "color-muted", "color-accent"):
            if n not in dark_decl:
                err(f"tokens.css dark: missing --{n}")
        if all(f"color-{k}" in dark_decl for k in ("bg", "fg", "muted", "surface", "accent")):
            for a, b in (("fg", "bg"), ("fg", "surface"), ("muted", "bg"), ("muted", "surface"), ("accent", "bg")):
                r = contrast(dark_decl[f"color-{a}"], dark_decl[f"color-{b}"])
                if r < 4.5:
                    err(f"tokens dark: contrast {a} on {b} = {r:.2f} (< 4.5)")
    # crop and risk marks: 3:1 against surface, rot lines 3:1
    for g in ("rot", "risk"):
        for k, v in tj.get(g, {}).items():
            if "surface" in c and contrast(v, c["surface"]) < 3.0:
                err(f"tokens: {g}.{k} {v} on surface = {contrast(v, c['surface']):.2f} (< 3.0)")
    # dark text on every crop fill >= 4.5
    for k, v in tj.get("crop", {}).items():
        if "fg" in c and contrast(v, c["fg"]) < 4.5:
            err(f"tokens: dark text on crop.{k} = {contrast(v, c['fg']):.2f} (< 4.5)")


def check_docs():
    for f in ("docs/SUBMISSION.md", "docs/PITCH.md"):
        p = ROOT / f
        if not p.exists():
            err(f"{f}: missing")
            continue
        t = p.read_text(encoding="utf-8")
        if EM_DASH in t:
            err(f"{f}: em dash")
        m = BANNED_EN.search(t)
        if m:
            err(f"{f}: banned word '{m.group(0)}' near: {t[max(0, m.start() - 30):m.end() + 30]!r}")


if __name__ == "__main__":
    only = set(sys.argv[1:])
    checks = {"card_text": check_card_text, "copy": check_copy, "glossary": check_glossary,
              "questions": check_questions, "crops": check_crops, "tokens": check_tokens, "docs": check_docs}
    for name, fn in checks.items():
        if not only or name in only:
            fn()
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)
