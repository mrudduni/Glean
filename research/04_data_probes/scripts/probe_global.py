"""Live probe of global (non-US) data sources for Field Shift.

Run:  python probe_global.py            (all probes)
      python probe_global.py soilgrids_wcs chirps   (selected probes)

No secrets and no accounts. Every source here is open without a key.
Point values come from small HTTP requests or windowed COG reads with
rasterio, never full-file downloads. The FAOSTAT bulk zips (1.5 MB and
2.6 MB) are cached outside the repo in FIELDSHIFT_CACHE
(default: ~/.cache/fieldshift).

Results go to ../samples/global_probe_results.json, plus small per-source
samples. Each probe records the exact URL, HTTP status, timing, and errors.
"""

from __future__ import annotations

import io
import json
import os
import sys
import time
import zipfile
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
SAMPLES = HERE.parent / "samples"
CACHE = Path(os.environ.get("FIELDSHIFT_CACHE", Path.home() / ".cache" / "fieldshift"))
UA = {"User-Agent": "field-shift-probe/0.1 (research script)"}

# Test points (lat, lon). The brief's Ludhiana, Karnal, Nashik and Eldoret
# points fall on built-up land, which SoilGrids and WorldCereal mask, so each has a nearby
# cropland twin found by scanning WorldCereal temporary-crop pixels.
POINTS = {
    "ludhiana": (30.90, 75.85),        # brief point, Ludhiana city
    "ludhiana_crop": (30.90, 75.77),   # 7.6 km west, WorldCereal cropland
    "karnal": (29.69, 76.98),          # brief point, Karnal city
    "karnal_crop": (29.69, 76.90),     # 7.7 km west, WorldCereal cropland
    "nashik": (20.00, 73.80),          # brief point, Nashik city
    "nashik_crop": (20.05, 73.75),     # 7.6 km north-west, WorldCereal cropland
    "eldoret": (0.52, 35.27),          # brief point, Eldoret town
    "eldoret_crop": (0.55, 35.35),     # 9.5 km east, WorldCereal cropland
    "iowa": (42.03, -93.75),
}

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif,.cog,.tiff")
os.environ.setdefault("GDAL_HTTP_MAX_RETRY", "3")
os.environ.setdefault("GDAL_HTTP_RETRY_DELAY", "2")


def timed_get(url, params=None, timeout=90, **kw):
    """GET with timing. Returns (response or None, record dict)."""
    t = time.time()
    rec = {"url": url, "params": params}
    try:
        r = requests.get(url, params=params, timeout=timeout, headers=UA, **kw)
        rec.update(status=r.status_code, seconds=round(time.time() - t, 1), final_url=r.url)
        return r, rec
    except Exception as e:  # record the failure, keep going
        rec.update(status=None, seconds=round(time.time() - t, 1), error=f"{type(e).__name__}: {e}")
        return None, rec


# --------------------------------------------------------------------------
# 1. SoilGrids 2.0
# --------------------------------------------------------------------------
SG_PROPS = ["clay", "sand", "silt", "soc", "phh2o", "bdod", "cec", "nitrogen", "wv0033", "wv1500"]
SG_DEPTHS = ["0-5cm", "15-30cm", "30-60cm"]
SG_VALUES = ["mean", "Q0.05", "Q0.95"]
# d_factor from the REST response: stored integer / d_factor = target unit.
SG_DFACTOR = {"clay": 10, "sand": 10, "silt": 10, "soc": 10, "phh2o": 10, "bdod": 100,
              "cec": 10, "nitrogen": 100, "wv0033": 10, "wv1500": 10}
SG_TARGET_UNIT = {"clay": "%", "sand": "%", "silt": "%", "soc": "g/kg", "phh2o": "pH",
                  "bdod": "kg/dm3", "cec": "cmol(c)/kg", "nitrogen": "g/kg",
                  "wv0033": "10^-2 cm3/cm3 (vol %)", "wv1500": "10^-2 cm3/cm3 (vol %)"}


