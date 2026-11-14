"""Probe US agriculture APIs for Field Shift.

Run:  python probe_us.py            (all probes)
      python probe_us.py sda cdl    (selected probes)

Writes samples/us_probe_results.json. No keys are read or stored; probes that
need a key record the no-key response so we know the failure mode.
"""
import json, re, sys, time
from pathlib import Path

import requests
from pyproj import Transformer

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "samples" / "us_probe_results.json"
UA = {"User-Agent": "field-shift-probe/0.1 (research script)"}

# S1 central Iowa (Marsden Farm area); S2 cropland near SD-6 LEMA, Sheridan County, Kansas
POINTS = {"iowa_s1": (42.03, -93.75), "kansas_sd6": (39.40, -100.40)}


def timed(method, url, **kw):
    t = time.time()
    try:
        r = requests.request(method, url, timeout=kw.pop("timeout", 90), headers=UA, **kw)
        return r, {"url": url, "status": r.status_code, "seconds": round(time.time() - t, 2)}
    except Exception as e:
        return None, {"url": url, "error": f"{type(e).__name__}: {e}", "seconds": round(time.time() - t, 2)}


# 1. SSURGO through Soil Data Access -------------------------------------------
SDA = "https://SDMDataAccess.sc.egov.usda.gov/Tabular/post.rest"


def sda(query):
    r, rec = timed("POST", SDA, data={"query": query, "format": "JSON+COLUMNNAME"})
    if r is not None and r.ok:
        table = r.json().get("Table", [])
        rec["columns"], rec["rows"] = (table[0], table[1:]) if table else ([], [])
    elif r is not None:
        rec["body"] = r.text[:300]
    return rec


def probe_sda():
    out = {}
    for name, (lat, lon) in POINTS.items():
        wkt = f"point({lon} {lat})"
        o = {"mukey": sda(f"SELECT * FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('{wkt}')")}
        rows = o["mukey"].get("rows") or []
        if rows:
            mukey = rows[0][0]
            o["muaggatt"] = sda(
                "SELECT mukey, muname, aws0100wta, aws0150wta, slopegradwta, hydgrpdcd, drclassdcd, "
                f"niccdcd, iccdcd FROM muaggatt WHERE mukey = {mukey}")
            o["horizons"] = sda(
                "SELECT c.cokey, c.compname, c.comppct_r, c.majcompflag, h.hzname, h.hzdept_r, h.hzdepb_r, "
                "h.sandtotal_r, h.claytotal_r, h.om_r, h.awc_r, h.ksat_r, h.dbthirdbar_r, h.ph1to1h2o_r, "
                "h.kwfact, h.wthirdbar_r, h.wfifteenbar_r "
                f"FROM component c JOIN chorizon h ON h.cokey = c.cokey WHERE c.mukey = {mukey} "
                "AND c.majcompflag = 'Yes' ORDER BY c.comppct_r DESC, h.hzdept_r")
        out[name] = o
        print("sda", name, o["mukey"].get("status"), (rows[:1] if rows else None))
    return out


# 2. CropScape CDL point history -------------------------------------------------
CDL = "https://nassgeodata.gmu.edu/axis2/services/CDLService/GetCDLValue"
TO_ALBERS = Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True)


def probe_cdl(years=range(2008, 2025)):
    out = {}
    for name, (lat, lon) in POINTS.items():
        x, y = TO_ALBERS.transform(lon, lat)
        hist = {}
        for yr in years:
            r, rec = timed("GET", CDL, params={"year": yr, "x": round(x, 1), "y": round(y, 1)})
            cat = None
            if r is not None and r.ok:
                m = re.search(r'value: (\d+), category: "([^"]*)"', r.text)
                cat = f"{m.group(1)} {m.group(2)}" if m else r.text[:120]
            hist[yr] = cat or rec.get("status") or rec.get("error")
        out[name] = {"albers_xy": [round(x, 1), round(y, 1)], "history": hist,
                     "example_url": f"{CDL}?year=2024&x={round(x, 1)}&y={round(y, 1)}"}
        print("cdl", name, hist)
    return out


