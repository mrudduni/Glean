"""Live probe of no-auth NASA data APIs for Field Shift (phase 2 research).

Run:  python probe_nasa.py [power] [cmr] [appeears] [gibs] [earthaccess] [cdl]
With no arguments it runs every probe.

Nothing here needs an Earthdata Login. The script never downloads granules.
Large POWER responses are cached outside the repo, in FIELDSHIFT_CACHE
(default: ~/.cache/fieldshift). Small, truncated samples go to ../samples/.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import requests  # noqa: E402

HERE = Path(__file__).resolve().parent
SAMPLES = HERE.parent / "samples"
SAMPLES.mkdir(exist_ok=True)
CACHE = Path(os.environ.get("FIELDSHIFT_CACHE", Path.home() / ".cache" / "fieldshift"))
CACHE.mkdir(parents=True, exist_ok=True)

HEADERS = {"Client-Id": "fieldshift-probe", "User-Agent": "fieldshift-probe/0.1"}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

SITES = {
    "S1": {"name": "Central Iowa corn-soy", "lat": 42.03, "lon": -93.75},
    "S2": {"name": "Finney County, Kansas", "lat": 37.95, "lon": -100.90},
    "S3": {"name": "Fresno County, California", "lat": 36.60, "lon": -120.10},
    "S4": {"name": "Ludhiana, Punjab", "lat": 30.90, "lon": 75.85},
}

MAX_SAMPLE_BYTES = 100_000


def save_sample(name: str, obj) -> Path | None:
    """Write a JSON sample if it fits in 100 KB. Larger objects stay in CACHE only,
    and write_summaries() puts a compact version in samples/."""
    path = SAMPLES / name
    text = json.dumps(obj, indent=1, default=str)
    if len(text.encode()) > MAX_SAMPLE_BYTES:
        text = json.dumps(obj, separators=(",", ":"), default=str)
    if len(text.encode()) > MAX_SAMPLE_BYTES:
        print(f"   skipped sample {name}: {len(text.encode())} bytes is over 100 KB (kept in cache)")
        if path.exists():
            path.unlink()
        return None
    path.write_text(text, encoding="utf-8")
    return path


def timed_get(url: str, params=None, timeout=300, stream=False):
    t0 = time.time()
    r = SESSION.get(url, params=params, timeout=timeout, stream=stream)
    return r, time.time() - t0


# --------------------------------------------------------------------------
# 1. NASA POWER
# --------------------------------------------------------------------------
POWER = "https://power.larc.nasa.gov"
POWER_PARAMS = [
    "T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "ALLSKY_SFC_SW_DWN",
    "RH2M", "WS2M", "GWETROOT", "GWETTOP", "EVPTRNS",
]
# Extra parameters that phase 1 claimed exist (SMAP and IMERG aliases, GDD, frost).
POWER_EXTRA = ["IMERG_PRECTOT", "SFMC", "RZMC", "RZMC_PRCNTL", "FROST_DAYS", "GDD10", "EVLAND"]


def power_probe() -> dict:
    out: dict = {"base": POWER}

    # Parameter manager (metadata) endpoint.
    url = f"{POWER}/api/system/manager/parameters"
    r, dt = timed_get(url, params={"community": "AG", "temporal": "daily"})
    out["manager"] = {"url": r.url, "status": r.status_code, "bytes": len(r.content),
                      "seconds": round(dt, 2), "rate_headers": rate_headers(r)}
    if r.ok:
        meta = r.json()
        out["manager"]["n_parameters"] = len(meta)
        wanted = POWER_PARAMS + POWER_EXTRA
        out["manager"]["checked"] = {
            p: ({k: meta[p].get(k) for k in ("name", "units", "type", "source", "definition")}
                if p in meta else None)
            for p in wanted
        }
        save_sample("power_manager_ag_daily_subset.json",
                    {p: meta[p] for p in wanted if p in meta})

    # Single-parameter detail endpoint.
    url = f"{POWER}/api/system/manager/parameters/T2M_MIN"
    r, dt = timed_get(url, params={"user": "fieldshift"})
    out["manager_single"] = {"url": r.url, "status": r.status_code, "bytes": len(r.content)}
    if r.ok:
        save_sample("power_manager_T2M_MIN.json", r.json())

    # Daily point, 2001 to 2025, ten parameters, every site.
    out["daily"] = {}
    for sid, s in SITES.items():
        params = {"parameters": ",".join(POWER_PARAMS), "community": "AG",
                  "longitude": s["lon"], "latitude": s["lat"],
                  "start": "20010101", "end": "20251231", "format": "JSON"}
        cache = CACHE / f"power_daily_{sid}_2001_2025.json"
        rec = {}
        meta_path = cache.with_suffix(".meta.json")
        if cache.exists():
            data = json.loads(cache.read_text())
            rec["from_cache"] = str(cache)
            if meta_path.exists():
                rec["first_fetch"] = json.loads(meta_path.read_text())
        else:
            r, dt = timed_get(f"{POWER}/api/temporal/daily/point", params=params)
            rec.update({"url": r.url, "status": r.status_code, "bytes": len(r.content),
                        "seconds": round(dt, 2), "rate_headers": rate_headers(r)})
            if not r.ok:
                rec["error"] = r.text[:1000]
                out["daily"][sid] = rec
                continue
            data = r.json()
            cache.write_text(json.dumps(data))
            meta_path.write_text(json.dumps({k: rec[k] for k in ("url", "status", "bytes", "seconds")}
                                            | {"fetched_utc": pd.Timestamp.utcnow().isoformat()}))
        rec["url"] = rec.get("url") or requests.Request("GET", f"{POWER}/api/temporal/daily/point", params=params).prepare().url
        rec["header"] = data.get("header")
        rec["messages"] = data.get("messages")
        rec["units"] = {k: v.get("units") for k, v in data.get("parameters", {}).items()}
        rec["geometry"] = data.get("geometry")
        rec["stats"] = power_stats(data)
        out["daily"][sid] = rec
        if sid == "S1":
            trimmed = json.loads(json.dumps(data))
            for p, series in trimmed["properties"]["parameter"].items():
                trimmed["properties"]["parameter"][p] = dict(list(series.items())[:31])
            save_sample("power_daily_S1_first31days.json", trimmed)

    # Extra parameters, one short request so we see which aliases really work.
    s = SITES["S1"]
    params = {"parameters": ",".join(POWER_EXTRA), "community": "AG",
              "longitude": s["lon"], "latitude": s["lat"],
              "start": "20240701", "end": "20240707", "format": "JSON"}
    r, dt = timed_get(f"{POWER}/api/temporal/daily/point", params=params)
    out["extra"] = {"url": r.url, "status": r.status_code, "seconds": round(dt, 2)}
    out["extra"]["body"] = r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text[:2000]
    save_sample("power_daily_S1_extra_params.json", out["extra"]["body"])

    # The same aliases with time-standard=UTC (IMERG is UTC only).
    params_utc = dict(params, **{"time-standard": "UTC"})
    r, _ = timed_get(f"{POWER}/api/temporal/daily/point", params=params_utc)
    out["extra_utc"] = {"url": r.url, "status": r.status_code, "body": r.json() if r.ok else r.text[:1500]}
    save_sample("power_daily_S1_extra_params_utc.json", out["extra_utc"]["body"])

    # IMERG_PRECTOT latency in UTC.
    today = pd.Timestamp.utcnow().normalize().tz_localize(None)
    params_im = {"parameters": "IMERG_PRECTOT", "community": "AG", "longitude": s["lon"],
                 "latitude": s["lat"], "start": (today - pd.Timedelta(days=120)).strftime("%Y%m%d"),
                 "end": today.strftime("%Y%m%d"), "format": "JSON", "time-standard": "UTC"}
    r, _ = timed_get(f"{POWER}/api/temporal/daily/point", params=params_im)
    if r.ok:
        ser = r.json()["properties"]["parameter"]["IMERG_PRECTOT"]
        good = [d for d, v in ser.items() if v != -999.0]
        out["imerg_latency"] = {"url": r.url, "last_valid_date": max(good) if good else None}

    # Source switches: which upstream product feeds each month of 2026.
    switch = {}
    for p in ("T2M", "ALLSKY_SFC_SW_DWN"):
        switch[p] = {}
        for m in pd.date_range("2026-01-01", today, freq="MS"):
            d = m.strftime("%Y%m%d")
            r, _ = timed_get(f"{POWER}/api/temporal/daily/point",
                             params={"parameters": p, "community": "AG", "longitude": s["lon"],
                                     "latitude": s["lat"], "start": d, "end": d, "format": "JSON"})
            switch[p][d] = r.json()["header"]["sources"] if r.ok else f"HTTP {r.status_code}"
    out["source_by_month_2026"] = switch

    # Latency: ask for the last 30 days and find the last non-fill date per parameter.
    params = {"parameters": ",".join(POWER_PARAMS + ["IMERG_PRECTOT"]), "community": "AG",
              "longitude": s["lon"], "latitude": s["lat"],
              "start": (today - pd.Timedelta(days=30)).strftime("%Y%m%d"),
              "end": today.strftime("%Y%m%d"), "format": "JSON"}
    r, dt = timed_get(f"{POWER}/api/temporal/daily/point", params=params)
    lat_rec = {"url": r.url, "status": r.status_code, "seconds": round(dt, 2)}
    if r.ok:
        body = r.json()
        lat_rec["header"] = body.get("header")
        lat_rec["messages"] = body.get("messages")
        fill = body["header"].get("fill_value", -999)
        last = {}
        for p, series in body["properties"]["parameter"].items():
            good = [d for d, v in series.items() if v is not None and v != fill]
            last[p] = max(good) if good else None
        lat_rec["last_valid_date"] = last
        save_sample("power_daily_S1_last30days.json", body)
    else:
        lat_rec["error"] = r.text[:1500]
    out["latency"] = lat_rec

    # Climatology endpoint.
    params = {"parameters": "T2M,T2M_MIN,PRECTOTCORR,ALLSKY_SFC_SW_DWN", "community": "AG",
              "longitude": s["lon"], "latitude": s["lat"], "format": "JSON"}
    r, dt = timed_get(f"{POWER}/api/temporal/climatology/point", params=params)
    out["climatology"] = {"url": r.url, "status": r.status_code, "bytes": len(r.content),
                          "seconds": round(dt, 2)}
    if r.ok:
        body = r.json()
        out["climatology"]["header"] = body.get("header")
        out["climatology"]["ANN"] = {p: v.get("ANN") for p, v in body["properties"]["parameter"].items()}
        save_sample("power_climatology_S1.json", body)
    else:
        out["climatology"]["error"] = r.text[:1500]

    # Deliberately bad parameter: record the error format.
    params = {"parameters": "NOT_A_PARAM", "community": "AG", "longitude": s["lon"],
              "latitude": s["lat"], "start": "20240101", "end": "20240102", "format": "JSON"}
    r, _ = timed_get(f"{POWER}/api/temporal/daily/point", params=params)
    out["bad_param"] = {"url": r.url, "status": r.status_code, "body": r.text[:800]}
    return out


def rate_headers(r) -> dict:
    return {k: v for k, v in r.headers.items()
            if re.search(r"rate|limit|retry|quota", k, re.I)}


def power_frame(data: dict) -> pd.DataFrame:
    p = data["properties"]["parameter"]
    df = pd.DataFrame(p)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    fill = data["header"].get("fill_value", -999.0)
    return df.replace(fill, np.nan)


def power_stats(data: dict) -> dict:
    df = power_frame(data)
    df["year"] = df.index.year
    st: dict = {"n_days": int(len(df)), "first": str(df.index.min().date()),
                "last": str(df.index.max().date()),
                "missing_by_param": {c: int(df[c].isna().sum()) for c in POWER_PARAMS if c in df}}

    annual_p = df.groupby("year")["PRECTOTCORR"].sum(min_count=300)
    st["mean_annual_precip_mm"] = round(float(annual_p.mean()), 0)
    st["min_annual_precip_mm"] = round(float(annual_p.min()), 0)
    st["max_annual_precip_mm"] = round(float(annual_p.max()), 0)

    # Last spring frost: last date from 1 Jan to 30 Jun with Tmin <= 0 C.
    doys = []
    for y, g in df.groupby("year"):
        spring = g[(g.index.month <= 6) & (g["T2M_MIN"] <= 0)]
        if len(spring):
            doys.append(int(spring.index.max().dayofyear))
    st["years_with_spring_frost"] = len(doys)
    if doys:
        mean_doy = float(np.mean(doys))
        st["mean_last_spring_frost_doy"] = round(mean_doy, 1)
        st["mean_last_spring_frost_date"] = (pd.Timestamp("2001-01-01") + pd.Timedelta(days=mean_doy - 1)).strftime("%d %b")
        st["latest_last_spring_frost_date"] = (pd.Timestamp("2001-01-01") + pd.Timedelta(days=max(doys) - 1)).strftime("%d %b")

    # GDD base 10 C, May to September. Two methods.
    ms = df[(df.index.month >= 5) & (df.index.month <= 9)].copy()
    simple = (((ms["T2M_MAX"] + ms["T2M_MIN"]) / 2) - 10).clip(lower=0)
    tmax = ms["T2M_MAX"].clip(upper=30, lower=10)
    tmin = ms["T2M_MIN"].clip(upper=30, lower=10)
    capped = ((tmax + tmin) / 2 - 10).clip(lower=0)
    st["gdd10_may_sep_simple_mean"] = round(float(simple.groupby(ms["year"]).sum().mean()), 0)
    st["gdd10_may_sep_86_50_mean"] = round(float(capped.groupby(ms["year"]).sum().mean()), 0)

    # Hot days, Tmax >= 35 C, per year with a linear trend.
    hot = (df["T2M_MAX"] >= 35).groupby(df["year"]).sum()
    yrs = hot.index.values.astype(float)
    slope = float(np.polyfit(yrs, hot.values.astype(float), 1)[0]) if hot.sum() else 0.0
    st["hot_days_35C_mean_per_year"] = round(float(hot.mean()), 1)
    st["hot_days_35C_2001_2012_mean"] = round(float(hot.loc[2001:2012].mean()), 1)
    st["hot_days_35C_2014_2025_mean"] = round(float(hot.loc[2014:2025].mean()), 1)
    st["hot_days_35C_trend_per_decade"] = round(slope * 10, 1)
    st["hot_days_35C_max_year"] = [int(hot.idxmax()), int(hot.max())]

    st["annual"] = {
        "precip_mm": {int(k): round(float(v), 0) for k, v in annual_p.items()},
        "hot_days_35C": {int(k): int(v) for k, v in hot.items()},
        "mean_tmax_C": {int(k): round(float(v), 2) for k, v in df.groupby("year")["T2M_MAX"].mean().items()},
    }
    st["mean_T2M"] = round(float(df["T2M"].mean()), 2)
    st["mean_daily_SW_MJ"] = round(float(df["ALLSKY_SFC_SW_DWN"].mean()), 2)
    jja = df[df.index.month.isin([6, 7, 8])]
    st["mean_GWETROOT_JJA"] = round(float(jja["GWETROOT"].mean()), 3)
    st["mean_EVPTRNS_JJA"] = round(float(jja["EVPTRNS"].mean()), 2)
    return st


# --------------------------------------------------------------------------
# 2. CMR
# --------------------------------------------------------------------------
CMR = "https://cmr.earthdata.nasa.gov/search"

# (group, short_name, version or None). None means "every version CMR returns".
CMR_TARGETS = [
    ("SMAP", "SPL3SMP_E", None), ("SMAP", "SPL4SMGP", None), ("SMAP", "SPL2SMP_E", None),
    ("SMAP", "SPL2SMAP_S", None), ("SMAP", "SPL3SMP", None),
    ("IMERG", "GPM_3IMERGDF", None), ("IMERG", "GPM_3IMERGDL", None), ("IMERG", "GPM_3IMERGDE", None),
    ("IMERG", "GPM_3IMERGM", None),
    ("HLS", "HLSL30", None), ("HLS", "HLSS30", None), ("HLS", "HLSL30_VI", None), ("HLS", "HLSS30_VI", None),
    ("Landsat", "concept:C3442503899-USGS_EROS", None), ("Landsat", "concept:C3442506077-USGS_EROS", None),
    ("MODIS", "MOD13Q1", None), ("MODIS", "MYD13Q1", None), ("MODIS", "MOD16A2GF", None),
    ("MODIS", "MOD16A2", None), ("MODIS", "MOD11A2", None), ("MODIS", "MCD12Q1", None),
    ("VIIRS", "VNP13A1", None), ("VIIRS", "VJ113A1", None), ("VIIRS", "VNP21A2", None),
    ("VIIRS", "VJ121A2", None), ("VIIRS", "VNP21A1D", None),
    ("ECOSTRESS", "ECO_L2T_LSTE", None), ("ECOSTRESS", "ECO_L3T_JET", None),
    ("ECOSTRESS", "ECO_L4T_ESI", None), ("ECOSTRESS", "ECO_L4T_WUE", None),
    ("ECOSTRESS", "ECO_L3T_ET_ALEXI", None), ("ECOSTRESS", "ECO_L4T_ESI_ALEXI", None),
    ("GRACE", "TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4", None),
    ("GRACE", "TELLUS_GRAC-GRFO_MASCON_GRID_RL06.3_V4", None),
    ("GRACE", "GRACEDADM_CLSM0125US_7D", None), ("GRACE", "GRACEDADM_CLSM025GL_7D", None),
    ("DEM", "SRTMGL1", None), ("DEM", "NASADEM_HGT", None),
    ("GEDI", "GEDI02_A", None), ("GEDI", "GEDI_L4A_AGB_Density_V2_1_2056", None),
    ("GEDI", "GEDI_L4B_Gridded_Biomass_V2_1_2299", None),
    ("LDAS", "NLDAS_FORA0125_H", None), ("LDAS", "NLDAS_NOAH0125_H", None),
    ("LDAS", "GLDAS_NOAH025_3H", None), ("LDAS", "GLDAS_NOAH025_M", None),
    ("LDAS", "GLDAS_CLSM025_DA1_D", None),
]
# Keyword searches recorded to show how we found products with unknown names.
CMR_KEYWORDS = ["GSFC mascon", "mascon", "GRACE drought indicator", "NLDAS-3",
                "GEDI L4B gridded biomass", "IMERG V08", "ECOSTRESS v003 tiled"]


def cmr_get(path: str, params) -> tuple[requests.Response, str]:
    r = SESSION.get(f"{CMR}/{path}", params=params, timeout=120)
    return r, r.url


def cmr_probe() -> dict:
    s1 = SITES["S1"]
    point = f"{s1['lon']},{s1['lat']}"
    results = {"queries": [], "collections": [], "keyword_searches": {}}

    for kw in CMR_KEYWORDS:
        r, u = cmr_get("collections.json", {"keyword": kw, "page_size": 30})
        results["queries"].append(u)
        results["keyword_searches"][kw] = {
            "url": u, "hits": r.headers.get("CMR-Hits"),
            "entries": [(e["short_name"], e.get("version_id"), e["id"]) for e in r.json()["feed"]["entry"]]}

    for group, name, ver in CMR_TARGETS:
        params = {"page_size": 20}
        if name.startswith("concept:"):
            params["concept_id"] = name.split(":", 1)[1]
        else:
            params["short_name"] = name
            if ver:
                params["version"] = ver
        r, u_json = cmr_get("collections.json", params)
        results["queries"].append(u_json)
        entries = r.json()["feed"]["entry"] if r.ok else []
        if not entries:
            results["collections"].append({"group": group, "query": name, "url": u_json,
                                           "status": r.status_code, "found": False})
            continue
        for e in entries:
            results["collections"].append(cmr_collection_detail(group, e, point, results["queries"]))
    return results


def cmr_collection_detail(group: str, e: dict, point: str, qlog: list) -> dict:
    cid = e["id"]
    rec = {"group": group, "short_name": e["short_name"], "version": e.get("version_id"),
           "concept_id": cid, "provider": e.get("data_center"), "title": e.get("title"),
           "archive_center": e.get("archive_center"), "cloud_hosted": e.get("cloud_hosted"),
           "time_start": e.get("time_start"), "time_end": e.get("time_end"),
           "service_features": e.get("service_features"), "found": True}
    r, u = cmr_get("collections.umm_json", {"concept_id": cid})
    qlog.append(u)
    rec["umm_url"] = u
    if r.ok and r.json().get("items"):
        item = r.json()["items"][0]
        umm, meta = item["umm"], item["meta"]
        rec["daac"] = [d.get("ShortName") for d in umm.get("DataCenters", [])
                       if "ARCHIVER" in (d.get("Roles") or [])]
        res = (umm.get("SpatialExtent", {}).get("HorizontalSpatialDomain", {})
               .get("ResolutionAndCoordinateSystem", {}).get("HorizontalDataResolution"))
        rec["spatial_resolution"] = res
        rec["formats"] = [f.get("Format") for f in
                          (umm.get("ArchiveAndDistributionInformation") or {}).get("FileDistributionInformation", [])]
        dd = umm.get("DirectDistributionInformation") or {}
        rec["s3_region"] = dd.get("Region")
        rec["s3_prefixes"] = dd.get("S3BucketAndObjectPrefixNames")
        rec["doi"] = (umm.get("DOI") or {}).get("DOI")
        rec["collection_progress"] = umm.get("CollectionProgress")
        urls = umm.get("RelatedUrls") or []
        rec["opendap_related_urls"] = [x.get("URL") for x in urls
                                       if "opendap" in (x.get("URL", "") + str(x.get("Subtype", ""))).lower()]
        rec["appeears_related_urls"] = [x.get("URL") for x in urls if "appeears" in x.get("URL", "").lower()]
        assoc = meta.get("associations") or {}
        rec["n_variables"] = len(assoc.get("variables", []))
        rec["services"] = cmr_names("services", assoc.get("services", []), qlog)
        rec["tools"] = cmr_names("tools", assoc.get("tools", []), qlog)
        if assoc.get("variables"):
            rec["variable_names"] = cmr_variable_names(assoc["variables"][:200], qlog)

    # Granules intersecting S1 in 2024.
    gp = {"collection_concept_id": cid, "point": point,
          "temporal": "2024-01-01T00:00:00Z,2024-12-31T23:59:59Z", "page_size": 5}
    r, u = cmr_get("granules.umm_json", gp)
    qlog.append(u)
    rec["granules_S1_2024_url"] = u
    rec["granules_S1_2024"] = int(r.headers.get("CMR-Hits", -1)) if r.ok else f"HTTP {r.status_code}"
    items = r.json().get("items", []) if r.ok else []
    if not items:
        # Fall back to the newest granules anywhere, to get a size and the latest date.
        r, u = cmr_get("granules.umm_json", {"collection_concept_id": cid,
                                             "sort_key": "-start_date", "page_size": 5})
        qlog.append(u)
        items = r.json().get("items", []) if r.ok else []
        rec["granule_size_source"] = "newest granules, no spatial filter"
    else:
        rec["granule_size_source"] = "granules at S1 in 2024"
    rec["granule_samples"] = [granule_summary(it) for it in items[:5]]
    # Newest granule date, to measure real latency.
    r, u = cmr_get("granules.json", {"collection_concept_id": cid,
                                     "sort_key": "-start_date", "page_size": 1})
    qlog.append(u)
    ent = r.json()["feed"]["entry"] if r.ok else []
    rec["newest_granule"] = ({"title": ent[0].get("title"), "time_start": ent[0].get("time_start"),
                              "time_end": ent[0].get("time_end")} if ent else None)
    rec["total_granules"] = r.headers.get("CMR-Hits")
    return rec


def granule_summary(item: dict) -> dict:
    umm = item["umm"]
    sizes = []
    for a in (umm.get("DataGranule") or {}).get("ArchiveAndDistributionInformation", []) or []:
        if "SizeInBytes" in a:
            sizes.append(round(a["SizeInBytes"] / 1e6, 3))
        elif "Size" in a:
            unit = a.get("SizeUnit", "MB")
            factor = {"KB": 1e-3, "MB": 1, "GB": 1e3, "TB": 1e6}.get(unit, 1)
            sizes.append(round(a["Size"] * factor, 3))
    rng = umm.get("TemporalExtent", {}).get("RangeDateTime", {})
    links = [x.get("URL") for x in umm.get("RelatedUrls", []) if x.get("Type") == "GET DATA"]
    return {"granule_ur": umm.get("GranuleUR"), "start": rng.get("BeginningDateTime"),
            "size_mb_per_file": sizes, "n_files": len(sizes), "n_data_links": len(links),
            "first_data_link": links[0] if links else None}


def cmr_names(kind: str, ids: list, qlog: list) -> list:
    if not ids:
        return []
    r, u = cmr_get(f"{kind}.umm_json", [("concept_id[]", i) for i in ids] + [("page_size", 50)])
    qlog.append(u)
    if not r.ok:
        return [f"HTTP {r.status_code}"]
    return [{"concept_id": it["meta"]["concept-id"], "name": it["umm"].get("Name"),
             "type": it["umm"].get("Type"), "long_name": it["umm"].get("LongName")}
            for it in r.json().get("items", [])]


def cmr_variable_names(ids: list, qlog: list) -> list:
    names = []
    for i in range(0, len(ids), 100):
        r = SESSION.post(f"{CMR}/variables.json", data=[("concept_id[]", x) for x in ids[i:i + 100]]
                         + [("page_size", 100)], timeout=120)
        qlog.append(f"POST {CMR}/variables.json concept_id[]=... ({len(ids[i:i + 100])} ids)")
        if r.ok:
            names += [it.get("name") for it in r.json().get("items", [])]
    return sorted(names)


# --------------------------------------------------------------------------
# 3. AppEEARS
# --------------------------------------------------------------------------
APPEEARS = "https://appeears.earthdatacloud.nasa.gov/api"
APPEEARS_WANT = ["SPL3SMP_E", "SPL4SMGP", "SPL3SMP", "SPL2SMAP", "GPM", "IMERG", "HLSL30", "HLSS30",
                 "MOD13Q1", "MYD13Q1", "MOD16A2", "MOD11A2", "MOD11A1", "MCD12Q1", "VNP13A1", "VJ113A1",
                 "VNP21", "VJ121", "ECO_L2T", "ECO_L3T", "ECO_L4T", "ECO", "SRTMGL1", "NASADEM",
                 "GEDI", "DAYMET", "GRACE", "NLDAS", "GLDAS", "MOD15A2H", "MOD17"]


def appeears_probe() -> dict:
    r, dt = timed_get(f"{APPEEARS}/product")
    out = {"url": r.url, "status": r.status_code, "bytes": len(r.content), "seconds": round(dt, 2)}
    if not r.ok:
        out["error"] = r.text[:1000]
        return out
    prods = r.json()
    out["n_products"] = len(prods)
    save_sample("appeears_products_all.json", prods)
    out["all_product_ids"] = sorted(p["ProductAndVersion"] for p in prods)
    hits = [p for p in prods if any(w in p["ProductAndVersion"].upper() for w in APPEEARS_WANT)]
    out["relevant"] = {}
    for p in sorted(hits, key=lambda x: x["ProductAndVersion"]):
        pid = p["ProductAndVersion"]
        rr, _ = timed_get(f"{APPEEARS}/product/{pid}")
        layers = rr.json() if rr.ok else {"error": rr.status_code}
        out["relevant"][pid] = {
            "url": rr.url, "platform": p.get("Platform"), "description": p.get("Description"),
            "resolution": p.get("Resolution"), "temporal_granularity": p.get("TemporalGranularity"),
            "temporal_extent": [p.get("TemporalExtentStart"), p.get("TemporalExtentEnd")],
            "available": p.get("Available"), "source": p.get("Source"),
            "layers": {k: {"units": v.get("Units"), "desc": v.get("Description"),
                           "fill": v.get("FillValue"), "scale": v.get("ScaleFactor"),
                           "is_qa": v.get("IsQA")}
                       for k, v in (layers.items() if isinstance(layers, dict) else [])},
        }
    return out


# --------------------------------------------------------------------------
# 4. GIBS
# --------------------------------------------------------------------------
GIBS_CAPS = {
    "epsg4326_best": "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi?SERVICE=WMTS&REQUEST=GetCapabilities",
    "epsg3857_best": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/wmts.cgi?SERVICE=WMTS&REQUEST=GetCapabilities",
}
GIBS_PATTERNS = {
    "SMAP": r"SMAP", "IMERG": r"IMERG", "MODIS_NDVI": r"MOD.*NDVI|MODIS.*NDVI|NDVI",
    "ECOSTRESS": r"ECOSTRESS|ECO_", "GRACE": r"GRACE", "HLS": r"HLS", "VIIRS_truecolor": r"VIIRS.*TrueColor",
    "MODIS_truecolor": r"MODIS_Terra_CorrectedReflectance_TrueColor", "LST": r"Land_Surface_Temp",
}


def gibs_probe() -> dict:
    out = {}
    for key, url in GIBS_CAPS.items():
        r, dt = timed_get(url, timeout=300)
        rec = {"url": url, "status": r.status_code, "bytes": len(r.content), "seconds": round(dt, 2),
               "content_type": r.headers.get("content-type")}
        if r.ok:
            text = r.text
            layers = re.findall(r"<Layer>.*?</Layer>", text, flags=re.S)
            ids = []
            info = {}
            for block in layers:
                m = re.search(r"<ows:Identifier>([^<]+)</ows:Identifier>", block)
                if not m:
                    continue
                lid = m.group(1)
                ids.append(lid)
                tdef = re.search(r"<Dimension>.*?<Default>([^<]*)</Default>.*?</Dimension>", block, flags=re.S)
                vals = re.findall(r"<Value>([^<]+)</Value>", block)
                tms = re.findall(r"<TileMatrixSet>([^<]+)</TileMatrixSet>", block)
                fmt = re.findall(r"<Format>([^<]+)</Format>", block)
                info[lid] = {"default_time": tdef.group(1) if tdef else None,
                             "time_values_first_last": [vals[0], vals[-1]] if vals else None,
                             "tile_matrix_set": tms[:2], "format": fmt[:2]}
            rec["n_layers"] = len(ids)
            rec["matches"] = {}
            for name, pat in GIBS_PATTERNS.items():
                found = [i for i in ids if re.search(pat, i, re.I)]
                rec["matches"][name] = {i: info[i] for i in found[:60]}
                rec["matches"][name + "_count"] = len(found)
            if key == "epsg3857_best":
                save_sample("gibs_epsg3857_layer_ids.json", ids)
        out[key] = rec
    # Fetch one real tile to prove the XYZ pattern works.
    tile = ("https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/"
            "default/2024-07-15/GoogleMapsCompatible_Level9/6/23/14.jpg")
    r, dt = timed_get(tile)
    out["tile_test"] = {"url": tile, "status": r.status_code, "bytes": len(r.content),
                        "content_type": r.headers.get("content-type")}
    return out


# --------------------------------------------------------------------------
# 5. earthaccess
# --------------------------------------------------------------------------
def earthaccess_probe() -> dict:
    out = {}
    try:
        import earthaccess  # noqa: F401
        out["installed"] = True
        out["version"] = getattr(earthaccess, "__version__", "unknown")
    except ImportError as exc:
        out["installed"] = False
        out["import_error"] = str(exc)
    r, _ = timed_get("https://pypi.org/pypi/earthaccess/json")
    if r.ok:
        info = r.json()["info"]
        rel = r.json()["releases"].get(info["version"], [])
        out["pypi"] = {"url": r.url, "version": info["version"], "requires_python": info.get("requires_python"),
                       "license": info.get("license") or info.get("license_expression"),
                       "upload_time": rel[0]["upload_time"] if rel else None,
                       "project_urls": info.get("project_urls")}
    base = "https://earthaccess.readthedocs.io/en/latest/"
    for page in [base + "user/explanation/authenticate/", base + "user/howto/authenticate/",
                 base + "user/howto/authenticate-with-environment-variables/",
                 base + "api/auth/auth/"]:
        r, _ = timed_get(page)
        txt = re.sub(r"<[^>]+>", " ", r.text)
        txt = re.sub(r"\s+", " ", txt)
        hits = sorted(set(re.findall(r"(EARTHDATA_[A-Z_]+|\.netrc|_netrc|\"interactive\"|\"netrc\"|\"environment\"|persist)", txt)))
        out[page] = {"status": r.status_code, "auth_terms": hits}
    return out


# --------------------------------------------------------------------------
# 5b. Follow-ups: where the auth wall sits, Landsat STAC, coverage questions
# --------------------------------------------------------------------------
def followup_probe() -> dict:
    out: dict = {}
    s1 = SITES["S1"]
    point = f"{s1['lon']},{s1['lat']}"

    # Auth wall. We send no credentials and record the status code and redirect target.
    tests = {
        "imerg_daily_https_file": "https://data.gesdisc.earthdata.nasa.gov/data/GPM_L3/GPM_3IMERGDF.07/2024/01/"
                                  "3B-DAY.MS.MRG.3IMERG.20240101-S000000-E235959.V07B.nc4",
        "imerg_opendap_dmr": "https://opendap.earthdata.nasa.gov/collections/C2723754864-GES_DISC/granules/"
                             "GPM_3IMERGDF.07:3B-DAY.MS.MRG.3IMERG.20240101-S000000-E235959.V07B.nc4.dmr",
        "hls_cog_file": "https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/HLSL30.020/"
                        "HLS.L30.T15TVG.2024002T165931.v2.0/HLS.L30.T15TVG.2024002T165931.v2.0.Fmask.tif",
        "smap_l3e_file": "https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/SMAP/SPL3SMP_E/006/"
                         "2024/01/01/SMAP_L3_SM_P_E_20240101_R19240_001.h5",
        "appeears_task_list": f"{APPEEARS}/task",
        "harmony_capabilities": "https://harmony.earthdata.nasa.gov/capabilities?collectionId=C2723754864-GES_DISC",
        "harmony_imerg_point_subset": "https://harmony.earthdata.nasa.gov/C2723754864-GES_DISC/ogc-api-coverages/1.0.0/"
                                      "collections/all/coverage/rangeset?subset=lat(42.0:42.1)&subset=lon(-93.8:-93.7)"
                                      "&subset=time(%222024-07-01T00:00:00Z%22:%222024-07-02T00:00:00Z%22)",
        "giovanni_landing": "https://giovanni.gsfc.nasa.gov/giovanni/",
        "nasagrace_unl": "https://nasagrace.unl.edu/",
    }
    out["auth_wall"] = {}
    for name, url in tests.items():
        try:
            r = SESSION.get(url, allow_redirects=False, timeout=60, stream=True)
            loc = r.headers.get("Location", "")
            body = ""
            if "json" in r.headers.get("content-type", "") or r.status_code >= 400:
                body = r.raw.read(600, decode_content=True).decode(errors="ignore")
            out["auth_wall"][name] = {"url": url, "status": r.status_code,
                                      "redirect_host": re.sub(r"^(https?://[^/]+).*", r"\1", loc) if loc else None,
                                      "content_type": r.headers.get("content-type"), "body_start": body[:400]}
            r.close()
        except Exception as exc:  # noqa: BLE001
            out["auth_wall"][name] = {"url": url, "error": repr(exc)}

    # Landsat Collection 2 Level-2 through the USGS LandsatLook STAC server (no auth for search).
    stac = "https://landsatlook.usgs.gov/stac-server/search"
    body = {"collections": ["landsat-c2l2-sr"], "intersects": {"type": "Point", "coordinates": [s1["lon"], s1["lat"]]},
            "datetime": "2024-01-01T00:00:00Z/2024-12-31T23:59:59Z", "limit": 100}
    try:
        r = SESSION.post(stac, json=body, timeout=120)
        rec = {"url": stac, "body": body, "status": r.status_code}
        if r.ok:
            j = r.json()
            feats = j.get("features", [])
            rec["matched"] = j.get("numberMatched") or j.get("context", {}).get("matched")
            rec["returned"] = len(feats)
            rec["platforms"] = sorted({f["properties"].get("platform") for f in feats})
            rec["cloud_cover_lt_20"] = sum(1 for f in feats if (f["properties"].get("eo:cloud_cover") or 100) < 20)
            if feats:
                a = feats[0]["assets"]
                rec["asset_keys"] = sorted(a)[:40]
                rec["example_href"] = (a.get("red") or a.get("SR_B4") or next(iter(a.values()))).get("href")
                rec["alternate_s3"] = ((a.get("red") or {}).get("alternate") or {}).get("s3", {}).get("href")
            save_sample("landsat_stac_S1_2024_first_item.json", feats[0] if feats else j)
        else:
            rec["error"] = r.text[:800]
        out["landsat_stac"] = rec
        r = SESSION.get("https://landsatlook.usgs.gov/stac-server/collections", timeout=60)
        out["landsat_stac_collections"] = [c["id"] for c in r.json().get("collections", [])] if r.ok else r.status_code
        if rec.get("example_href"):
            rr = SESSION.get(rec["example_href"], allow_redirects=False, timeout=60, stream=True)
            out["landsat_asset_http"] = {"status": rr.status_code, "location_host": re.sub(r"^(https?://[^/]+).*", r"\1", rr.headers.get("Location", ""))}
            rr.close()
    except Exception as exc:  # noqa: BLE001
        out["landsat_stac"] = {"url": stac, "error": repr(exc)}

    # Landsat ARD (the product AppEEARS serves as L08.002/L09.002) versus global L2, at S1 and S4.
    ard = {}
    for sid in ("S1", "S4"):
        s = SITES[sid]
        for col in ("landsat-c2ard-sr", "landsat-c2l2-sr"):
            b = {"collections": [col], "intersects": {"type": "Point", "coordinates": [s["lon"], s["lat"]]},
                 "datetime": "2024-01-01T00:00:00Z/2024-12-31T23:59:59Z", "limit": 100}
            r = SESSION.post(stac, json=b, timeout=120)
            ard[f"{sid}_{col}"] = len(r.json().get("features", [])) if r.ok else f"HTTP {r.status_code}"
    out["landsat_ard_vs_l2_2024"] = ard

    # Coverage questions raised by the CMR run.
    def gcount(cid, **extra):
        p = {"collection_concept_id": cid, "page_size": 1, **extra}
        r = SESSION.get(f"{CMR}/granules.json", params=p, timeout=60)
        ent = r.json()["feed"]["entry"] if r.ok else []
        return {"url": r.url, "hits": r.headers.get("CMR-Hits"),
                "first": ent[0].get("time_start") if ent else None}

    cov = {}
    for label, cid in [("ECO_L2T_LSTE_v003", "C3998139651-LPCLOUD"), ("ECO_L3T_JET_v003", "C4057232489-LPCLOUD"),
                       ("ECO_L4T_ESI_v003", "C4057232495-LPCLOUD"), ("ECO_L3T_ET_ALEXI_v002", "C2076105456-LPCLOUD"),
                       ("GEDI02_A_v003", "C3974616071-LPCLOUD"), ("GEDI02_A_v002", "C2142771958-LPCLOUD"),
                       ("GEDI_L4A_v2_1", "C2237824918-ORNL_CLOUD")]:
        cov[label] = {"S1_all_time": gcount(cid, point=point),
                      "S1_all_time_oldest": gcount(cid, point=point, sort_key="start_date"),
                      "global_oldest": gcount(cid, sort_key="start_date"),
                      "global_newest": gcount(cid, sort_key="-start_date")}
    for sid in ("S2", "S3", "S4"):
        s = SITES[sid]
        cov[f"GEDI02_A_v002_{sid}_all_time"] = gcount("C2142771958-LPCLOUD", point=f"{s['lon']},{s['lat']}")
        cov[f"ECO_L2T_LSTE_v002_{sid}_2024"] = gcount("C2076090826-LPCLOUD", point=f"{s['lon']},{s['lat']}",
                                                     temporal="2024-01-01T00:00:00Z,2024-12-31T23:59:59Z")
        cov[f"HLSL30_{sid}_2024"] = gcount("C2021957657-LPCLOUD", point=f"{s['lon']},{s['lat']}",
                                           temporal="2024-01-01T00:00:00Z,2024-12-31T23:59:59Z")
        cov[f"HLSS30_{sid}_2024"] = gcount("C2021957295-LPCLOUD", point=f"{s['lon']},{s['lat']}",
                                           temporal="2024-01-01T00:00:00Z,2024-12-31T23:59:59Z")
    # Granules per year at S1, to see which years each version covers.
    per_year = {}
    for label, cid in [("ECO_L2T_LSTE_v003", "C3998139651-LPCLOUD"), ("ECO_L3T_JET_v003", "C4057232489-LPCLOUD"),
                       ("ECO_L2T_LSTE_v002", "C2076090826-LPCLOUD"), ("GEDI02_A_v003", "C3974616071-LPCLOUD"),
                       ("ECO_L3T_ET_ALEXI_v002", "C2076105456-LPCLOUD")]:
        per_year[label] = {}
        for y in range(2018, 2027):
            r = SESSION.get(f"{CMR}/granules.json", timeout=60,
                            params={"collection_concept_id": cid, "point": point, "page_size": 0,
                                    "temporal": f"{y}-01-01T00:00:00Z,{y}-12-31T23:59:59Z"})
            per_year[label][y] = r.headers.get("CMR-Hits")
    cov["S1_granules_per_year"] = per_year
    # IMERG V08: is any version 08 collection registered yet?
    r = SESSION.get(f"{CMR}/collections.json", params={"short_name": "GPM_3IMERG*", "version": "08",
                                                     "options[short_name][pattern]": "true"}, timeout=60)
    cov["imerg_v08_collections"] = {"url": r.url, "hits": r.headers.get("CMR-Hits")}
    out["coverage"] = cov
    return out


# --------------------------------------------------------------------------
# 6. Cropland check of the US study points (USDA CropScape, no auth)
# --------------------------------------------------------------------------
NON_CROP = {"Grass/Pasture", "Developed/Open Space", "Developed/Low Intensity", "Developed/Med Intensity",
            "Developed/High Intensity", "Shrubland", "Fallow/Idle Cropland", "Open Water", "Barren",
            "Deciduous Forest", "Evergreen Forest", "Mixed Forest", "Woody Wetlands",
            "Herbaceous Wetlands", "Grassland/Pasture", "Background"}


def cdl_value(lat: float, lon: float, year: int = 2024) -> dict:
    from rasterio.warp import transform
    xs, ys = transform("EPSG:4326", "EPSG:5070", [lon], [lat])
    url = "https://nassgeodata.gmu.edu/axis2/services/CDLService/GetCDLValue"
    params = {"year": year, "x": round(xs[0], 1), "y": round(ys[0], 1)}
    try:
        r, _ = timed_get(url, params=params, timeout=60)
        m = re.search(r"category\s*:\s*\"?([^,\"}]+)", r.text)
        return {"url": r.url, "status": r.status_code, "category": m.group(1) if m else None}
    except Exception as exc:  # noqa: BLE001
        return {"url": url, "params": params, "error": repr(exc)}


def cdl_probe() -> dict:
    """Check the US study points against the 2024 Cropland Data Layer and, if a point
    is not on a crop, walk outward on a 0.005 degree ring until we hit one."""
    out = {}
    for sid in ("S1", "S2", "S3"):
        s = SITES[sid]
        rec = {"given": cdl_value(s["lat"], s["lon"])}
        if rec["given"].get("category") in NON_CROP:
            found = None
            for ring in range(1, 7):
                d = 0.005 * ring
                for dlat, dlon in [(d, 0), (-d, 0), (0, d), (0, -d), (d, d), (-d, -d), (d, -d), (-d, d)]:
                    lat, lon = round(s["lat"] + dlat, 4), round(s["lon"] + dlon, 4)
                    v = cdl_value(lat, lon)
                    if v.get("category") and v["category"] not in NON_CROP:
                        found = {"lat": lat, "lon": lon, **v}
                        break
                if found:
                    break
            rec["nearest_crop"] = found
        out[sid] = rec
    return out


PROBES = {"power": power_probe, "cmr": cmr_probe, "appeears": appeears_probe,
          "gibs": gibs_probe, "earthaccess": earthaccess_probe, "followup": followup_probe,
          "cdl": cdl_probe}


def write_summaries() -> None:
    """Write compact, valid-JSON summaries of the large results into ../samples/."""
    cmr = CACHE / "probe_cmr.json"
    if cmr.exists():
        d = json.loads(cmr.read_text(encoding="utf-8"))
        (SAMPLES / "cmr_query_urls.txt").write_text("\n".join(d.get("queries", [])) + "\n", encoding="utf-8")
        rows = []
        for r in d.get("collections", []):
            if not r.get("found"):
                rows.append(r)
                continue
            sizes = [g["size_mb_per_file"] for g in r.get("granule_samples", [])[:3]]
            rows.append({k: r.get(k) for k in (
                "group", "short_name", "version", "concept_id", "provider", "daac", "cloud_hosted",
                "time_start", "time_end", "collection_progress", "spatial_resolution", "formats", "doi",
                "granules_S1_2024", "granules_S1_2024_url", "total_granules", "newest_granule",
                "granule_size_source", "s3_prefixes")}
                | {"granule_mb_per_file_samples": sizes,
                   "first_granule": (r.get("granule_samples") or [{}])[0].get("granule_ur"),
                   "services": [(s.get("name"), s.get("type")) for s in r.get("services", []) if isinstance(s, dict)],
                   "tools": [t.get("name") for t in r.get("tools", []) if isinstance(t, dict)],
                   "harmony_flags": sorted(k for k, v in ((r.get("service_features") or {}).get("harmony") or {}).items() if v),
                   "n_variables": r.get("n_variables"),
                   "variables_first_25": (r.get("variable_names") or [])[:25]})
        save_sample("cmr_collections_summary.json", rows)
        save_sample("cmr_keyword_searches.json", d.get("keyword_searches"))
    app = CACHE / "probe_appeears.json"
    if app.exists():
        d = json.loads(app.read_text(encoding="utf-8"))
        save_sample("appeears_relevant_products_layers.json",
                    {pid: {k: v[k] for k in ("url", "resolution", "temporal_granularity", "temporal_extent", "source")}
                     | {"layers": sorted(v["layers"])} for pid, v in d.get("relevant", {}).items()})
        save_sample("appeears_all_product_ids.json", d.get("all_product_ids"))


def main(argv: list[str]) -> None:
    chosen = argv or list(PROBES)
    for name in chosen:
        t0 = time.time()
        print(f"== {name}", flush=True)
        try:
            res = PROBES[name]()
        except Exception as exc:  # noqa: BLE001
            res = {"fatal_error": repr(exc)}
        res["_run_utc"] = pd.Timestamp.utcnow().isoformat()
        res["_seconds"] = round(time.time() - t0, 1)
        full = CACHE / f"probe_{name}.json"
        full.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
        save_sample(f"probe_{name}_result.json", res)
        print(f"   done in {res['_seconds']} s, full result at {full}", flush=True)
    write_summaries()


if __name__ == "__main__":
    main(sys.argv[1:])