def soilgrids_rest(lat, lon, props=("clay", "sand", "soc", "phh2o"), timeout=240):
    """The REST point API. ISRIC labels it beta and it is often slow."""
    params = [("lon", lon), ("lat", lat)]
    params += [("property", p) for p in props]
    params += [("depth", d) for d in SG_DEPTHS]
    params += [("value", v) for v in SG_VALUES]
    r, rec = timed_get("https://rest.isric.org/soilgrids/v2.0/properties/query", params, timeout=timeout)
    if r is not None and r.ok:
        layers = r.json()["properties"]["layers"]
        rec["values"] = {
            L["name"]: {d["label"]: d["values"] for d in L["depths"]} for L in layers
        }
        rec["units"] = {L["name"]: L["unit_measure"] for L in layers}
    elif r is not None:
        rec["body"] = r.text[:300]
    return rec


def soilgrids_wcs(lat, lon, prop, depth, value="mean", half=0.01):
    """Read one SoilGrids layer from ISRIC's WCS as a tiny GeoTIFF window.

    Returns the pixel at the point, and if that is masked (0, which ISRIC
    uses for built-up land and water), the nearest valid pixel in the window.
    """
    import numpy as np
    import rasterio
    from rasterio.io import MemoryFile

    url = "https://maps.isric.org/mapserv"
    params = [
        ("map", f"/map/{prop}.map"), ("SERVICE", "WCS"), ("VERSION", "2.0.1"),
        ("REQUEST", "GetCoverage"), ("COVERAGEID", f"{prop}_{depth}_{value}"),
        ("FORMAT", "GEOTIFF_INT16"),
        ("SUBSET", f"long({lon - half},{lon + half})"), ("SUBSET", f"lat({lat - half},{lat + half})"),
        ("SUBSETTINGCRS", "http://www.opengis.net/def/crs/EPSG/0/4326"),
        ("OUTPUTCRS", "http://www.opengis.net/def/crs/EPSG/0/4326"),
    ]
    r, rec = timed_get(url, params, timeout=90)
    if r is None or not r.ok or not r.headers.get("content-type", "").startswith("image/tiff"):
        rec["body"] = None if r is None else r.text[:300]
        return rec
    with MemoryFile(r.content) as mf, mf.open() as d:
        a = d.read(1).astype(float)
        row, col = d.index(lon, lat)
        raw = a[row, col]
        rec["raw_at_point"] = raw
        if raw == 0:
            rr, cc = np.nonzero(a > 0)
            if rr.size:
                dist = np.hypot(rr - row, cc - col)
                k = int(dist.argmin())
                x, y = d.xy(rr[k], cc[k])
                rec["nearest_valid"] = {"raw": a[rr[k], cc[k]], "lon": round(x, 5), "lat": round(y, 5),
                                        "km": round(float(dist[k]) * 0.25, 2)}
                raw = a[rr[k], cc[k]]
            else:
                raw = None
        rec["value"] = None if raw is None else raw / SG_DFACTOR[prop]
        rec["unit"] = SG_TARGET_UNIT[prop]
        rec["pixel_deg"] = d.res
    return rec


def probe_soilgrids_wcs():
    """Mean at three depths for every property; Q0.05 and Q0.95 at 0-5 cm and 30-60 cm."""
    from concurrent.futures import ThreadPoolExecutor

    jobs = []
    for name in ["ludhiana", "ludhiana_crop", "karnal_crop", "nashik", "nashik_crop",
                 "eldoret", "eldoret_crop", "iowa"]:
        for prop in SG_PROPS:
            for depth in SG_DEPTHS:
                for value in SG_VALUES:
                    if value != "mean" and depth == "15-30cm":
                        continue
                    jobs.append((name, prop, depth, value))

    def run(job):
        name, prop, depth, value = job
        lat, lon = POINTS[name]
        return job, soilgrids_wcs(lat, lon, prop, depth, value)

    out = {}
    with ThreadPoolExecutor(max_workers=4) as pool:  # keep the load on ISRIC modest
        for (name, prop, depth, value), rec in pool.map(run, jobs):
            o = out.setdefault(name, {})
            o[f"{prop}_{depth}_{value}"] = rec.get("value", rec.get("error") or rec.get("body"))
            if "nearest_valid" in rec:
                o["_masked_at_point"] = True
                o["_nearest_valid"] = rec["nearest_valid"]
            o.setdefault("_example_request", rec.get("final_url", rec["url"]))
    for name, o in out.items():
        print("soilgrids_wcs", name, {k: v for k, v in o.items() if k.endswith("0-5cm_mean")})
    return out


