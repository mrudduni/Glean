"""CONTRACT section 8.6 text key catalog and shared JSON writer. M uses only these keys and vars."""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

WHY_VARS = {
    "water_use": ["irrigation_mm", "saved_mm"],
    "income_mean": ["revenue_usd_ac", "diff_usd_ac"],
    "income_worst": ["worst5_usd_ac", "r0_worst5_usd_ac"],
    "soil_health": ["score", "living_root_days", "legume_years"],
    "water_erosion": ["bare_storm_days", "r0_bare_storm_days"],
    "wind_erosion": ["bare_windy_days", "r0_bare_windy_days"],
    "pest_break": ["max_run_years", "r0_max_run_years"],
    "heat_frost_risk": ["heat_days", "r0_heat_days"],
}
BENEFIT_VARS = {
    "water_saved": ["saved_mm"],
    "bare_days_reduced": ["days"],
    "legume_added": ["legume_years", "cycle_years"],
    "income_steadier": ["worst5_gain_usd_ac"],
    "pest_cycle_broken": ["max_run_years"],
    "forage_income": ["forage_crop"],
}
EVIDENCE_VARS = {
    "replay_avg": ["years_from", "years_to", "irrigation_mm", "revenue_usd_ac"],
    "replay_drought": ["year", "irrigation_mm", "r0_irrigation_mm"],
    "neighbors": ["n", "et_mm", "r0_et_mm"],
    "validation_et": ["bias_pct"],
}
GAP_IDS = ["no_pest_data", "costs_not_modelled", "prices_constant", "openet_record_short", "smap_coarse",
           "county_yields", "neighbors_observational", "model_simplified", "crop_params_generic"]
RISK_IDS = ["herbicide_carryover", "buyer_availability", "crop_insurance", "water_rights", "equipment_access",
            "cover_establishment", "alfalfa_stand_water", "fallow_wind", "new_crop_learning", "seed_availability"]
INFEASIBLE_IDS = ["needs_more_water", "needs_equipment", "no_local_market"]
HEADLINE_VARS = {
    "grace_trend": ["cm_per_yr"],
    "well_trend": ["m_per_yr"],
    "frost_free_change": ["days"],
    "heat_days_change": ["days"],
    "current_rotation": ["years_from", "years_to"],
}
VALIDATION_VARS = {
    "et_vs_openet": ["bias_pct"],
    "sm_vs_smap": ["r"],
    "precip_power_vs_imerg": ["bias_pct"],
    "precip_vs_cocorahs": ["bias_pct"],
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def meta(schema: str, generator: str, mock: bool = False) -> dict:
    return {"schema": schema, "mock": mock, "generated_at": now_utc(), "generator": generator}


def _check_finite(obj, path="$"):
    if isinstance(obj, float) and not math.isfinite(obj):
        raise ValueError(f"non-finite number at {path}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            _check_finite(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _check_finite(v, f"{path}[{i}]")


def write_json(path: Path, payload: dict) -> Path:
    """Write payload (which must start with _meta) as compact UTF-8 JSON. Rejects NaN and Infinity."""
    assert next(iter(payload)) == "_meta", f"{path}: _meta must be the first key"
    _check_finite(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    path.write_text(text, encoding="utf-8")
    return path
