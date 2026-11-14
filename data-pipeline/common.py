"""Small helpers shared by every step: JSON/CSV writing, _meta, HTTP, geometry."""
from __future__ import annotations

import json
import math
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config as C


# ---------------------------------------------------------------- logging
def log(step: str, msg: str) -> None:
    print(f"[{step}] {msg}", flush=True)


class Skip(Exception):
    """Raised by a step that cannot run yet (missing key, missing input)."""


# ---------------------------------------------------------------- _meta + JSON
def meta(schema_name: str, generator: str, version: int = 1, notes: str | None = None) -> dict:
    m = {
        "schema": f"{schema_name}@{version}",
        "mock": False,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": f"data-pipeline/{generator}",
    }
    if notes:
        m["notes"] = notes  # optional extra key; safe per README §6.2 rule 3
    return m


def _clean(o: Any) -> Any:
    """Recursively replace NaN/Inf with None and numpy scalars with Python ones."""
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        f = float(o)
        return None if (math.isnan(f) or math.isinf(f)) else f
    if isinstance(o, np.bool_):
        return bool(o)
    if o is pd.NaT:
        return None
    return o


def write_json(path: Path, obj: dict, compact: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    obj = _clean(obj)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        if compact:
            json.dump(obj, f, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        else:
            json.dump(obj, f, ensure_ascii=False, indent=1, allow_nan=False)
        f.write("\n")
    size = path.stat().st_size
    if size > 2_000_000:
        print(f"  WARNING {path.name} is {size/1e6:.1f} MB (> 2 MB budget)")


def read_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_csv(path: Path, df: pd.DataFrame, columns: list[str]) -> None:
    """Write with the exact column order from README §8.2; NaN -> empty cell."""
    path.parent.mkdir(parents=True, exist_ok=True)
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name}: missing columns {missing}")
    df[columns].to_csv(path, index=False, na_rep="", lineterminator="\n")


def r(x, nd: int = 0):
    """Round, keeping None/NaN as None. nd=0 returns int."""
    if x is None:
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return int(round(f)) if nd == 0 else round(f, nd)


# ---------------------------------------------------------------- HTTP
_session: requests.Session | None = None


def session() -> requests.Session:
    global _session
    if _session is None:
        s = requests.Session()
        # Retry server errors on GET only. No automatic retry on 429 (each retry can spend
        # quota) and none on POST (OpenET/SDA/PRISM/AppEEARS posts may each count as a request).
        retry = Retry(total=3, backoff_factor=2, status_forcelist=(500, 502, 503, 504),
                      allowed_methods=frozenset(["GET"]))
        s.mount("https://", HTTPAdapter(max_retries=retry))
        s.mount("http://", HTTPAdapter(max_retries=retry))
        s.headers["User-Agent"] = C.USER_AGENT
        _session = s
    return _session


# ---------------------------------------------------------------- request budgets
# Every call to an outside service is counted here so no run can exceed a free tier.
# Only OpenET enforces a hard free quota (it stopped us at ~100 requests in a month); the
# others publish no request limit, so these are conservative self-imposed caps sized well
# above what one full run needs. Counts persist in raw/usage.json across runs.
#   service: (max requests per period, period, min seconds between requests)
BUDGETS: dict[str, tuple[int, str, float]] = {
    "openet":    (90,     "month", 1.0),   # one full run: 3 polygons + 150 points
    "nass":      (300,    "day",   1.0),   # one full run: ~20 queries
    "appeears":  (200,    "day",   1.0),   # login/submit/status/bundle calls, not file bytes
    "gesdisc":   (12_000, "day",   0.25),  # IMERG: one tiny subset per day, ~9,500 in total
    "earthdata": (60,     "day",   1.0),   # CMR searches + GRACE download
    "power":     (100,    "day",   1.0),
    "prism":     (20,     "day",   2.0),
    "sda":       (500,    "day",   0.5),
    "usgs":      (200,    "hour",  1.0),
    "ornl":      (3_000,  "day",   0.0),   # slow service; concurrency capped in modis_ornl.py
}
USAGE = C.RAW / "usage.json"
_usage_lock = threading.Lock()
_last_call: dict[str, float] = {}


def _period_key(period: str) -> str:
    now = datetime.now(timezone.utc)
    return now.strftime({"month": "%Y-%m", "day": "%Y-%m-%d", "hour": "%Y-%m-%dT%H"}[period])


def _usage_rec(u: dict, service: str) -> dict:
    key = _period_key(BUDGETS[service][1])
    rec = u.get(service, {})
    return rec if rec.get("period") == key else {"period": key, "used": 0}


def _save_usage(u: dict) -> None:
    USAGE.parent.mkdir(parents=True, exist_ok=True)
    tmp = USAGE.with_name(USAGE.name + ".tmp")
    tmp.write_text(json.dumps(u, indent=1))
    tmp.replace(USAGE)


def spend(service: str, n: int = 1) -> None:
    """Count n requests to `service`; raise Skip instead of going over its budget.
    Also spaces calls to the same service by its minimum gap (threads queue here)."""
    limit, period, gap = BUDGETS[service]
    with _usage_lock:
        u = read_json(USAGE) if USAGE.exists() else {}
        rec = _usage_rec(u, service)
        if rec.get("blocked"):
            raise Skip(f"{service}: the server reported its limit reached ({rec['blocked']}); "
                       f"no more calls until the next {period} (UTC)")
        if rec["used"] + n > limit:
            raise Skip(f"{service}: local budget of {limit} requests per {period} used up; "
                       f"rerun next {period} (UTC) to continue")
        wait = _last_call.get(service, 0.0) + gap - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_call[service] = time.monotonic()
        rec["used"] += n
        u[service] = rec
        _save_usage(u)


def mark_exhausted(service: str, why: str) -> None:
    """Stop all calls to `service` for the rest of the current budget period."""
    with _usage_lock:
        u = read_json(USAGE) if USAGE.exists() else {}
        rec = _usage_rec(u, service)
        rec["blocked"] = why[:160]
        u[service] = rec
        _save_usage(u)


def note_response(service: str, resp: requests.Response) -> None:
    """Act on rate-limit signals: 429 stops the service now; a low
    X-RateLimit-Remaining header stops it before the next call would fail."""
    if resp.status_code == 429:
        why = f"HTTP 429, Retry-After {resp.headers.get('Retry-After', '?')}"
        mark_exhausted(service, why)
        raise Skip(f"{service}: {why}; stopped, rerun later")
    rem = resp.headers.get("X-RateLimit-Remaining")
    if rem is not None and rem.strip().lstrip("-").isdigit() and int(rem) <= 5:
        mark_exhausted(service, f"X-RateLimit-Remaining {rem}")


def request(service: str, method: str, url: str, sess: requests.Session | None = None, **kw) -> requests.Response:
    """A budgeted HTTP call: spend() first, then note_response()."""
    spend(service)
    resp = (sess or session()).request(method, url, **kw)
    note_response(service, resp)
    return resp


def usage_report() -> dict:
    """Current-period usage per service, for logs: {service: (used, limit, period)}."""
    u = read_json(USAGE) if USAGE.exists() else {}
    return {s: (_usage_rec(u, s)["used"], b[0], b[1]) for s, b in BUDGETS.items()}


def get_json(url: str, params: dict | None = None, timeout: int = 120, service: str | None = None, **kw) -> Any:
    if service:
        resp = request(service, "GET", url, params=params, timeout=timeout, **kw)
    else:
        resp = session().get(url, params=params, timeout=timeout, **kw)
    resp.raise_for_status()
    return resp.json()


def download(url: str, dest: Path, chunk: int = 1 << 20, **kw) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with session().get(url, stream=True, timeout=300, **kw) as resp:
        resp.raise_for_status()
        with open(tmp, "wb") as f:
            for block in resp.iter_content(chunk):
                f.write(block)
    tmp.replace(dest)
    return dest


def cached_json(path: Path, fetch, max_age_days: float | None = None):
    """Return JSON from `path` if present (and fresh), else call fetch() and cache it."""
    if path.exists():
        if max_age_days is None or (time.time() - path.stat().st_mtime) < max_age_days * 86400:
            return read_json(path)
    data = fetch()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{threading.get_ident()}.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f)
    tmp.replace(path)  # atomic: an interrupted run never leaves a half-written cache
    return data