def probe_soilgrids_rest():
    out = {}
    for name in ["ludhiana_crop", "karnal_crop", "nashik_crop", "eldoret_crop", "iowa"]:
        lat, lon = POINTS[name]
        out[name] = soilgrids_rest(lat, lon)
        print("soilgrids_rest", name, out[name].get("status"), out[name].get("seconds"), out[name].get("error", ""))
        time.sleep(12)  # ISRIC asks for at most 5 calls per minute
    return out


# --------------------------------------------------------------------------
# 2. Open-Meteo historical (ERA5 / ERA5-Land), no key
# --------------------------------------------------------------------------
def probe_open_meteo():
    out = {}
    daily = "temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration,shortwave_radiation_sum"
    for name in ["ludhiana_crop", "karnal_crop", "nashik_crop", "eldoret_crop", "iowa"]:
        lat, lon = POINTS[name]
        params = {"latitude": lat, "longitude": lon, "start_date": "2024-01-01", "end_date": "2024-12-31",
                  "daily": daily, "hourly": "soil_moisture_0_to_7cm,soil_moisture_28_to_100cm",
                  "timezone": "auto"}
        r, rec = timed_get("https://archive-api.open-meteo.com/v1/archive", params)
        if r is not None and r.ok:
            j = r.json()
            d = j["daily"]
            sm = [v for v in j["hourly"]["soil_moisture_0_to_7cm"] if v is not None]
            rec.update(
                grid_lat=j["latitude"], grid_lon=j["longitude"], elevation=j["elevation"],
                annual_precip_mm=round(sum(v for v in d["precipitation_sum"] if v is not None), 1),
                annual_et0_mm=round(sum(v for v in d["et0_fao_evapotranspiration"] if v is not None), 1),
                tmax_max=max(v for v in d["temperature_2m_max"] if v is not None),
                tmin_min=min(v for v in d["temperature_2m_min"] if v is not None),
                sm_0_7_mean=round(sum(sm) / len(sm), 3),
                ratelimit_headers={k: v for k, v in r.headers.items() if "limit" in k.lower()},
            )
            if name == "ludhiana_crop":
                small = {"latitude": j["latitude"], "longitude": j["longitude"], "daily_units": j["daily_units"],
                         "daily": {k: v[150:160] for k, v in d.items()}}
                (SAMPLES / "open_meteo_ludhiana_2024-05-31_10days.json").write_text(json.dumps(small, indent=1))
        out[name] = rec
        print("open_meteo", name, {k: rec.get(k) for k in ("status", "annual_precip_mm", "annual_et0_mm", "sm_0_7_mean")})
    return out


# --------------------------------------------------------------------------
# 3. CHIRPS v2 and v3 monthly COGs, windowed reads
# --------------------------------------------------------------------------
CHIRPS = {
    "v3": "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/cogs/chirps-v3.0.{y}.{m:02d}.cog",
    "v2": "https://data.chc.ucsb.edu/products/CHIRPS/v2.0/global_monthly/cogs/chirps-v2.0.{y}.{m:02d}.cog",
}


