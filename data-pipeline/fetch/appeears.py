"""NASA AppEEARS: submit / poll / download point and area tasks.

Tasks (state kept in raw/appeears/tasks.json so reruns never resubmit):
  demo_points      5 points per demo field: MODIS NDVI, SMAP L4, ECOSTRESS ET + ESI
  neighbor_points  every neighbour centre: MODIS NDVI (+ reliability)
  neighbor_esi     every neighbour centre: ECOSTRESS ESI, Jun–Aug 2018–2025
  srtm             county polygon: SRTMGL1 DEM GeoTIFF

Usage:
  python fetch/appeears.py            submit missing tasks, download finished ones
  python fetch/appeears.py status     print task states
  python fetch/appeears.py --force    resubmit everything (e.g. after fields change)

Needs EARTHDATA_USERNAME / EARTHDATA_PASSWORD in data-pipeline/.env.
Downloads land in raw/appeears/<task>/.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config as C  # noqa: E402
from common import Skip, field_points, load_fields_draft, log, read_json, request  # noqa: E402

API = "https://appeears.earthdatacloud.nasa.gov/api"
DIR = C.RAW / "appeears"
STATE = DIR / "tasks.json"
TOKEN = DIR / "token.json"
OUTPUTS = [DIR / "demo_points" / ".done"]

# product prefix -> wanted layers (regex), resolved against /product at submit time
DEMO_LAYERS = {
    "MOD13Q1": [r"^_250m_16_days_NDVI$", r"^_250m_16_days_pixel_reliability$"],
    "SPL4SMGP": [r"^Geophysical_Data_sm_rootzone$", r"^Geophysical_Data_sm_surface$"],
    "ECO_L3T_JET": [r"^ETdaily$", r"^cloud$"],
    "ECO_L4T_ESI": [r"^ESI$", r"^cloud$"],
}
NEIGHBOR_LAYERS = {"MOD13Q1": DEMO_LAYERS["MOD13Q1"]}
NEIGHBOR_ESI_LAYERS = {"ECO_L4T_ESI": DEMO_LAYERS["ECO_L4T_ESI"]}


# ---------------------------------------------------------------- auth + helpers
def token() -> str:
    if TOKEN.exists():
        t = read_json(TOKEN)
        if t.get("expires_at", 0) > time.time() + 3600:
            return t["token"]
    if not (C.EARTHDATA_USERNAME and C.EARTHDATA_PASSWORD):
        raise Skip("EARTHDATA_USERNAME / EARTHDATA_PASSWORD not set in data-pipeline/.env")
    resp = request("appeears", "POST", f"{API}/login", auth=(C.EARTHDATA_USERNAME, C.EARTHDATA_PASSWORD), timeout=60)
    resp.raise_for_status()
    t = resp.json()
    DIR.mkdir(parents=True, exist_ok=True)
    TOKEN.write_text(json.dumps({"token": t["token"], "expires_at": time.time() + 46 * 3600}))
    return t["token"]


def _h() -> dict:
    return {"Authorization": f"Bearer {token()}"}


def _state() -> dict:
    return read_json(STATE) if STATE.exists() else {}


def _save_state(s: dict) -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=1))


def resolve_layers(spec: dict[str, list[str]]) -> list[dict]:
    """Map product prefixes + layer regexes to exact ProductAndVersion / layer names."""
    products = request("appeears", "GET", f"{API}/product", timeout=60).json()
    out = []
    for prefix, patterns in spec.items():
        cands = sorted([p["ProductAndVersion"] for p in products
                        if p["ProductAndVersion"].split(".")[0] == prefix and p.get("Available", True)])
        if not cands:
            log("appeears", f"product {prefix} not available; skipping")
            continue
        pv = cands[-1]  # highest version
        layers = request("appeears", "GET", f"{API}/product/{pv}", timeout=60).json()
        for pat in patterns:
            hit = [name for name in layers if re.search(pat, name)]
            if not hit:
                raise RuntimeError(f"{pv}: no layer matches {pat}; have {list(layers)}")
            out.append({"product": pv, "layer": hit[0]})
    return out


def submit(name: str, body: dict) -> str:
    resp = request("appeears", "POST", f"{API}/task", json=body, headers=_h(), timeout=120)
    if resp.status_code >= 400:
        raise RuntimeError(f"AppEEARS submit {name}: {resp.status_code} {resp.text[:500]}")
    tid = resp.json()["task_id"]
    s = _state()
    s[name] = {"task_id": tid, "submitted": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "status": "queued"}
    _save_state(s)
    log("appeears", f"submitted {name}: {tid}")
    return tid


def status(tid: str) -> str:
    resp = request("appeears", "GET", f"{API}/task/{tid}", headers=_h(), timeout=60)
    resp.raise_for_status()
    return resp.json().get("status", "unknown")


POLL_GAP_S = 300   # never ask AppEEARS about the same task more than once per 5 minutes


def polled_status(info: dict) -> str:
    """Task status, re-asked only if the last check is older than POLL_GAP_S (kept in tasks.json)."""
    if time.time() - info.get("checked_at", 0) < POLL_GAP_S and info.get("status") not in (None, "queued"):
        return info["status"]
    info["status"] = status(info["task_id"])
    info["checked_at"] = time.time()
    return info["status"]


def download_bundle(name: str, tid: str) -> None:
    dest = DIR / name
    dest.mkdir(parents=True, exist_ok=True)
    bundle = request("appeears", "GET", f"{API}/bundle/{tid}", headers=_h(), timeout=60).json()
    for f in bundle["files"]:
        fn = f["file_name"].split("/")[-1]
        p = dest / fn
        if p.exists() and p.stat().st_size == f.get("file_size", p.stat().st_size):
            continue
        with request("appeears", "GET", f"{API}/bundle/{tid}/{f['file_id']}", headers=_h(), stream=True,
                           timeout=600, allow_redirects=True) as r:
            r.raise_for_status()
            with open(p, "wb") as out:
                for chunk in r.iter_content(1 << 20):
                    out.write(chunk)
        log("appeears", f"{name}: downloaded {fn}")
    (dest / ".done").write_text(tid)


# ---------------------------------------------------------------- task bodies
def _point_body(name: str, coords: list[dict], layers: list[dict], dates: list[dict]) -> dict:
    return {"task_type": "point", "task_name": f"brackets_{name}",
            "params": {"dates": dates, "layers": layers, "coordinates": coords}}


def demo_points_body() -> dict:
    pts = field_points(load_fields_draft())
    coords = [{"id": pid, "category": fid, "latitude": round(lat, 6), "longitude": round(lon, 6)}
              for fid, plist in pts.items() for pid, lon, lat in plist]
    dates = [{"startDate": "01-01-2000", "endDate": "12-31-2025"}]
    return _point_body("demo_points", coords, resolve_layers(DEMO_LAYERS), dates)


def _neighbor_coords() -> list[dict]:
    p = C.RAW / "neighbors" / "pool.geojson"
    if not p.exists():
        raise Skip("neighbour pool not built yet (neighbors/pool.py select)")
    import geopandas as gpd

    pool = gpd.read_file(p)
    return [{"id": str(r.nid), "category": "neighbor", "latitude": round(r.lat, 6),
             "longitude": round(r.lon, 6)} for r in pool.itertuples()]


def neighbor_points_body() -> dict:
    dates = [{"startDate": "01-01-2000", "endDate": "12-31-2025"}]
    return _point_body("neighbor_points", _neighbor_coords(), resolve_layers(NEIGHBOR_LAYERS), dates)


def neighbor_esi_body() -> dict:
    dates = [{"startDate": "06-01", "endDate": "08-31", "recurring": True, "yearRange": [2018, 2025]}]
    return _point_body("neighbor_esi", _neighbor_coords(), resolve_layers(NEIGHBOR_ESI_LAYERS), dates)


def srtm_body() -> dict:
    county = read_json(C.RAW / f"county_{C.COUNTY_FIPS_FULL}.geojson")
    return {"task_type": "area", "task_name": "brackets_srtm",
            "params": {"dates": [{"startDate": "02-11-2000", "endDate": "02-21-2000"}],
                       "layers": [{"product": "SRTMGL1_NC.003", "layer": "SRTMGL1_DEM"}],
                       "geo": county,
                       "output": {"format": {"type": "geotiff"}, "projection": "geographic"}}}


TASKS = {"demo_points": demo_points_body, "srtm": srtm_body,
         "neighbor_points": neighbor_points_body, "neighbor_esi": neighbor_esi_body}


# ---------------------------------------------------------------- driver
def run(force: bool = False) -> dict:
    s = _state()
    for name, body_fn in TASKS.items():
        if name in s and not force:
            continue
        try:
            submit(name, body_fn())
        except Skip as e:
            log("appeears", f"{name}: not submitted ({e})")
    s = _state()
    for name, info in s.items():
        if (DIR / name / ".done").exists() and not force:
            info["status"] = "downloaded"
            continue
        st = polled_status(info)
        log("appeears", f"{name}: {st}")
        if st == "done":
            download_bundle(name, info["task_id"])
            info["status"] = "downloaded"
    _save_state(s)
    return s


def main(force: bool = False) -> None:
    if not (C.EARTHDATA_USERNAME and C.EARTHDATA_PASSWORD):
        raise Skip("EARTHDATA_USERNAME / EARTHDATA_PASSWORD not set in data-pipeline/.env")
    s = run(force)
    if s.get("demo_points", {}).get("status") != "downloaded":
        raise Skip("AppEEARS demo_points not finished yet — rerun later (poll every few minutes, not faster)")


if __name__ == "__main__":
    if "status" in sys.argv:
        st = _state()
        for k, v in st.items():
            print(k, v["task_id"], "downloaded" if (DIR / k / ".done").exists() else polled_status(v))
        _save_state(st)
    else:
        main(force="--force" in sys.argv)