# ---------------------------------------------------------------- fields
def load_fields_draft():
    """Load raw/fields_draft.geojson as a GeoDataFrame indexed by field id."""
    import geopandas as gpd

    p = C.RAW / "fields_draft.geojson"
    if not p.exists():
        raise Skip("raw/fields_draft.geojson missing — run process/select_fields.py first")
    gdf = gpd.read_file(p).set_index("id")
    return gdf.loc[C.FIELD_IDS]


def field_points(gdf) -> dict[str, list[tuple[str, float, float]]]:
    """Centre + 4 interior points per field: {fid: [(pid, lon, lat), ...]}."""
    out: dict[str, list[tuple[str, float, float]]] = {}
    utm = gdf.to_crs(C.CRS_UTM14)
    for fid, geom in utm.geometry.items():
        c = geom.representative_point() if not geom.contains(geom.centroid) else geom.centroid
        pts = [("c", c)]
        # four points halfway between centre and the edge, N/E/S/W
        minx, miny, maxx, maxy = geom.bounds
        for name, (dx, dy) in {"n": (0, 1), "e": (1, 0), "s": (0, -1), "w": (-1, 0)}.items():
            from shapely.geometry import Point

            half = 0.25 * ((maxx - minx) if dx else (maxy - miny))
            p = Point(c.x + dx * half, c.y + dy * half)
            if geom.contains(p):
                pts.append((name, p))
        import geopandas as gpd

        g = gpd.GeoSeries([p for _, p in pts], crs=C.CRS_UTM14).to_crs(C.CRS_WGS84)
        out[fid] = [(f"{fid}_{n}", float(q.x), float(q.y)) for (n, _), q in zip(pts, g)]
    return out