def probe_chirps(year=2024, months=(6, 7, 8, 9)):
    import rasterio
    names = ["ludhiana_crop", "karnal_crop", "nashik_crop", "eldoret_crop", "iowa"]
    xy = [(POINTS[n][1], POINTS[n][0]) for n in names]
    out = {}
    for ver, tmpl in CHIRPS.items():
        out[ver] = {"months": {}}
        for m in months:
            url = tmpl.format(y=year, m=m)
            t = time.time()
            try:
                with rasterio.open("/vsicurl/" + url) as d:
                    vals = [round(float(v[0]), 1) for v in d.sample(xy)]
                    out[ver]["profile"] = {"crs": str(d.crs), "res": d.res, "shape": d.shape,
                                           "nodata": d.nodata, "bounds": tuple(d.bounds)}
                out[ver]["months"][f"{year}-{m:02d}"] = dict(zip(names, vals))
                out[ver]["months"][f"{year}-{m:02d}"]["_seconds"] = round(time.time() - t, 1)
            except Exception as e:
                out[ver]["months"][f"{year}-{m:02d}"] = {"error": f"{type(e).__name__}: {e}", "url": url}
            print("chirps", ver, year, m, out[ver]["months"][f"{year}-{m:02d}"])
        out[ver]["url_template"] = tmpl
    return out


# --------------------------------------------------------------------------
# 4. ESA WorldCereal 2021 through the Terrascope STAC and TiTiler point API
# --------------------------------------------------------------------------
WC_COLLECTIONS = ["temporarycrops", "wintercereals", "maize", "springcereals", "irrigation", "activecropland"]


def worldcereal_point(lat, lon):
    res = {}
    for prod in WC_COLLECTIONS:
        coll = f"esa-worldcereal-{prod}-10m-2021-v1"
        r, rec = timed_get("https://stac.terrascope.be/search",
                           {"collections": coll, "limit": 10,
                            "intersects": json.dumps({"type": "Point", "coordinates": [lon, lat]})})
        if r is None or not r.ok:
            res[prod] = rec
            continue
        items = [f["id"] for f in r.json().get("features", [])]
        res[prod] = {"items": items, "values": {}}
        for it in items:
            pr, prec = timed_get(
                f"https://titiler.terrascope.be/collections/{coll}/items/{it}/point/{lon},{lat}",
                {"assets": ["classification", "confidence"]})
            if pr is not None and pr.ok:
                res[prod]["values"][it] = pr.json()["values"]  # [class (0 or 100), confidence 0-100]
            else:
                res[prod]["values"][it] = prec
    return res


def probe_worldcereal():
    out = {}
    for name in list(POINTS):
        out[name] = worldcereal_point(*POINTS[name])
        print("worldcereal", name, {p: v.get("values") for p, v in out[name].items()})
    # Downloading the GeoTIFF itself needs a Terrascope login:
    _, rec = timed_get("https://services.terrascope.be/download/WORLDCEREAL/ESA_WORLDCEREAL_TEMPORARYCROPS_V1/"
                       "aez/2021/tc-annual/34119_tc-annual_temporarycrops_2021/"
                       "34119_tc-annual_temporarycrops_2020-10-22_2021-10-22_classification.tif",
                       stream=True)
    out["_direct_download_check"] = rec
    return out


