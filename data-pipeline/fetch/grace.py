"""JPL GRACE/GRACE-FO RL06.3 mascon (CRI filtered) -> out/processed/{fid}/grace_monthly.csv

Downloads the single global netCDF from PO.DAAC with earthaccess (Earthdata login),
takes the 0.5° grid cell containing each field and writes lwe_thickness (cm) per month.
True resolution is ~300 km: this is a regional aquifer/storage signal, not a field value.
The 2017-07 -> 2018-05 inter-mission gap has no data; nothing is interpolated.

Also writes raw/grace/grace_fields.json with cell centre + OLS trend (cm/yr) for build_water.
Columns: month, tws_anom_cm
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import config as C  # noqa: E402
from common import Skip, load_fields_draft, log, ols_slope, spend, write_csv  # noqa: E402

DIR = C.RAW / "grace"
SHORT_NAMES = ["TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4", "TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.1_V3"]
COLUMNS = ["month", "tws_anom_cm"]
OUTPUTS = [C.PROCESSED / fid / "grace_monthly.csv" for fid in C.FIELD_IDS]
INFO = DIR / "grace_fields.json"


def _netcdf() -> Path:
    hits = sorted(DIR.glob("*MSCN*CRI*.nc"))
    if hits:
        return hits[-1]
    if not C.has_earthdata():
        raise Skip("Earthdata login needed for GRACE (PO.DAAC)")
    import earthaccess

    earthaccess.login(strategy="environment" if C.EARTHDATA_USERNAME else "netrc")
    for sn in SHORT_NAMES:
        spend("earthdata")
        res = earthaccess.search_data(short_name=sn)
        if res:
            DIR.mkdir(parents=True, exist_ok=True)
            spend("earthdata")
            files = earthaccess.download(res[-1:], str(DIR))
            return Path(files[0])
    raise RuntimeError("GRACE mascon collection not found in CMR")


def main(force: bool = False) -> None:
    if all(p.exists() for p in OUTPUTS) and INFO.exists() and not force:
        log("grace", "exists: grace_monthly.csv for all fields")
        return
    import xarray as xr

    nc = _netcdf()
    ds = xr.open_dataset(nc)
    lwe = ds["lwe_thickness"]
    gdf = load_fields_draft()
    info = {}
    for fid, geom in gdf.geometry.items():
        c = geom.representative_point()
        lon360 = c.x % 360
        cell = lwe.sel(lat=c.y, lon=lon360, method="nearest")
        months = pd.to_datetime(cell["time"].values).strftime("%Y-%m")
        df = pd.DataFrame({"month": months, "tws_anom_cm": np.round(cell.values.astype(float), 2)})
        df = df.dropna().drop_duplicates("month").sort_values("month")
        gap = (df.month >= C.GRACE_GAP[0]) & (df.month <= C.GRACE_GAP[1])
        df = df[~gap]
        write_csv(C.PROCESSED / fid / "grace_monthly.csv", df, COLUMNS)
        t = pd.to_datetime(df.month + "-15")
        slope = ols_slope(t.dt.year + (t.dt.dayofyear - 1) / 365.25, df.tws_anom_cm)
        clon = float(cell["lon"].values)
        info[fid] = {"cell_center": [round(clon - 360 if clon > 180 else clon, 3), round(float(cell["lat"].values), 3)],
                     "trend_cm_per_yr": round(slope, 2) if slope is not None else None,
                     "period": [df.month.iloc[0], df.month.iloc[-1]]}
        log("grace", f"{fid}: {len(df)} months, trend {slope:+.2f} cm/yr, cell {info[fid]['cell_center']}")
    INFO.write_text(json.dumps(info, indent=1))


if __name__ == "__main__":
    main(force="--force" in sys.argv)