# ---------------------------------------------------------------- geometry
def simplify_to(geom, max_vertices: int, crs_metric=None):
    """Simplify a (multi)polygon until its exterior has <= max_vertices vertices.

    `geom` must be in a metric CRS. Returns the largest polygon if multi.
    """
    from shapely.geometry import MultiPolygon, Polygon

    if isinstance(geom, MultiPolygon):
        geom = max(geom.geoms, key=lambda g: g.area)
    geom = Polygon(geom.exterior)  # drop holes: display outline only
    tol = 0.5
    g = geom
    while len(g.exterior.coords) > max_vertices and tol < 500:
        g = geom.simplify(tol, preserve_topology=True)
        tol *= 1.6
    return g


def polygon_geojson(geom_wgs84, nd: int = 6) -> dict:
    coords = [[round(x, nd), round(y, nd)] for x, y in geom_wgs84.exterior.coords]
    return {"type": "Polygon", "coordinates": [coords]}


def circularity(geom_metric) -> float:
    """4*pi*A/P^2: 1.0 for a circle, ~0.785 for a square."""
    if geom_metric.length == 0:
        return 0.0
    return 4 * math.pi * geom_metric.area / geom_metric.length ** 2


def pivot_fill(geoms):
    """Area / area of the minimum bounding circle: ~1.0 for a pivot circle, 0.64 for a square.

    More robust than perimeter-based circularity on CSB's raster-derived, jagged outlines.
    """
    import shapely

    vals = getattr(geoms, "values", geoms)
    radius = shapely.minimum_bounding_radius(vals)
    return shapely.area(vals) / (math.pi * radius ** 2)


def haversine_km(lon1, lat1, lon2, lat2) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def ols_slope(x: Iterable[float], y: Iterable[float]) -> float | None:
    x = np.asarray(list(x), dtype=float)
    y = np.asarray(list(y), dtype=float)
    ok = ~(np.isnan(x) | np.isnan(y))
    if ok.sum() < 3:
        return None
    return float(np.polyfit(x[ok], y[ok], 1)[0])


def decimal_year(dates) -> np.ndarray:
    d = pd.to_datetime(pd.Series(dates))
    return (d.dt.year + (d.dt.dayofyear - 1) / 365.25).to_numpy()


def ensure_import_path() -> None:
    """Allow `python fetch/x.py` as well as `python -m fetch.x`."""
    if str(C.ROOT) not in sys.path:
        sys.path.insert(0, str(C.ROOT))


def rel(p: Path) -> str:
    """Path relative to data-pipeline/ for log lines (absolute if outside it)."""
    try:
        return str(Path(p).relative_to(C.ROOT))
    except ValueError:
        return str(p)
