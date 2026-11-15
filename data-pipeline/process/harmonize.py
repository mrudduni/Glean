"""Harmonize satellite point/pixel series to the field -> out/processed/{fid}/*.csv

  ndvi_modis.csv    date, ndvi, qa_ok        (AppEEARS 5-point mean, else ORNL in-field pixels)
  smap_l4_daily.csv date, sm_rootzone_m3m3, sm_surface_m3m3   (AppEEARS, 3-hourly -> daily mean)
  ecostress.csv     datetime, et_mm_day, esi (AppEEARS, cloud-free passes only)

The field is the analysis unit (README §4): MODIS is averaged over the pixels/points
inside the outline; SMAP (9 km) is the cell the field sits in. qa_ok = 1 when at least
half of the in-field samples have MODIS pixel reliability 0–1 (good / marginal); the
NDVI is then the mean of those good samples. No interpolation.

Finally checks every processed CSV against the README §8.2 column lists.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import config as C  # noqa: E402
from common import log, write_csv  # noqa: E402

APP = C.RAW / "appeears" / "demo_points"
ORNL = C.RAW / "modis_ornl"
SCHEMA = {
    "weather_daily.csv": ["date", "tmax_c", "tmin_c", "tmean_c", "rh_pct", "ws2m_ms", "ws10m_ms",
                          "ws10m_max_ms", "rs_mj_m2", "precip_mm"],
    "precip_imerg_daily.csv": ["date", "precip_mm"],
    "prism_daily.csv": ["date", "tmin_c", "tmax_c", "precip_mm"],
    "ndvi_modis.csv": ["date", "ndvi", "qa_ok"],
    "smap_l4_daily.csv": ["date", "sm_rootzone_m3m3", "sm_surface_m3m3"],
    "openet_monthly.csv": ["month", "et_mm"],
    "ecostress.csv": ["datetime", "et_mm_day", "esi"],
    "grace_monthly.csv": ["month", "tws_anom_cm"],
}
OUTPUTS = [C.PROCESSED / fid / "ndvi_modis.csv" for fid in C.FIELD_IDS]


def _norm(x: str) -> str:
    return re.sub(r"[-_.]", "", x).lower()


def find_results(folder: Path, prefix: str) -> list[Path]:
    """AppEEARS names files like <task>-ECO-L3T-JET-002-results.csv: match ignoring -_. separators."""
    if not folder.exists():
        return []
    return sorted(p for p in folder.glob("*results.csv") if _norm(prefix) in _norm(p.name))


def _app_csv(prefix: str) -> pd.DataFrame | None:
    hits = find_results(APP, prefix)
    return pd.read_csv(hits[0]) if hits else None


def _col(df: pd.DataFrame, suffix: str) -> str:
    return next(c for c in df.columns if c.endswith(suffix))


def _ndvi_scale(s: pd.Series) -> pd.Series:
    return s * 0.0001 if s.abs().quantile(0.95) > 1.5 else s


def _reduce(df: pd.DataFrame, key: str) -> pd.DataFrame:
    """df has date, ndvi, rel per sample -> one row per date."""
    df = df[(df.ndvi > -0.2) & (df.ndvi <= 1.0)]
    g = df.assign(good=df.rel.isin([0, 1])).groupby("date")
    out = pd.DataFrame({
        "n": g.size(), "n_good": g.good.sum(),
        "mean_good": g.apply(lambda x: x.loc[x.good, "ndvi"].mean(), include_groups=False),
        "mean_all": g.ndvi.mean(),
    })
    out["qa_ok"] = (out.n_good >= np.ceil(out.n / 2)).astype(int)
    out["ndvi"] = np.where(out.qa_ok == 1, out.mean_good, out.mean_all).round(3)
    log("harmonize", f"{key}: {len(out)} composites, {out.qa_ok.mean():.0%} qa_ok")
    return out.reset_index()[["date", "ndvi", "qa_ok"]]


def ndvi() -> str | None:
    app = _app_csv("MOD13Q1")
    for fid in C.FIELD_IDS:
        dest = C.PROCESSED / fid / "ndvi_modis.csv"
        if app is not None:
            d = app[app["Category"].astype(str) == fid]
            df = pd.DataFrame({"date": pd.to_datetime(d["Date"]).dt.strftime("%Y-%m-%d"),
                               "ndvi": _ndvi_scale(d[_col(d, "_250m_16_days_NDVI")].astype(float)),
                               "rel": d[_col(d, "_250m_16_days_pixel_reliability")]})
            src = "AppEEARS"
        elif (ORNL / f"{fid}_pixels.csv").exists():
            p = pd.read_csv(ORNL / f"{fid}_pixels.csv")
            p = p[p.inside] if p.inside.any() else p
            p = p[p.ndvi_raw > -3000]
            df = pd.DataFrame({"date": p.date, "ndvi": _ndvi_scale(p.ndvi_raw.astype(float)), "rel": p.reliability})
            src = "ORNL"
        else:
            log("harmonize", f"{fid}: no MODIS input yet")
            continue
        out = _reduce(df, f"{fid} ({src})")
        out = out[(out.date >= C.MODIS_START) & (out.date <= C.MODIS_END)]
        write_csv(dest, out, SCHEMA["ndvi_modis.csv"])
    return None


def smap() -> None:
    app = _app_csv("SPL4SMGP")
    if app is None:
        log("harmonize", "SMAP: no AppEEARS output yet")
        return
    rz, sf = _col(app, "sm_rootzone"), _col(app, "sm_surface")
    for fid in C.FIELD_IDS:
        d = app[app["Category"].astype(str) == fid].copy()
        d["date"] = pd.to_datetime(d["Date"]).dt.strftime("%Y-%m-%d")
        for c in (rz, sf):
            d[c] = pd.to_numeric(d[c], errors="coerce").mask(lambda s: (s < 0) | (s > 1))
        g = d.groupby("date")[[rz, sf]].mean().round(4).reset_index()
        g = g.rename(columns={rz: "sm_rootzone_m3m3", sf: "sm_surface_m3m3"})
        g = g[(g.date >= C.SMAP_START) & (g.date <= C.SMAP_END)]
        write_csv(C.PROCESSED / fid / "smap_l4_daily.csv", g, SCHEMA["smap_l4_daily.csv"])
        log("harmonize", f"{fid}: SMAP {len(g)} days, root-zone {g.sm_rootzone_m3m3.min():.2f}–"
                         f"{g.sm_rootzone_m3m3.max():.2f} m3/m3")


def _eco(prefix: str, layer: str) -> pd.DataFrame | None:
    a = _app_csv(prefix)
    if a is None:
        return None
    v, cl = _col(a, f"_{layer}"), _col(a, "_cloud")
    a = a[pd.to_numeric(a[cl], errors="coerce") == 0]
    t = a["Date"].astype(str)
    if "Time" in a.columns:
        t = t + "T" + a["Time"].astype(str)
    return pd.DataFrame({"fid": a["Category"].astype(str), "datetime": pd.to_datetime(t, utc=True),
                         layer: pd.to_numeric(a[v], errors="coerce")})


def ecostress() -> None:
    et, esi = _eco("ECO_L3T_JET", "ETdaily"), _eco("ECO_L4T_ESI", "ESI")
    if et is None and esi is None:
        log("harmonize", "ECOSTRESS: no AppEEARS output yet")
        return
    if et is not None:
        # AppEEARS reports ETdaily in W/m2 (daily mean latent heat) -> mm/day (/28.36)
        if et["ETdaily"].median() > 20:
            et["ETdaily"] = et["ETdaily"] / 28.36
    frames = [f for f in (et, esi) if f is not None]
    for fid in C.FIELD_IDS:
        parts = [f[f.fid == fid].assign(datetime=lambda d: d.datetime.dt.floor("min"))
                 .groupby("datetime").mean(numeric_only=True) for f in frames]
        df = pd.concat(parts, axis=1).reset_index().sort_values("datetime")
        out = pd.DataFrame({"datetime": df.datetime.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "et_mm_day": df.get("ETdaily", pd.Series(np.nan, index=df.index)).round(2),
                            "esi": df.get("ESI", pd.Series(np.nan, index=df.index)).round(2)})
        out = out[out.et_mm_day.notna() | out.esi.notna()]
        write_csv(C.PROCESSED / fid / "ecostress.csv", out, SCHEMA["ecostress.csv"])
        log("harmonize", f"{fid}: ECOSTRESS {len(out)} cloud-free passes")


def check() -> list[str]:
    problems = []
    for fid in C.FIELD_IDS:
        for name, cols in SCHEMA.items():
            p = C.PROCESSED / fid / name
            if not p.exists():
                problems.append(f"{fid}/{name}: missing")
                continue
            head = pd.read_csv(p, nrows=0).columns.tolist()
            if head != cols:
                problems.append(f"{fid}/{name}: columns {head} != {cols}")
    return problems


def main(force: bool = False) -> None:
    ndvi()
    smap()
    ecostress()
    for p in check():
        log("harmonize", f"  {p}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
