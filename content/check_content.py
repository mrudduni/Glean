import json, re, sys, os

root = sys.argv[1]
C = os.path.join(root, "content")
D = os.path.join(root, "design")
errs = []


def load(p):
    return json.load(open(p, encoding="utf-8"))


ct = load(os.path.join(C, "card_text.json"))
crit = {
    "water_use": ["irrigation_mm", "saved_mm"],
    "income_mean": ["revenue_usd_ac", "diff_usd_ac"],
    "income_worst": ["worst5_usd_ac", "r0_worst5_usd_ac"],
    "soil_health": ["score", "living_root_days", "legume_years"],
    "water_erosion": ["bare_storm_days", "r0_bare_storm_days"],
    "wind_erosion": ["bare_windy_days", "r0_bare_windy_days"],
    "pest_break": ["max_run_years", "r0_max_run_years"],
    "heat_frost_risk": ["heat_days", "r0_heat_days"],
}
cat = {
    "why": crit,
    "benefits": {
        "water_saved": ["saved_mm"], "bare_days_reduced": ["days"],
        "legume_added": ["legume_years", "cycle_years"], "income_steadier": ["worst5_gain_usd_ac"],
        "pest_cycle_broken": ["max_run_years"], "forage_income": ["forage_crop"],
    },
    "evidence": {
        "replay_avg": ["years_from", "years_to", "irrigation_mm", "revenue_usd_ac"],
        "replay_drought": ["year", "irrigation_mm", "r0_irrigation_mm"],
        "neighbors": ["n", "et_mm", "r0_et_mm"], "validation_et": ["bias_pct"],
    },
    "gaps": {k: [] for k in "no_pest_data costs_not_modelled prices_constant openet_record_short smap_coarse county_yields neighbors_observational model_simplified crop_params_generic".split()},
    "risks": {k: [] for k in "herbicide_carryover buyer_availability crop_insurance water_rights equipment_access cover_establishment alfalfa_stand_water fallow_wind new_crop_learning seed_availability".split()},
    "infeasible": {k: [] for k in "needs_more_water needs_equipment no_local_market".split()},
    "headline": {
        "grace_trend": ["cm_per_yr"], "well_trend": ["m_per_yr"], "frost_free_change": ["days"],
        "heat_days_change": ["days"], "current_rotation": ["years_from", "years_to"],
    },
    "validation": {
        "et_vs_openet": ["bias_pct"], "sm_vs_smap": ["r"],
        "precip_power_vs_imerg": ["bias_pct"], "precip_vs_cocorahs": ["bias_pct"],
    },
}
ph = re.compile(r"\{([a-z0-9_]+)\}")


def chk_loc(path, v, allowed=None):
    if not isinstance(v, dict) or set(v) != {"en", "es"}:
        errs.append(f"{path}: not Localized")
        return
    for lang in ("en", "es"):
        s = v[lang]
        if not s:
            errs.append(f"{path}.{lang}: empty")
        if allowed is not None:
            for p in ph.findall(s):
                if p not in allowed:
                    errs.append(f"{path}.{lang}: placeholder {{{p}}} not allowed {allowed}")
    if allowed is not None and set(ph.findall(v["en"])) != set(ph.findall(v["es"])):
        errs.append(f"{path}: en/es placeholders differ")


for sec, keys in cat.items():
    got = ct.get(sec, {})
    for k, allowed in keys.items():
        if k not in got:
            errs.append(f"card_text.{sec}.{k} missing")
            continue
        chk_loc(f"card_text.{sec}.{k}", got[k], allowed)
    for k in got:
        if k not in keys:
            errs.append(f"card_text.{sec}.{k} not in catalog")
for k in crit:
    if k not in ct["criteria_labels"]:
        errs.append(f"criteria_labels.{k} missing")
    else:
        chk_loc(f"criteria_labels.{k}", ct["criteria_labels"][k], [])
for r in [f"R{i}" for i in range(7)]:
    if r not in ct["rotations"]:
        errs.append(f"rotations.{r} missing")
    else:
        for f in ("name", "tagline"):
            chk_loc(f"rotations.{r}.{f}", ct["rotations"][r][f], [])

unit_next = re.compile(r"\{[a-z0-9_]*(_mm|_usd_ac|_pct|_cm_per_yr|_m_per_yr)\}\s*(mm|in\b|%|/ac|cm|m\b)")
for sec, d in ct.items():
    if sec == "_meta":
        continue
    for k, v in d.items():
        locs = [v] if "en" in v else list(v.values())
        for loc in locs:
            for lang, s in loc.items():
                if unit_next.search(s) or "${" in s:
                    errs.append(f"{sec}.{k}.{lang}: unit typed next to placeholder")

copy_keys = """app.name app.tagline disclaimer.main banner.mock lang.en lang.es
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
assistant.title assistant.placeholder assistant.send assistant.suggested assistant.verified assistant.unverified assistant.using_cache assistant.error""".split()
cp = load(os.path.join(C, "copy.json"))["strings"]
for k in copy_keys:
    if k not in cp:
        errs.append(f"copy.{k} missing")
    else:
        chk_loc(f"copy.{k}", cp[k])
