"""Field terrain: mean elevation, mean slope (%), and the low-spot flag.

DEM source, in order:
  1. SRTMGL1 GeoTIFF from the AppEEARS area task (raw/appeears/srtm/*SRTMGL1_DEM*.tif)
  2. fallback: USGS 3DEP 1/3" via the National Map ImageServer (no login)
Everything is computed in UTM 14N (EPSG:32614). slope = |grad z| * 100 using numpy
gradients; low_spot = field mean elevation >= 3 m below the mean of a 1 km ring.

Output: raw/terrain.json {fid: {elev_m, slope_pct, low_spot, ring_mean_m, source}}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from rasterio.features import geometry_mask  # noqa: E402
from rasterio.warp import Resampling, reproject  # noqa: E402

import config as C  # noqa: E402
from common import rel, download, load_fields_draft, log  # noqa: E402

OUT = C.RAW / "terrain.json"
OUTPUTS = [OUT]
TDEP = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage"


def _srtm_file() -> Path | None:
    hits = sorted((C.RAW / "appeears" / "srtm").glob("*SRTMGL1*DEM*.tif"))
    return hits[0] if hits else None


def _to_utm(src_path: Path, bounds_utm, res: float):
    """Reproject a DEM window to a UTM grid covering bounds_utm at `res` metres."""
    minx, miny, maxx, maxy = bounds_utm
    width, height = int((maxx - minx) / res), int((maxy - miny) / res)
    transform = rasterio.transform.from_origin(minx, maxy, res, res)
    dst = np.full((height, width), np.nan, dtype="float32")
    with rasterio.open(src_path) as src:
        reproject(rasterio.band(src, 1), dst, dst_transform=transform, dst_crs=C.CRS_UTM14,
                  resampling=Resampling.bilinear, dst_nodata=np.nan,
                  src_nodata=src.nodata if src.nodata is not None else -32768)
    return dst, transform


def _3dep(fid: str, bounds_utm, res: float = 10.0) -> Path:
    minx, miny, maxx, maxy = bounds_utm
    w, h = int((maxx - minx) / res), int((maxy - miny) / res)
    p = C.RAW / "terrain" / f"{fid}_3dep.tif"
    if not p.exists():
        download(TDEP, p, params={
            "bbox": f"{minx},{miny},{maxx},{maxy}", "bboxSR": 32614, "imageSR": 32614,
            "size": f"{w},{h}", "format": "tiff", "pixelType": "F32",
            "interpolation": "RSP_BilinearInterpolation", "f": "image"})
    return p


def stats(dem: np.ndarray, transform, geom_utm, ring_m: float = 1000) -> dict:
    res = transform.a
    gy, gx = np.gradient(dem, res)
    slope = np.hypot(gx, gy) * 100
    inside = ~geometry_mask([geom_utm], dem.shape, transform, invert=False)
    ring = ~geometry_mask([geom_utm.buffer(ring_m).difference(geom_utm)], dem.shape, transform, invert=False)
    f_mean, r_mean = float(np.nanmean(dem[inside])), float(np.nanmean(dem[ring]))
    return {"elev_m": round(f_mean, 1), "slope_pct": round(float(np.nanmean(slope[inside])), 2),
            "low_spot": bool(f_mean <= r_mean - 3), "ring_mean_m": round(r_mean, 1)}


def main(force: bool = False) -> None:
    if OUT.exists() and not force:
        upgraded = _srtm_file() and any(v.get("source") != "SRTM" for v in json.loads(OUT.read_text()).values())
        if not upgraded:
            log("terrain", f"exists: {OUT.name}")
            return
        log("terrain", "SRTM has arrived; recomputing terrain from it")
    gdf = load_fields_draft().to_crs(C.CRS_UTM14)
    srtm = _srtm_file()
    out = {}
    for fid, geom in gdf.geometry.items():
        b = geom.buffer(1500).bounds
        if srtm:
            dem, tr = _to_utm(srtm, b, 30.0)
            src = "SRTM"
        else:
            p = _3dep(fid, b)
            with rasterio.open(p) as ds:
                dem = ds.read(1).astype("float32")
                dem[dem < -1000] = np.nan
                tr = ds.transform
                if ds.crs is None or ds.crs.to_epsg() != 32614:
                    dem, tr = _to_utm(p, b, 10.0)
            src = "3DEP"
        s = stats(dem, tr, geom)
        s["source"] = src
        out[fid] = s
        log("terrain", f"{fid}: {s}")
    OUT.write_text(json.dumps(out, indent=1))
    log("terrain", f"wrote {rel(OUT)}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
