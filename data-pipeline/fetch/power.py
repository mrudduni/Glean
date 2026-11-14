"""NASA POWER daily point data (AG community) -> out/processed/{fid}/weather_daily.csv

Columns (README §8.2): date, tmax_c, tmin_c, tmean_c, rh_pct, ws2m_ms, ws10m_ms,
ws10m_max_ms, rs_mj_m2, precip_mm. Fill value -999 -> empty. Single missing
days are linearly filled (the only interpolation the contract allows).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

import config as C  # noqa: E402
from common import cached_json, get_json, load_fields_draft, log, write_csv  # noqa: E402

URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS = ["T2M_MAX", "T2M_MIN", "T2M", "RH2M", "WS2M", "WS10M", "WS10M_MAX",
          "ALLSKY_SFC_SW_DWN", "PRECTOTCORR"]
RENAME = {"T2M_MAX": "tmax_c", "T2M_MIN": "tmin_c", "T2M": "tmean_c", "RH2M": "rh_pct",
          "WS2M": "ws2m_ms", "WS10M": "ws10m_ms", "WS10M_MAX": "ws10m_max_ms",
          "ALLSKY_SFC_SW_DWN": "rs_mj_m2", "PRECTOTCORR": "precip_mm"}
COLUMNS = ["date", *RENAME.values()]
OUTPUTS = [C.PROCESSED / fid / "weather_daily.csv" for fid in C.FIELD_IDS]


def _fetch(lon: float, lat: float, start: str, end: str) -> dict:
    return get_json(URL, params={
        "parameters": ",".join(PARAMS), "community": "AG", "longitude": f"{lon:.4f}",
        "latitude": f"{lat:.4f}", "start": start, "end": end, "format": "JSON",
    }, timeout=300, service="power")


def fetch_point(fid: str, lon: float, lat: float) -> tuple[pd.DataFrame, dict]:
    raw = C.RAW / "power"
    try:
        data = cached_json(raw / f"{fid}_{C.POWER_START}_{C.POWER_END}.json",
                           lambda: _fetch(lon, lat, C.POWER_START, C.POWER_END))
        parts = [data]
    except Exception as e:  # full range refused -> split by decade
        log("power", f"{fid}: full range failed ({e}); splitting by decade")
        parts = []
        for y0 in range(int(C.POWER_START[:4]), int(C.POWER_END[:4]) + 1, 10):
            y1 = min(y0 + 9, int(C.POWER_END[:4]))
            s, t = f"{y0}0101", f"{y1}1231"
            parts.append(cached_json(raw / f"{fid}_{s}_{t}.json", lambda s=s, t=t: _fetch(lon, lat, s, t)))
    frames, units = [], {}
    for d in parts:
        p = d["properties"]["parameter"]
        units.update({k: v.get("units") for k, v in d.get("parameters", {}).items()})
        frames.append(pd.DataFrame(p))
    df = pd.concat(frames)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df = df[~df.index.duplicated()].sort_index()
    return df, units


def to_weather(df: pd.DataFrame, units: dict) -> pd.DataFrame:
    df = df.mask(df <= -998)  # -999 fill
    rs_units = (units.get("ALLSKY_SFC_SW_DWN") or "").lower().replace(" ", "")
    if "kw" in rs_units:  # kWh/m^2/day -> MJ/m^2/day
        df["ALLSKY_SFC_SW_DWN"] = df["ALLSKY_SFC_SW_DWN"] * 3.6
    elif "w/m" in rs_units and "mj" not in rs_units:  # mean W/m^2 -> MJ/m^2/day
        df["ALLSKY_SFC_SW_DWN"] = df["ALLSKY_SFC_SW_DWN"] * 0.0864
    full = pd.date_range(df.index.min(), pd.Timestamp(C.POWER_END), freq="D")
    df = df.reindex(full)
    df = df.interpolate(limit=1, limit_area="inside")  # single missing days only
    out = df.rename(columns=RENAME)
    out.insert(0, "date", out.index.strftime("%Y-%m-%d"))
    for c in RENAME.values():
        out[c] = out[c].round(2)
    return out


def main(force: bool = False) -> None:
    gdf = load_fields_draft()
    for fid, geom in gdf.geometry.items():
        dest = C.PROCESSED / fid / "weather_daily.csv"
        if dest.exists() and not force:
            log("power", f"exists: {fid}/weather_daily.csv")
            continue
        c = geom.representative_point()
        df, units = fetch_point(fid, c.x, c.y)
        log("power", f"{fid}: units {units}")
        w = to_weather(df, units)
        write_csv(dest, w, COLUMNS)
        yr = w.assign(y=w.date.str[:4]).groupby("y")
        p = yr.precip_mm.sum(min_count=300)
        rs = w.rs_mj_m2.dropna()
        log("power", f"{fid}: {len(w)} days {w.date.iloc[0]}..{w.date.iloc[-1]} | "
                     f"precip median {p.median():.0f} mm/yr | rs median {rs.median():.1f} MJ/m2/d | "
                     f"days Tmax>32C/yr {(w.tmax_c > 32).sum() / p.size:.0f}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