extra = set(cp) - set(copy_keys)
if extra:
    errs.append(f"copy: extra keys {sorted(extra)}")

gl = load(os.path.join(C, "glossary.json"))["terms"]
gids = "et et0 ndvi soil_moisture_anomaly root_zone frost_risk gdd water_balance evaporative_stress aquifer rotation cover_crop fallow nitrogen_fixing wind_erosion water_erosion satellite_vs_ground model_estimate".split()
have = [t["id"] for t in gl]
for g in gids:
    if g not in have:
        errs.append(f"glossary {g} missing")
for t in gl:
    for f in ("term", "short", "long"):
        chk_loc(f"glossary.{t['id']}.{f}", t[f])

qs = load(os.path.join(C, "assistant_questions.json"))["questions"]
if [q["id"] for q in qs] != [f"q{i}" for i in range(1, 7)]:
    errs.append("questions ids wrong")
for q in qs:
    chk_loc(f"questions.{q['id']}", q["text"])

try:
    import yaml
    cr = yaml.safe_load(open(os.path.join(C, "crops.yaml"), encoding="utf-8"))
    crops = "corn sorghum wheat soybean alfalfa triticale rye_cover cotton fallow".split()
    fields = "name family host_group season plant_window harvest_window stage_days kc root_max_m p ky heat frost_kill_c requires_irrigation n_fixing residue root_type forage yield price equipment sources".split()
    if sorted(cr) != sorted(crops):
        errs.append(f"crops.yaml crops: {sorted(cr)}")
    print("crops.yaml stage totals:")
    for c in crops:
        for f in fields:
            if f not in cr.get(c, {}):
                errs.append(f"crops.{c}.{f} missing")
        sd = cr[c]["stage_days"]
        print(f"  {c:10s} {sum(sd.values()):4d} days  season={cr[c]['season']}")
except ImportError:
    print("pyyaml not installed; skipped crops.yaml")
    errs.append("crops.yaml not checked (no pyyaml)")

css = open(os.path.join(D, "tokens.css"), encoding="utf-8").read()
root_block = css.split("[data-theme")[0]
cssvars = {k: v.strip() for k, v in re.findall(r"--([a-zA-Z0-9_-]+):\s*([^;]+);", root_block)}
req = "color-bg color-surface color-fg color-muted color-border color-accent color-good color-fair color-limited crop-corn crop-sorghum crop-wheat crop-soybean crop-alfalfa crop-triticale crop-rye_cover crop-cotton crop-fallow crop-bare rot-R0 rot-R1 rot-R2 rot-R3 rot-R4 rot-R5 rot-R6 risk-heat risk-frost risk-dry risk-storm risk-wind font-display font-body font-mono radius".split()
for r in req:
    if r not in cssvars:
        errs.append(f"tokens.css --{r} missing")
tj = load(os.path.join(D, "tokens.json"))
for grp in ("color", "crop", "rot", "risk"):
    for k, v in tj[grp].items():
        cv = cssvars.get(f"{grp}-{k}")
        if cv is None or cv.upper() != v.upper():
            errs.append(f"tokens mismatch {grp}.{k}: css={cv} json={v}")


def lum(h):
    h = h.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    rgb = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def ratio(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def contrast_set(label, pal, pairs):
    print(f"contrast ({label}):")
    for fg, bg, need in pairs:
        r = ratio(pal[fg], pal[bg])
        ok = r >= need
        print(f"  {fg:8s} on {bg:8s} {r:5.2f}  need {need}  {'OK' if ok else 'FAIL'}")
        if not ok:
            errs.append(f"{label} contrast {fg}/{bg} {r:.2f}")


pairs = [("fg", "bg", 4.5), ("fg", "surface", 4.5), ("muted", "surface", 4.5), ("muted", "bg", 4.5),
         ("accent", "surface", 4.5), ("accent", "bg", 4.5), ("good", "surface", 3), ("fair", "surface", 3), ("limited", "surface", 3)]
contrast_set("light", tj["color"], pairs)
contrast_set("dark", {**tj["color"], **tj["dark"]["color"]}, pairs)
print("crop cell text contrast:")
for c, h in tj["crop"].items():
    t = tj["crop_text"][c]
    r = ratio(h, t)
    print(f"  {c:10s} {r:5.2f}  {'OK' if r >= 4.5 else 'LOW'}")
    if r < 4.5:
        errs.append(f"crop text contrast {c} {r:.2f}")
print("rotation lines vs surface (need 3 for chart marks):")
for k, h in tj["rot"].items():
    r = ratio(h, tj["color"]["surface"])
    print(f"  {k} {r:5.2f}  {'OK' if r >= 3 else 'LOW'}")

print("\nALL CHECKS PASSED" if not errs else "\nERRORS:")
for e in errs:
    print(" -", e)