# --------------------------------------------------------------------------
# 5. FAOSTAT producer prices: the API needs a token, the bulk zips do not
# --------------------------------------------------------------------------
def probe_faostat():
    out = {}
    r, rec = timed_get("https://faostatservices.fao.org/api/v1/en/data/PP",
                       {"area": "100", "item": "27", "element": "5532", "year": "2022"})
    rec["body"] = None if r is None else r.text[:200]
    out["api_no_token"] = rec
    CACHE.mkdir(parents=True, exist_ok=True)
    wanted = {"India": ["Rice", "Wheat", "Maize (corn)", "Rape or colza seed", "Mustard seed", "Chick peas, dry",
                        "Soya beans", "Sugar cane"],
              "Kenya": ["Maize (corn)", "Wheat", "Beans, dry", "Potatoes"]}
    for region, country in [("Asia", "India"), ("Africa", "Kenya")]:
        url = f"https://bulks-faostat.fao.org/production/Prices_E_{region}.zip"
        f = CACHE / f"Prices_E_{region}.zip"
        t = time.time()
        if not f.exists():
            r = requests.get(url, timeout=180, headers=UA)
            r.raise_for_status()
            f.write_bytes(r.content)
        rec = {"url": url, "bytes": f.stat().st_size, "seconds": round(time.time() - t, 1)}
        import pandas as pd
        with zipfile.ZipFile(f) as z:
            name = [n for n in z.namelist() if n.endswith(".csv") and "Flag" not in n and "Item" not in n
                    and "Area" not in n and "Element" not in n][0]
            df = pd.read_csv(z.open(name), encoding="latin-1")
        rec["csv"] = name
        rec["columns"] = list(df.columns)[:12]
        sel = df[(df["Area"] == country) & (df["Item"].isin(wanted[country]))
                 & (df["Element"].str.contains("Producer Price \\(LCU/tonne\\)|Producer Price \\(USD/tonne\\)",
                                               regex=True))]
        ycols = sorted([c for c in df.columns if c.startswith("Y") and c[1:].isdigit()])[-4:]
        if ycols:  # wide layout
            table = sel[["Item", "Element", "Unit"] + ycols]
        else:
            table = sel
        rec["latest_years"] = ycols
        rec["rows"] = table.fillna("").astype(str).values.tolist()
        out[country] = rec
        (SAMPLES / f"faostat_producer_prices_{country.lower()}.csv").write_text(table.to_csv(index=False))
        print("faostat", country, rec["bytes"], ycols, len(rec["rows"]))
    return out


# --------------------------------------------------------------------------
# 6. FAO WaPOR v3 COGs (public Google Cloud bucket)
# --------------------------------------------------------------------------
def probe_wapor():
    import rasterio
    names = ["ludhiana_crop", "karnal_crop", "nashik_crop", "eldoret_crop", "iowa"]
    xy = [(POINTS[n][1], POINTS[n][0]) for n in names]
    out = {}
    r, rec = timed_get("https://data.apps.fao.org/gismgr/api/v2/catalog/workspaces/WAPOR-3/mapsets")
    out["catalog"] = rec
    for code, scale, unit in [("L1-AETI-A/WAPOR-3.L1-AETI-A.2024", 0.1, "mm/year"),
                              ("L1-RSM-D/WAPOR-3.L1-RSM-D.2024-08-D1", 0.001, "fraction")]:
        url = f"https://storage.googleapis.com/fao-gismgr-wapor-3-data/DATA/WAPOR-3/MAPSET/{code}.tif"
        t = time.time()
        try:
            with rasterio.open("/vsicurl/" + url) as d:
                vals = [None if v[0] == d.nodata else round(float(v[0]) * scale, 3) for v in d.sample(xy)]
                out[code] = {"url": url, "unit": unit, "res_deg": d.res, "values": dict(zip(names, vals)),
                             "seconds": round(time.time() - t, 1)}
        except Exception as e:
            out[code] = {"url": url, "error": f"{type(e).__name__}: {e}"}
        print("wapor", code, out[code].get("values", out[code].get("error")))
    return out


# --------------------------------------------------------------------------
# 7. FAO crop calendar API (GIEWS / AGP)
# --------------------------------------------------------------------------
def probe_crop_calendar():
    out = {}
    r, rec = timed_get("https://api-cropcalendar.apps.fao.org/api/v1/countries", {"language": "en"})
    if r is not None and r.ok:
        rec["countries"] = [c["id"] for c in r.json()]
    out["countries"] = rec
    for iso in ["IN", "KE"]:
        r, rec = timed_get(f"https://api-cropcalendar.apps.fao.org/api/v1/countries/{iso}/cropCalendar",
                           {"language": "en"})
        if r is not None and r.status_code == 200 and r.text:
            j = r.json()
            rec["n_entries"] = len(j)
            rec["crops"] = sorted({x["crop"]["name"] for x in j})
            if iso == "KE":
                (SAMPLES / "fao_crop_calendar_kenya_first3.json").write_text(json.dumps(j[:3], indent=1))
        else:
            rec["body_len"] = None if r is None else len(r.text)
        out[iso] = rec
        print("crop_calendar", iso, rec.get("status"), rec.get("n_entries"))
    return out


