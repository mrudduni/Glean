"""MOD13Q1 NDVI from the ORNL DAAC MODIS/VIIRS Land Product Subsets service (no login).

Fallback for AppEEARS (handover §6.2). Two modes:

  demo  : a 9x9-pixel (~2 km) subset around each demo field, every 16-day composite
          2000–2025; we keep the pixels whose centres fall inside the field outline.
          -> raw/modis_ornl/{fid}_pixels.csv  (date, pixel, ndvi, reliability, inside)
  area  : one large subset covering the neighbour pool, Jun–Aug composites for 2012
          and 2016–2025 only (what Farms Like Yours needs).
          -> raw/modis_ornl/area_{band}_{date}.npy + area_grid.json

The API returns at most 10 composites per request.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from pyproj import Transformer  # noqa: E402

import config as C  # noqa: E402
from common import cached_json, get_json, load_fields_draft, log  # noqa: E402

API = "https://modis.ornl.gov/rst/api/v1/MOD13Q1"
DIR = C.RAW / "modis_ornl"
BANDS = {"ndvi": "250m_16_days_NDVI", "rel": "250m_16_days_pixel_reliability"}
SINU = "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +R=6371007.181 +units=m +no_defs"
TO_LL = Transformer.from_crs(SINU, "EPSG:4326", always_xy=True)
OUTPUTS = [DIR / f"{fid}_pixels.csv" for fid in C.FIELD_IDS]
AREA_YEARS = [2012] + list(range(2016, 2026))
WORKERS = 4


def dates_for(lat: float, lon: float) -> list[dict]:
    """MOD13Q1 composite dates. They are global, so one cached list serves every location."""
    cached = sorted(DIR.glob("dates_*.json"))
    path = cached[0] if cached else DIR / f"dates_{lat:.3f}_{lon:.3f}.json"
    d = cached_json(path, lambda: get_json(f"{API}/dates", params={"latitude": lat, "longitude": lon}, service="ornl"))
    return [x for x in d["dates"] if C.MODIS_START <= x["calendar_date"] <= C.MODIS_END]


def subset(lat: float, lon: float, band: str, d0: str, d1: str, km: int, tag: str) -> dict:
    cache = DIR / "chunks" / f"{tag}_{band}_{d0}_{d1}.json"
    return cached_json(cache, lambda: get_json(f"{API}/subset", timeout=300, service="ornl", params={
        "latitude": lat, "longitude": lon, "band": band, "startDate": d0, "endDate": d1,
        "kmAboveBelow": km, "kmLeftRight": km}))


def _pixel_centres(meta: dict) -> tuple[np.ndarray, np.ndarray]:
    nrows, ncols, cs = int(meta["nrows"]), int(meta["ncols"]), float(meta["cellsize"])
    xll, yll = float(meta["xllcorner"]), float(meta["yllcorner"])
    cols, rows = np.meshgrid(np.arange(ncols), np.arange(nrows))
    x = xll + (cols + 0.5) * cs
    y = yll + (nrows - rows - 0.5) * cs   # data are listed row by row from the top
    lon, lat = TO_LL.transform(x.ravel(), y.ravel())
    return np.asarray(lon), np.asarray(lat)


def _chunks(dates: list[dict], n: int = 10):
    for i in range(0, len(dates), n):
        yield dates[i:i + n]


def demo(force: bool = False) -> None:
    from shapely.geometry import Point

    from concurrent.futures import ThreadPoolExecutor, as_completed

    gdf = load_fields_draft()
    todo = {fid: g for fid, g in gdf.geometry.items() if force or not (DIR / f"{fid}_pixels.csv").exists()}
    # 1. prefetch every (field, band, 10-composite chunk) in parallel; each is cached on disk.
    #    The service is slow (minutes per request at busy times), so a few workers help a lot.
    jobs = []
    for fid, geom in todo.items():
        c = geom.representative_point()
        lat, lon = round(c.y, 5), round(c.x, 5)
        for ch in _chunks(dates_for(lat, lon)):
            for band in BANDS.values():
                jobs.append((lat, lon, band, ch[0]["modis_date"], ch[-1]["modis_date"], fid))
    log("modis_ornl", f"{len(jobs)} subset requests (cached ones return instantly)")
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(subset, *j[:5], 1, j[5]) for j in jobs]
        for n, f in enumerate(as_completed(futs), 1):
            f.result()
            if n % 20 == 0 or n == len(futs):
                log("modis_ornl", f"{n}/{len(futs)} requests done")
    # 2. assemble from cache
    for fid, geom in todo.items():
        out = DIR / f"{fid}_pixels.csv"
        c = geom.representative_point()
        lat, lon = round(c.y, 5), round(c.x, 5)
        dates = dates_for(lat, lon)
        rows = []
        inside = None
        for i, ch in enumerate(_chunks(dates)):
            got = {}
            for key, band in BANDS.items():
                res = subset(lat, lon, band, ch[0]["modis_date"], ch[-1]["modis_date"], 1, fid)
                if inside is None:
                    plon, plat = _pixel_centres(res)
                    inside = np.array([geom.contains(Point(a, b)) for a, b in zip(plon, plat)])
                for s in res["subset"]:
                    got.setdefault(s["calendar_date"], {})[key] = np.asarray(s["data"], dtype=float)
            for date, v in got.items():
                if "ndvi" not in v or "rel" not in v:
                    continue
                for px, (n, q) in enumerate(zip(v["ndvi"], v["rel"])):
                    rows.append((date, px, n, q, bool(inside[px])))
            if i % 10 == 0:
                log("modis_ornl", f"{fid}: {min((i + 1) * 10, len(dates))}/{len(dates)} composites")
        df = pd.DataFrame(rows, columns=["date", "pixel", "ndvi_raw", "reliability", "inside"])
        DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
        log("modis_ornl", f"{fid}: {df.date.nunique()} composites, {int(inside.sum())} pixels inside field")


def area(center_lat: float, center_lon: float, km: int, force: bool = False) -> Path:
    """Jun–Aug composites for AREA_YEARS over a (2km+1)^2 box; returns the grid json path."""
    grid_p = DIR / "area_grid.json"
    dates = [d for d in dates_for(round(center_lat, 3), round(center_lon, 3))
             if int(d["calendar_date"][:4]) in AREA_YEARS and d["calendar_date"][5:7] in ("06", "07", "08")]
    tag = f"area{km}_{center_lat:.3f}_{center_lon:.3f}"
    meta = None
    for i, ch in enumerate(_chunks(dates)):
        for key, band in BANDS.items():
            if all((DIR / "area" / f"{key}_{d['calendar_date']}.npy").exists() for d in ch) and not force \
                    and grid_p.exists():
                continue
            res = subset(round(center_lat, 3), round(center_lon, 3), band,
                         ch[0]["modis_date"], ch[-1]["modis_date"], km, tag)
            meta = {k: res[k] for k in ("xllcorner", "yllcorner", "cellsize", "nrows", "ncols")}
            (DIR / "area").mkdir(parents=True, exist_ok=True)
            for s in res["subset"]:
                arr = np.asarray(s["data"], dtype=np.int16).reshape(int(res["nrows"]), int(res["ncols"]))
                np.save(DIR / "area" / f"{key}_{s['calendar_date']}.npy", arr)
            # drop the bulky chunk cache once saved as npy
            (DIR / "chunks" / f"{tag}_{band}_{ch[0]['modis_date']}_{ch[-1]['modis_date']}.json").unlink(missing_ok=True)
        log("modis_ornl", f"area: {min((i + 1) * 10, len(dates))}/{len(dates)} composites")
    if meta:
        grid_p.write_text(json.dumps(meta))
    return grid_p


def area_for_pool(force: bool = False) -> Path | None:
    """Area subset centred on the demo fields, just large enough to cover the neighbour pool."""
    import math

    import geopandas as gpd

    pool_p = C.RAW / "neighbors" / "pool.geojson"
    if not pool_p.exists():
        log("modis_ornl", "area: neighbour pool not built yet")
        return None
    if (C.RAW / "appeears" / "neighbor_points" / ".done").exists() and not force:
        log("modis_ornl", "area: AppEEARS neighbour NDVI already downloaded; skipping")
        return None
    pool = gpd.read_file(pool_p)
    c = load_fields_draft().to_crs(C.CRS_UTM14).geometry.representative_point().to_crs(C.CRS_WGS84)
    clat, clon = float(c.y.mean()), float(c.x.mean())
    far = max(math.hypot((x - clon) * 88.0, (y - clat) * 111.0) for x, y in zip(pool.lon, pool.lat))
    km = min(100, int(math.ceil(far + 2)))
    log("modis_ornl", f"area: centre {clat:.3f},{clon:.3f} ±{km} km")
    return area(clat, clon, km, force)


def main(force: bool = False) -> None:
    if (C.RAW / "appeears" / "demo_points" / ".done").exists() and not force:
        log("modis_ornl", "AppEEARS demo NDVI already downloaded; ORNL fallback not needed")
    else:
        demo(force)
    area_for_pool(force)


if __name__ == "__main__":
    force = "--force" in sys.argv
    if "demo" in sys.argv:
        demo(force)
    elif "area" in sys.argv:
        area_for_pool(force)
    else:
        main(force)
