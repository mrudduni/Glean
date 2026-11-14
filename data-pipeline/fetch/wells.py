"""Groundwater levels near each demo field (USGS Water Data OGC API).

The legacy waterservices.usgs.gov/nwis/gwlevels service was decommissioned in fall
2025, so this uses api.waterdata.usgs.gov (collections monitoring-locations and
field-measurements, parameter 72019 = depth to water below land surface, ft).

Keeps the 3 wells nearest each demo field with >= 10 years of winter (Dec–Apr)
measurements since 2000. Depth converted ft -> m; trend = OLS slope of winter
depth to water vs time (positive = water table falling).

Output: raw/wells/wells.json  {fid: [{site_id, name, distance_km, series, trend_m_per_yr}]}
Fallback: if this API fails, export Finney County from KGS WIZARD
(https://www.kgs.ku.edu/Magellan/WaterLevels/) to raw/wells/wizard.csv (columns
site_id, name, lon, lat, date, depth_ft) and it is parsed instead.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

import config as C  # noqa: E402
from common import (rel, cached_json, decimal_year, get_json, haversine_km, load_fields_draft,  # noqa: E402
                    log, ols_slope)

API = "https://api.waterdata.usgs.gov/ogcapi/v1/collections"
DIR = C.RAW / "wells"
OUT = DIR / "wells.json"
OUTPUTS = [OUT]
WINTER = {12, 1, 2, 3, 4}
MIN_YEARS = 10


def _paged(url: str, params: dict) -> list[dict]:
    feats, nxt, p = [], url, dict(params)
    while nxt:
        d = get_json(nxt, params=p, timeout=300, service="usgs")
        feats += d.get("features", [])
        nxt = next((ln["href"] for ln in d.get("links", []) if ln.get("rel") == "next"), None)
        p = None  # the next link already carries the query
    return feats


def sites() -> pd.DataFrame:
    feats = cached_json(DIR / "sites.json", lambda: _paged(
        f"{API}/monitoring-locations/items",
        {"f": "json", "limit": 10000, "state_code": C.STATE_FIPS, "county_code": C.COUNTY_FIPS,
         "site_type_code": "GW"}), max_age_days=30)
    return pd.DataFrame([{"site_id": f["id"], "name": f["properties"].get("monitoring_location_name") or f["id"],
                          "lon": f["geometry"]["coordinates"][0], "lat": f["geometry"]["coordinates"][1]}
                         for f in feats if f.get("geometry")])


def measurements() -> pd.DataFrame:
    b = C.COUNTY_BBOX
    feats = cached_json(DIR / "measurements.json", lambda: _paged(
        f"{API}/field-measurements/items",
        {"f": "json", "limit": 10000, "bbox": f"{b[0]},{b[1]},{b[2]},{b[3]}",
         "parameter_code": "72019", "time": "2000-01-01T00:00:00Z/.."}), max_age_days=30)
    rows = []
    for f in feats:
        p = f["properties"]
        try:
            v = float(p["value"])
        except (TypeError, ValueError):
            continue
        if (p.get("unit_of_measure") or "ft").lower().startswith("ft"):
            v *= 0.3048
        rows.append({"site_id": p["monitoring_location_id"], "date": p["time"][:10], "depth_m": v,
                     "lon": f["geometry"]["coordinates"][0] if f.get("geometry") else None,
                     "lat": f["geometry"]["coordinates"][1] if f.get("geometry") else None})
    return pd.DataFrame(rows)


def from_wizard(p: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(p)
    df["depth_m"] = df["depth_ft"] * 0.3048
    s = df.groupby("site_id").agg(name=("name", "first"), lon=("lon", "first"), lat=("lat", "first")).reset_index()
    return s, df[["site_id", "date", "depth_m"]]


def main(force: bool = False) -> None:
    if OUT.exists() and not force:
        log("wells", f"exists: {OUT.name}")
        return
    wiz = DIR / "wizard.csv"
    if wiz.exists():
        s, m = from_wizard(wiz)
    else:
        s, m = sites(), measurements()
        # sites outside the county list (other agencies) still have coordinates on the measurement
        extra = m[~m.site_id.isin(s.site_id)].groupby("site_id").agg(lon=("lon", "first"), lat=("lat", "first"))
        s = pd.concat([s, extra.reset_index().assign(name=lambda d: d.site_id)], ignore_index=True)
    log("wells", f"{len(s)} sites, {len(m)} measurements since 2000")
    m["date"] = pd.to_datetime(m["date"])
    m = m[m.depth_m.notna() & (m.depth_m > 0)]
    w = m[m.date.dt.month.isin(WINTER)].copy()
    # winter season label: Dec 2011 belongs to the 2012 winter
    w["season"] = w.date.dt.year + (w.date.dt.month == 12).astype(int)
    years = w.groupby("site_id").season.nunique()
    ok = years[years >= MIN_YEARS].index
    s = s[s.site_id.isin(ok)].drop_duplicates("site_id")
    log("wells", f"{len(s)} wells with >= {MIN_YEARS} winters of measurements")

    gdf = load_fields_draft()
    out = {}
    for fid, geom in gdf.geometry.items():
        c = geom.representative_point()
        s = s.assign(distance_km=[haversine_km(c.x, c.y, a, b) for a, b in zip(s.lon, s.lat)])
        near = s.nsmallest(3, "distance_km")
        wells = []
        for r in near.itertuples():
            ws = w[w.site_id == r.site_id].sort_values("date")
            # one value per winter (median) for the trend, all winter readings for the series
            per = ws.groupby("season").agg(date=("date", "median"), depth_m=("depth_m", "median"))
            slope = ols_slope(decimal_year(per.date), per.depth_m)
            wells.append({
                "site_id": r.site_id, "name": str(r.name), "distance_km": round(r.distance_km, 1),
                "series": [{"date": d.strftime("%Y-%m-%d"), "depth_to_water_m": round(v, 2)}
                           for d, v in zip(ws.date, ws.depth_m)],
                "trend_m_per_yr": round(slope, 2) if slope is not None else None,
            })
            log("wells", f"{fid}: {r.site_id} {r.distance_km:.1f} km, {len(per)} winters, "
                         f"trend {slope:+.2f} m/yr" if slope is not None else f"{fid}: {r.site_id}")
        out[fid] = wells
    DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    log("wells", f"wrote {rel(OUT)}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