# --------------------------------------------------------------------------
# 8. WFP market prices on HDX (CKAN API, no key)
# --------------------------------------------------------------------------
def probe_wfp_hdx():
    out = {}
    for c in ["india", "kenya"]:
        r, rec = timed_get("https://data.humdata.org/api/3/action/package_show", {"id": f"wfp-food-prices-for-{c}"})
        if r is not None and r.ok:
            j = r.json()["result"]
            rec.update(license=j.get("license_title"), last_modified=j.get("last_modified"),
                       resources=[(x["name"], x["url"], x.get("size")) for x in j["resources"]])
            price = [x for x in j["resources"] if x["name"].endswith("Food Prices")][0]
            # Stream the first ~300 KB only; the India file is about 26 MB.
            with requests.get(price["url"], stream=True, timeout=120, headers=UA) as pr:
                buf = b""
                for chunk in pr.iter_content(65536):
                    buf += chunk
                    if len(buf) > 300_000:
                        break
            lines = buf.decode("utf-8", "replace").splitlines()[:-1]
            rec["header"] = lines[:2]
            rec["sample_rows"] = lines[2:7]
            (SAMPLES / f"wfp_prices_{c}_head.csv").write_text("\n".join(lines[:40]))
        out[c] = rec
        print("wfp_hdx", c, rec.get("status"), rec.get("license"))
    return out


# --------------------------------------------------------------------------
# 9. SSURGO Soil Data Access at the Iowa point, for the SoilGrids comparison
# --------------------------------------------------------------------------
def probe_ssurgo_iowa():
    lat, lon = POINTS["iowa"]
    q = f"""SELECT mu.mukey, mu.muname, c.compname, c.comppct_r, h.hzdept_r, h.hzdepb_r,
    h.claytotal_r, h.sandtotal_r, h.om_r, h.ph1to1h2o_r, h.dbthirdbar_r, h.cec7_r,
    h.wthirdbar_r, h.wfifteenbar_r, h.awc_r
    FROM mapunit mu JOIN component c ON c.mukey = mu.mukey JOIN chorizon h ON h.cokey = c.cokey
    WHERE mu.mukey IN (SELECT * FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('point({lon} {lat})'))
    AND c.majcompflag = 'Yes' ORDER BY c.comppct_r DESC, h.hzdept_r"""
    t = time.time()
    r = requests.post("https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest",
                      data={"query": q, "format": "JSON+COLUMNNAME"}, timeout=90, headers=UA)
    rec = {"url": "https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest", "status": r.status_code,
           "seconds": round(time.time() - t, 1), "query": " ".join(q.split())}
    if r.ok:
        rec["table"] = r.json()["Table"]
    print("ssurgo", rec["status"], len(rec.get("table", [])))
    return rec


# --------------------------------------------------------------------------
# 10. India: IMD gridded data (POST endpoints used by imdlib 0.4.0) and the
#     data.gov.in OGD API without a key
# --------------------------------------------------------------------------
IMD_INDIA_POINTS = ["ludhiana_crop", "karnal_crop", "nashik_crop"]


def imd_cell(buf, lat, lon, lat0, lon0, step, nlat, nlon):
    """IMD .grd files are little-endian float32, longitude fastest, south row first."""
    import numpy as np
    a = np.frombuffer(buf, dtype="<f4").reshape(-1, nlat, nlon)
    j, i = int(round((lat - lat0) / step)), int(round((lon - lon0) / step))
    return a[:, j, i]