# 3. NASS Quick Stats without a key ------------------------------------------------
def probe_nass():
    r, rec = timed("GET", "https://quickstats.nass.usda.gov/api/api_GET/",
                   params={"commodity_desc": "CORN", "state_alpha": "IA", "year": 2024, "format": "JSON"})
    rec["body"] = None if r is None else r.text[:200]
    print("nass", rec.get("status"), rec.get("body"))
    return {"no_key": rec}


# 4. USGS Water Data OGC API: groundwater wells near SD-6 ---------------------------
USGS = "https://api.waterdata.usgs.gov/ogcapi/v0/collections"


def probe_usgs():
    lat, lon = POINTS["kansas_sd6"]
    bbox = f"{lon - 0.25},{lat - 0.25},{lon + 0.25},{lat + 0.25}"
    r, rec = timed("GET", f"{USGS}/monitoring-locations/items",
                   params={"bbox": bbox, "site_type_code": "GW", "limit": 20, "f": "json"})
    out = {"wells": rec}
    if r is not None and r.ok:
        feats = r.json().get("features", [])
        rec["n_returned"] = len(feats)
        rec["sample_ids"] = [f["id"] for f in feats[:5]]
        rec["ratelimit_remaining"] = r.headers.get("x-ratelimit-remaining")
        for f in feats[:5]:
            fr, frec = timed("GET", f"{USGS}/field-measurements/items",
                             params={"monitoring_location_id": f["id"], "limit": 500, "f": "json"})
            if fr is not None and fr.ok:
                ms = fr.json().get("features", [])
                vals = [(m["properties"].get("time"), m["properties"].get("value"),
                         m["properties"].get("parameter_code"), m["properties"].get("unit_of_measure"))
                        for m in ms]
                frec["n"] = len(vals)
                # 72019 = depth to water below land surface (ft); 62611 = level above NAVD88 (ft)
                frec["by_parameter"] = {}
                for code in sorted({v[2] for v in vals}):
                    s = sorted(v for v in vals if v[2] == code)
                    frec["by_parameter"][code] = {"n": len(s), "first": s[0], "last": s[-1]}
            out[f"measurements_{f['id']}"] = frec
            if frec.get("n"):
                break
    print("usgs", {k: (v.get("status"), v.get("n_returned", v.get("n"))) for k, v in out.items()})
    return out


# 5. PRISM web service and 6. AMS MyMarketNews without a key -------------------------
def probe_prism_ams():
    out = {}
    for name, url in {
        "prism_ppt_monthly_202407": "https://services.nacse.org/prism/data/get/us/4km/ppt/202407",
        "prism_old_public_path": "https://services.nacse.org/prism/data/public/4km/ppt/202407",
    }.items():
        r, rec = timed("HEAD", url, allow_redirects=True)
        if r is not None:
            rec["content_type"] = r.headers.get("content-type")
            rec["content_disposition"] = r.headers.get("content-disposition")
        out[name] = rec
    r, rec = timed("GET", "https://marsapi.ams.usda.gov/services/v1.2/reports")
    rec["body"] = None if r is None else r.text[:200]
    out["ams_no_key"] = rec
    print("prism/ams", {k: v.get("status") for k, v in out.items()})
    return out


PROBES = {"sda": probe_sda, "cdl": probe_cdl, "nass": probe_nass, "usgs": probe_usgs, "prism_ams": probe_prism_ams}


def main(argv):
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    for name in argv or list(PROBES):
        t = time.time()
        try:
            res[name] = PROBES[name]()
        except Exception as e:
            res[name] = {"error": f"{type(e).__name__}: {e}"}
            print(name, "FAILED", e)
        res[name + "_ran_at"] = time.strftime("%Y-%m-%d %H:%M:%S %z")
        res[name + "_seconds"] = round(time.time() - t, 1)
        OUT.write_text(json.dumps(res, indent=1, default=str))
    print("wrote", OUT)


if __name__ == "__main__":
    main(sys.argv[1:])
