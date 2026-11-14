"""USDA NASS QuickStats -> out/processed/nass.json (README §8.2 NassFile).

Yields: Finney County, filled from the SW Kansas ag district, then Kansas.
Prices: Kansas annual (marketing year), US if Kansas missing.
Acres planted: Finney County, filled from the district.
Needs NASS_API_KEY in data-pipeline/.env.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

import config as C  # noqa: E402
import requests  # noqa: E402

from common import rel, Skip, cached_json, get_json, log, meta, write_json  # noqa: E402

API = "https://quickstats.nass.usda.gov/api/api_GET/"
OUT = C.PROCESSED / "nass.json"
OUTPUTS = [OUT]
YEAR_MIN = 2000

# CropId -> (commodity_desc, filters applied in pandas, yield unit, contract unit)
CROPS = {
    "corn": ("CORN", {"util_practice_desc": "GRAIN"}, "BU / ACRE", "bu/ac"),
    "sorghum": ("SORGHUM", {"util_practice_desc": "GRAIN"}, "BU / ACRE", "bu/ac"),
    "wheat": ("WHEAT", {"class_desc": "WINTER"}, "BU / ACRE", "bu/ac"),
    "soybean": ("SOYBEANS", {}, "BU / ACRE", "bu/ac"),
    "alfalfa": ("HAY", {"class_desc": "ALFALFA"}, "TONS / ACRE", "tons/ac"),
    "cotton": ("COTTON", {"class_desc": "UPLAND"}, "LB / ACRE", "lb/ac"),
}
PRACTICE = {"IRRIGATED": "irrigated", "NON-IRRIGATED": "non_irrigated",
            "ALL PRODUCTION PRACTICES": "all"}
PRICE_FILTERS = {
    "corn": ("CORN", {"util_practice_desc": "GRAIN"}),
    "sorghum": ("SORGHUM", {"util_practice_desc": "GRAIN"}),
    "wheat": ("WHEAT", {"class_desc": "ALL CLASSES"}),
    "soybean": ("SOYBEANS", {}),
    "alfalfa": ("HAY", {"class_desc": "ALFALFA"}),
    "cotton": ("COTTON", {"class_desc": "UPLAND"}),
}
PRICE_UNITS = {"$ / BU": "usd/bu", "$ / TON": "usd/ton", "$ / LB": "usd/lb", "$ / CWT": "usd/cwt"}


def q(**params) -> pd.DataFrame:
    if not C.NASS_API_KEY:
        raise Skip("NASS_API_KEY not set in data-pipeline/.env")
    key = "_".join(f"{k}={v}" for k, v in sorted(params.items())).replace(" ", "").replace("/", "")
    cache = C.RAW / "nass" / f"{key[:180]}.json"

    def fetch():
        try:
            return get_json(API, params={"key": C.NASS_API_KEY, "format": "JSON", **params}, service="nass")
        except requests.HTTPError as e:  # QuickStats returns HTTP 400 for "no data"
            if "400" in str(e):
                return {"data": []}
            raise

    data = cached_json(cache, fetch)
    df = pd.DataFrame(data.get("data", []))
    if df.empty:
        return df
    df["num"] = pd.to_numeric(df["Value"].str.replace(",", "").str.strip(), errors="coerce")
    df = df.dropna(subset=["num"])
    df["year"] = df["year"].astype(int)
    return df


def _filter(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    if df.empty:
        return df
    for k, v in filters.items():
        df = df[df[k] == v]
    if "reference_period_desc" in df:
        df = df[df["reference_period_desc"].isin(["YEAR", "MARKETING YEAR"])]
    if "domain_desc" in df:
        df = df[df["domain_desc"] == "TOTAL"]
    return df


def levels(stat: str, commodity: str) -> dict[str, pd.DataFrame]:
    base = {"source_desc": "SURVEY", "sector_desc": "CROPS", "state_alpha": C.STATE_ALPHA,
            "statisticcat_desc": stat, "commodity_desc": commodity, "year__GE": YEAR_MIN}
    return {
        "county": q(**base, agg_level_desc="COUNTY", county_name=C.COUNTY_NAME),
        "district": q(**base, agg_level_desc="AGRICULTURAL DISTRICT", asd_desc=C.NASS_DISTRICT),
        "state": q(**base, agg_level_desc="STATE"),
    }


def yields() -> list[dict]:
    out = []
    for crop, (commodity, flt, unit, unit_out) in CROPS.items():
        by_level = {}
        for lvl, df in levels("YIELD", commodity).items():
            df = _filter(df, flt)
            if not df.empty:
                df = df[(df["unit_desc"] == unit) & df["prodn_practice_desc"].isin(PRACTICE)]
            by_level[lvl] = {(PRACTICE[r.prodn_practice_desc], r.year): r.num for r in df.itertuples()}
        keys = set().union(*[set(d) for d in by_level.values()])
        # only fill a (practice, year) from a coarser level if the county ever reports that practice
        for practice, year in sorted(keys):
            for lvl in ("county", "district", "state"):
                v = by_level[lvl].get((practice, year))
                if v is not None:
                    out.append({"crop": crop, "practice": practice, "year": year,
                                "value": round(float(v), 1), "unit": unit_out, "level": lvl})
                    break
        log("nass", f"yields {crop}: " + ", ".join(
            f"{lvl}={len(d)}" for lvl, d in by_level.items()))
    return out


def prices() -> list[dict]:
    out = []
    for crop, (commodity, flt) in PRICE_FILTERS.items():
        base = {"source_desc": "SURVEY", "sector_desc": "CROPS", "statisticcat_desc": "PRICE RECEIVED",
                "commodity_desc": commodity, "freq_desc": "ANNUAL", "year__GE": 2015, "year__LE": 2024}
        st = _filter(q(**base, agg_level_desc="STATE", state_alpha=C.STATE_ALPHA), flt)
        us = _filter(q(**base, agg_level_desc="NATIONAL"), flt)
        for year in range(2015, 2025):
            for lvl, df in (("state", st), ("us", us)):
                if df.empty:
                    continue
                row = df[(df["year"] == year) & df["unit_desc"].isin(PRICE_UNITS)]
                if row.empty:
                    continue
                r0 = row.iloc[0]
                unit, val = PRICE_UNITS[r0["unit_desc"]], float(r0["num"])
                if unit == "usd/cwt":  # sorghum: $/bu = $/cwt * 0.56
                    unit, val = "usd/bu", val * 0.56
                out.append({"crop": crop, "year": year, "value": round(val, 2), "unit": unit, "level": lvl})
                break
    log("nass", f"prices: {len(out)} crop-years")
    return out


def acres() -> list[dict]:
    out = []
    for crop, (commodity, flt, _, _) in CROPS.items():
        if crop == "alfalfa":
            continue  # NASS has no planted area for hay
        lv = levels("AREA PLANTED", commodity)
        by_level = {}
        for lvl in ("county", "district"):
            df = _filter(lv[lvl], {k: v for k, v in flt.items() if k != "util_practice_desc"})
            if not df.empty:
                df = df[(df["unit_desc"] == "ACRES") & df["prodn_practice_desc"].isin(PRACTICE)]
                if "util_practice_desc" in df:
                    df = df[df["util_practice_desc"] == "ALL UTILIZATION PRACTICES"]
            by_level[lvl] = {(PRACTICE[r.prodn_practice_desc], r.year): r.num for r in df.itertuples()}
        for practice, year in sorted(set(by_level["county"]) | set(by_level["district"])):
            for lvl in ("county", "district"):
                v = by_level[lvl].get((practice, year))
                if v is not None:
                    out.append({"crop": crop, "practice": practice, "year": year,
                                "planted_ac": int(v), "level": lvl})
                    break
    log("nass", f"acres: {len(out)} rows")
    return out


def main(force: bool = False) -> None:
    if OUT.exists() and not force:
        log("nass", f"exists: {OUT.name}")
        return
    doc = {"_meta": meta("nass", "fetch/nass.py"), "county": C.COUNTY_NAME, "state": C.STATE_ALPHA,
           "yields": yields(), "prices": prices(), "acres": acres()}
    write_json(OUT, doc)
    log("nass", f"wrote {rel(OUT)}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