def probe_india():
    out = {}
    # Real-time daily rainfall, 0.25 degree, one day = 135 x 129 float32 = 69,660 bytes
    for day in ["15072025", "01082025"]:
        url = "https://imdpune.gov.in/cmpg/Realtimedata/Rainfall/rain.php"
        t = time.time()
        r = requests.post(url, data={"rain": day}, timeout=120, headers=UA)
        rec = {"url": url, "post": {"rain": day}, "status": r.status_code, "bytes": len(r.content),
               "content_disposition": r.headers.get("content-disposition"), "seconds": round(time.time() - t, 1)}
        if len(r.content) == 135 * 129 * 4:
            rec["rain_mm"] = {n: round(float(imd_cell(r.content, *POINTS[n], 6.5, 66.5, 0.25, 129, 135)[0]), 1)
                              for n in IMD_INDIA_POINTS}
        out[f"realtime_rain_{day}"] = rec
        print("imd realtime rain", day, rec.get("rain_mm"), rec["status"], rec["bytes"])
    # Archive daily Tmax 2023, 1 degree, 31 x 31 grid from 7.5N 67.5E, 365 days = 1.4 MB
    url = "https://imdpune.gov.in/cmpg/Griddata/maxtemp.php"
    t = time.time()
    r = requests.post(url, data={"maxtemp": "2023"}, timeout=180, headers=UA)
    rec = {"url": url, "post": {"maxtemp": "2023"}, "status": r.status_code, "bytes": len(r.content),
           "content_disposition": r.headers.get("content-disposition"), "seconds": round(time.time() - t, 1)}
    if len(r.content) == 31 * 31 * 365 * 4:
        rec["tmax_2023"] = {}
        for n in IMD_INDIA_POINTS:
            s = imd_cell(r.content, *POINTS[n], 7.5, 67.5, 1.0, 31, 31)
            s = s[s < 99]  # 99.9 marks missing
            rec["tmax_2023"][n] = {"max": round(float(s.max()), 1), "mean": round(float(s.mean()), 1),
                                   "days_over_40": int((s > 40).sum())}
    out["archive_tmax_2023"] = rec
    print("imd tmax 2023", rec.get("tmax_2023"))
    # Archive daily rain: check headers only (the yearly file is about 25 MB)
    url = "https://imdpune.gov.in/cmpg/Griddata/rainfall.php"
    with requests.post(url, data={"rain": "2023"}, timeout=120, headers=UA, stream=True) as r:
        out["archive_rain_2023_headers_only"] = {"url": url, "status": r.status_code,
                                                 "content_disposition": r.headers.get("content-disposition")}
    # data.gov.in OGD API (Agmarknet daily mandi prices) without a key
    r, rec = timed_get("https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070",
                       {"format": "json", "limit": 5, "filters[state.keyword]": "Haryana"})
    rec["body"] = None if r is None else r.text[:200]
    out["data_gov_in_no_key"] = rec
    print("data.gov.in", rec.get("status"), rec.get("body"))
    return out


PROBES = {
    "india": probe_india,
    "soilgrids_wcs": probe_soilgrids_wcs,
    "soilgrids_rest": probe_soilgrids_rest,
    "open_meteo": probe_open_meteo,
    "chirps": probe_chirps,
    "worldcereal": probe_worldcereal,
    "faostat": probe_faostat,
    "wapor": probe_wapor,
    "crop_calendar": probe_crop_calendar,
    "wfp_hdx": probe_wfp_hdx,
    "ssurgo_iowa": probe_ssurgo_iowa,
}


def main(argv):
    SAMPLES.mkdir(parents=True, exist_ok=True)
    chosen = argv or list(PROBES)
    path = SAMPLES / "global_probe_results.json"
    results = json.loads(path.read_text()) if path.exists() else {}
    for name in chosen:
        t = time.time()
        try:
            results[name] = PROBES[name]()
        except Exception as e:
            results[name] = {"error": f"{type(e).__name__}: {e}"}
            print(name, "FAILED", e)
        results[name + "_ran_at"] = time.strftime("%Y-%m-%d %H:%M:%S %z")
        results[name + "_seconds"] = round(time.time() - t, 1)
        path.write_text(json.dumps(results, indent=1, default=str))
    print("wrote", path)


if __name__ == "__main__":
    main(sys.argv[1:])
