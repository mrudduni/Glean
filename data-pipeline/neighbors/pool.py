"""Farms Like Yours, step 1: the neighbour pool and its features.

  python neighbors/pool.py select     -> raw/neighbors/pool.geojson
      CSB fields within 25 km of any demo field, 20–130 ha, >= 6 known crop years,
      stratified by RotationClass (seed 42) up to 150 fields.
  python neighbors/pool.py features   -> raw/neighbors/pool_features.csv
      SSURGO at the centre; irrigated flag; MODIS drought NDVI; OpenET; ECOSTRESS ESI.

irrigated, first method that has data wins (recorded per field in `irr_method`):
  ndvi   : MODIS Jul–Aug NDVI peak >= 0.75 in at least half of 2018–2025
  shape  : proxy until NDVI arrives — pivot circle (pivot_fill >= 0.82) or corn/alfalfa in
           >= 3 of 8 years (in Finney County nearly all corn and alfalfa is irrigated)
NDVI drop (%) = -(Jun–Aug mean in the year / Jun–Aug mean 2016–2019 - 1) * 100; positive = less green.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import geopandas as gpd  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import config as C  # noqa: E402
from common import rel, Skip, load_fields_draft, log, pivot_fill  # noqa: E402
from fetch import ssurgo  # noqa: E402
from process.rotation_class import classify  # noqa: E402

DIR = C.RAW / "neighbors"
POOL = DIR / "pool.geojson"
FEATURES = DIR / "pool_features.csv"
OUTPUTS = [FEATURES]
YEAR_COLS = [f"cdl_{y}" for y in C.CROP_YEARS]
SUMMER = (6, 7, 8)


# ---------------------------------------------------------------- select
def select(force: bool = False) -> gpd.GeoDataFrame:
    if POOL.exists() and not force:
        return gpd.read_file(POOL)
    p = C.RAW / "csb_finney.gpkg"
    if not p.exists():
        raise Skip("raw/csb_finney.gpkg missing")
    csb = gpd.read_file(p)
    demo = load_fields_draft().to_crs(C.CRS_UTM14)
    csb = csb[~csb.csb_id.isin(demo.csb_id.astype(str))]
    cen = csb.geometry.representative_point()
    dist = np.min([cen.distance(g.representative_point()) for g in demo.geometry], axis=0) / 1000
    csb = csb[(dist <= C.NEIGHBOR_RADIUS_KM) & csb.area_ha.between(C.NEIGHBOR_MIN_HA, C.NEIGHBOR_MAX_HA)].copy()
    crops = csb[YEAR_COLS].apply(lambda r: [C.cdl_to_crop(v) for v in r], axis=1)
    csb["known"] = crops.apply(lambda cs: sum(c != "other" for c in cs))
    csb = csb[csb.known >= C.NEIGHBOR_MIN_KNOWN_YEARS].copy()
    crops = crops.loc[csb.index]
    cls = crops.apply(classify)
    csb["rotation_class"] = cls.apply(lambda d: d["rotation_class"])
    csb["confidence"] = cls.apply(lambda d: d["confidence"])
    csb["crops"] = crops.apply(",".join)
    csb["pivot_fill"] = pivot_fill(csb.geometry)
    log("pool", f"{len(csb):,} eligible CSB fields within {C.NEIGHBOR_RADIUS_KM} km; "
                f"classes {csb.rotation_class.value_counts().to_dict()}")

    # stratified sample: equal quota per class, leftovers filled at random
    rng = np.random.default_rng(42)
    classes = sorted(csb.rotation_class.unique())
    quota = C.NEIGHBOR_POOL_MAX // len(classes)
    picked = []
    for c in classes:
        idx = csb.index[csb.rotation_class == c].to_numpy()
        picked += list(rng.choice(idx, size=min(quota, len(idx)), replace=False))
    rest = np.setdiff1d(csb.index.to_numpy(), picked)
    need = C.NEIGHBOR_POOL_MAX - len(picked)
    if need > 0 and len(rest):
        picked += list(rng.choice(rest, size=min(need, len(rest)), replace=False))
    pool = csb.loc[sorted(picked[:C.NEIGHBOR_POOL_MAX])].copy()
    wgs = pool.geometry.representative_point().to_crs(C.CRS_WGS84)
    pool["lon"], pool["lat"] = wgs.x.round(6), wgs.y.round(6)
    pool["nid"] = pool.csb_id.astype(str)
    pool = pool[["nid", "csb_id", "lon", "lat", "area_ha", "known", "rotation_class", "confidence",
                 "crops", "pivot_fill", *YEAR_COLS, "geometry"]].to_crs(C.CRS_WGS84)
    DIR.mkdir(parents=True, exist_ok=True)
    pool.to_file(POOL, driver="GeoJSON")
    log("pool", f"wrote {rel(POOL)}: {len(pool)} fields "
                f"{pool.rotation_class.value_counts().to_dict()}")
    return pool


# ---------------------------------------------------------------- NDVI sources
def _summer_ndvi_appeears() -> pd.DataFrame | None:
    """long table nid, date, ndvi (QA-ok only) from the AppEEARS neighbour task."""
    from process.harmonize import find_results

    hits = find_results(C.RAW / "appeears" / "neighbor_points", "MOD13Q1")
    if not hits:
        return None
    a = pd.read_csv(hits[0])
    v = next(c for c in a.columns if c.endswith("_250m_16_days_NDVI"))
    q = next(c for c in a.columns if c.endswith("_250m_16_days_pixel_reliability"))
    a = a[a[q].isin([0, 1])]
    nd = a[v].astype(float)
    nd = nd * 0.0001 if nd.abs().quantile(0.95) > 1.5 else nd
    return pd.DataFrame({"nid": a["ID"].astype(str), "date": pd.to_datetime(a["Date"]), "ndvi": nd})


def _summer_ndvi_ornl(pool: gpd.GeoDataFrame) -> pd.DataFrame | None:
    """Mean of the QA-ok MODIS pixels inside each pool polygon, from the ORNL area subset."""
    from fetch import modis_ornl as mo

    grid_p = mo.DIR / "area_grid.json"
    if not grid_p.exists():
        log("pool", "no ORNL area subset yet (run fetch/modis_ornl.py area)")
        return None
    grid = json.loads(grid_p.read_text())
    lon, lat = mo._pixel_centres(grid)
    px = gpd.GeoDataFrame({"pix": np.arange(lon.size)}, geometry=gpd.points_from_xy(lon, lat), crs=C.CRS_WGS84)
    j = gpd.sjoin(px, pool[["nid", "geometry"]], predicate="within")[["pix", "nid"]]
    # fields with no pixel centre inside: use the pixel nearest the centre
    missing = set(pool.nid) - set(j.nid)
    if missing:
        sub = pool[pool.nid.isin(missing)]
        near = gpd.sjoin_nearest(gpd.GeoDataFrame(sub[["nid"]], geometry=gpd.points_from_xy(sub.lon, sub.lat),
                                                  crs=C.CRS_WGS84).to_crs(C.CRS_UTM14),
                                 px.to_crs(C.CRS_UTM14))[["pix", "nid"]]
        j = pd.concat([j, near])
    rows = []
    for f in sorted((mo.DIR / "area").glob("ndvi_*.npy")):
        date = f.stem.split("_", 1)[1]
        nd = np.load(f).ravel().astype(float) * 0.0001
        rel = np.load(mo.DIR / "area" / f"rel_{date}.npy").ravel()
        ok = np.isin(rel, [0, 1]) & (nd > -0.2)
        jj = j[ok[j.pix.to_numpy()]]
        m = pd.Series(nd[jj.pix.to_numpy()]).groupby(jj.nid.to_numpy()).mean()
        rows += [(nid, date, v) for nid, v in m.items()]
    if not rows:
        return None
    return pd.DataFrame(rows, columns=["nid", "date", "ndvi"]).assign(date=lambda d: pd.to_datetime(d.date))


def ndvi_features(long: pd.DataFrame) -> pd.DataFrame:
    s = long[long.date.dt.month.isin(SUMMER)].copy()
    s["year"] = s.date.dt.year
    mean = s.groupby(["nid", "year"]).ndvi.mean().unstack()
    normal = mean[[y for y in C.NDVI_NORMAL_YEARS if y in mean.columns]].mean(axis=1)
    out = pd.DataFrame(index=mean.index)
    for y in (2012, 2022):
        out[f"ndvi_drop_{y}_pct"] = (-(mean[y] / normal - 1) * 100).round(1) if y in mean.columns else np.nan
    ja = s[s.date.dt.month.isin([7, 8]) & s.year.isin(C.CROP_YEARS)]
    peaks = ja.groupby(["nid", "year"]).ndvi.max().unstack()
    n = peaks.notna().sum(axis=1)
    out["ndvi_peak_years"] = n
    out["irr_ndvi"] = np.where(n >= 4, ((peaks >= C.IRRIGATED_NDVI_PEAK).sum(axis=1) >= n / 2), np.nan)
    return out


def _esi() -> pd.Series | None:
    from process.harmonize import find_results

    hits = find_results(C.RAW / "appeears" / "neighbor_esi", "ECO_L4T_ESI")
    if not hits:
        return None
    a = pd.read_csv(hits[0])
    v = next(c for c in a.columns if c.endswith("_ESI"))
    cl = next(c for c in a.columns if c.endswith("_cloud"))
    a = a[pd.to_numeric(a[cl], errors="coerce") == 0]
    return pd.to_numeric(a[v], errors="coerce").groupby(a["ID"].astype(str)).mean().round(2)


# ---------------------------------------------------------------- features
def features(force: bool = False) -> pd.DataFrame:
    pool = select()
    mk = ssurgo.mukeys_at_points([(r.nid, r.lon, r.lat) for r in pool.itertuples()])
    soils = {m: ssurgo.soil_for_mukey(m) for m in set(v for v in mk.values() if v)}
    rows = []
    for r in pool.itertuples():
        s = soils.get(mk.get(r.nid) or "", {})
        rows.append({"nid": r.nid, "mukey": s.get("mukey"), "awc_mm_per_m": s.get("awc_mm_per_m"),
                     "om_pct": s.get("om_pct"), "hydgrp": s.get("hydgrp"), "weg": s.get("weg"),
                     "wei_t_ac_yr": s.get("wei_t_ac_yr"), "slope_pct": s.get("slope_pct"),
                     "texture": s.get("texture")})
    f = pd.DataFrame(rows).set_index("nid")
    f = f.join(pool.set_index("nid")[["lon", "lat", "area_ha", "rotation_class", "confidence", "crops", "pivot_fill"]])

    long, src = _summer_ndvi_appeears(), "appeears"
    if long is None:
        long, src = _summer_ndvi_ornl(pool), "ornl"
    if long is not None:
        f = f.join(ndvi_features(long))
        log("pool", f"NDVI features from {src}: {int(f.ndvi_peak_years.fillna(0).gt(0).sum())} fields")
    else:
        for c in ("ndvi_drop_2012_pct", "ndvi_drop_2022_pct", "irr_ndvi"):
            f[c] = np.nan

    crops = f.crops.str.split(",")
    shape = (f.pivot_fill >= 0.82) | crops.apply(lambda cs: cs.count("corn") + cs.count("alfalfa") >= 3)
    f["irrigated"] = np.where(f.irr_ndvi.notna(), f.irr_ndvi.astype(float) > 0.5, shape)
    f["irr_method"] = np.where(f.irr_ndvi.notna(), "ndvi", "shape")
    agree = (f.irr_ndvi.notna()) & ((f.irr_ndvi.astype(float) > 0.5) == shape)
    if f.irr_ndvi.notna().any():
        log("pool", f"irrigated: NDVI vs shape/crop proxy agree on {agree.sum()}/{f.irr_ndvi.notna().sum()}")

    et_p = C.RAW / "openet" / "neighbors_annual.json"
    f["et_mm_yr"] = f.index.map(json.loads(et_p.read_text()).get) if et_p.exists() else np.nan
    esi = _esi()
    f["esi_summer_mean"] = f.index.map(esi.get) if esi is not None else np.nan
    f["irrigated"] = f.irrigated.astype(bool)
    f.to_csv(FEATURES)
    log("pool", f"wrote {rel(FEATURES)}: {len(f)} fields, "
                f"{int(f.irrigated.sum())} irrigated ({f.irr_method.value_counts().to_dict()})")
    return f


def main(force: bool = False) -> None:
    select(force)
    features(force)


if __name__ == "__main__":
    if "select" in sys.argv:
        select(force="--force" in sys.argv)
    elif "features" in sys.argv:
        features(force="--force" in sys.argv)
    else:
        main(force="--force" in sys.argv)
