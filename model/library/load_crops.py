"""content/crops.yaml -> validated crop dicts with NASS yields and prices filled in; writes crops.json."""
from __future__ import annotations

import copy
import json
import subprocess
from statistics import mean

import yaml

from model import config
from model.contract import meta, write_json

REQUIRED = ["name", "family", "host_group", "season", "plant_window", "harvest_window", "stage_days", "kc",
            "root_max_m", "p", "ky", "heat", "frost_kill_c", "requires_irrigation", "n_fixing", "residue",
            "root_type", "forage", "yield", "price", "equipment", "sources"]
SOLD = ["corn", "sorghum", "wheat", "soybean", "alfalfa", "triticale", "cotton"]


def read_crops_yaml() -> tuple[dict, str]:
    """Return (crops, source label). Order: CONTENT_DIR, the content git branch, the vendored snapshot."""
    path = config.CONTENT_DIR / "crops.yaml"
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8")), str(path)
    try:
        text = subprocess.run(["git", "-C", str(config.REPO_DIR), "show", f"{config.CONTENT_GIT_REF}:content/crops.yaml"],
                              capture_output=True, text=True, encoding="utf-8", check=True).stdout
        return yaml.safe_load(text), f"git {config.CONTENT_GIT_REF}:content/crops.yaml"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return yaml.safe_load(config.DEFAULT_CROPS_YAML.read_text(encoding="utf-8")), str(config.DEFAULT_CROPS_YAML)


def load_nass() -> dict | None:
    path = config.DATA_DIR / "processed" / "nass.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _pick_yield(nass: dict, crop: str, practice: str) -> dict | None:
    """Most local level with >= NASS_MIN_VALUES values; prefer the recent window; mean of the last 5."""
    for prac in (practice, "all"):
        rows = [r for r in nass["yields"] if r["crop"] == crop and r["practice"] == prac and r["year"] <= config.NASS_RECENT_TO]
        for recent_only in (True, False):
            for level in config.NASS_LEVEL_ORDER:
                vals = sorted((r["year"], r["value"]) for r in rows if r["level"] == level
                              and (not recent_only or r["year"] >= config.NASS_RECENT_FROM))
                if len(vals) >= config.NASS_MIN_VALUES:
                    last = vals[-config.NASS_N_YEARS:]
                    return {"value": round(mean(v for _, v in last), 2), "level": level, "practice": prac,
                            "years": [last[0][0], last[-1][0]], "unit": rows[0]["unit"]}
    return None


def _pick_price(nass: dict, crop: str) -> dict | None:
    lo, hi = config.PRICE_YEARS
    for level in ("state", "us"):
        vals = [r["value"] for r in nass["prices"] if r["crop"] == crop and r["level"] == level and lo <= r["year"] <= hi]
        if vals:
            unit = next(r["unit"] for r in nass["prices"] if r["crop"] == crop)
            return {"value": round(mean(vals), 3), "level": level, "years": [lo, hi], "unit": unit, "n": len(vals)}
    return None


def county_market(nass: dict | None) -> dict[str, bool]:
    """A crop has a local market if NASS reports county acres or county yields for it."""
    if nass is None:
        return {c: True for c in SOLD}
    seen = {r["crop"] for r in nass["acres"] if r["level"] == "county"}
    seen |= {r["crop"] for r in nass["yields"] if r["level"] == "county"}
    return {c: c in seen for c in SOLD}


def load_crops() -> tuple[dict, dict]:
    """Return (crops, provenance). crops[cid] has every README 8.5 field plus model-filled yields/prices."""
    raw, source = read_crops_yaml()
    missing = [c for c in config.CROP_IDS if c not in raw]
    if missing:
        raise ValueError(f"crops.yaml is missing crops {missing}")
    nass = load_nass()
    crops, prov = {}, {"crops_yaml": source, "nass": nass is not None, "yields": {}, "prices": {}}
    for cid in config.CROP_IDS:
        c = copy.deepcopy(raw[cid])
        # crops.yaml may write a missing block as null; keep one shape for every caller
        c["heat"] = c.get("heat") or {"stage": None, "tmax_c": None}
        for w in ("plant_window", "harvest_window"):
            c[w] = c.get(w) or {"start": None, "end": None}
        absent = [k for k in REQUIRED if k not in c]
        if absent:
            raise ValueError(f"crops.yaml {cid} lacks {absent}")
        if cid in SOLD and nass is not None:
            for practice, key in (("irrigated", "irrigated_default"), ("non_irrigated", "dryland_default")):
                pick = _pick_yield(nass, cid, practice)
                if pick:
                    c["yield"][key] = pick["value"]
                    prov["yields"][f"{cid}.{practice}"] = pick
                elif c["yield"].get(key) is not None:
                    prov["yields"][f"{cid}.{practice}"] = {"value": c["yield"][key], "level": "crops_yaml"}
            price = _pick_price(nass, cid)
            if price is None and cid == "triticale":
                price = _pick_price(nass, "alfalfa")       # no triticale price series: NASS alfalfa hay price
                if price:
                    price["proxy"] = "alfalfa"
            if price:
                c["price"]["default"] = price["value"]
                c["price"]["unit"] = c["price"]["unit"] or price["unit"]
                prov["prices"][cid] = price
        if cid in SOLD and (c["yield"]["irrigated_default"] is None or c["yield"]["dryland_default"] is None
                            or c["price"]["default"] is None):
            raise ValueError(f"{cid}: no yield or price from NASS or crops.yaml")
        crops[cid] = c
    prov["local_market"] = county_market(nass)
    return crops, prov


def yields_not_county(prov: dict, crop_ids: list[str]) -> bool:
    """True if any yield for these crops came from district/state data, the 'all' practice, or crops.yaml."""
    for key, p in prov["yields"].items():
        if key.split(".")[0] in crop_ids and (p.get("level") != "county" or p.get("practice") not in ("irrigated", "non_irrigated")):
            return True
    return False


def write_crops_json(crops: dict) -> None:
    write_json(config.OUT_DIR / "crops.json", {"_meta": meta("crops@1", "model/library/load_crops.py"), "crops": crops})
