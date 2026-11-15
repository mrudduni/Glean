"""GPM IMERG Final daily (GPM_3IMERGDF v07) -> out/processed/{fid}/precip_imerg_daily.csv

Sources, in order:
  1. Manual Giovanni exports: raw/imerg/{fid}.csv (or raw/imerg/county.csv for all three).
     Giovanni -> "Time Series, Area-Averaged" -> GPM_3IMERGDF precipitation -> CSV.
  2. Automated: OPeNDAP subset of each daily granule at GES DISC (one tiny request per
     day for a box covering all three fields), found through CMR with earthaccess.
     Needs EARTHDATA_USERNAME / EARTHDATA_PASSWORD and the "NASA GESDISC DATA ARCHIVE"
     application approved in your Earthdata profile. ~9,300 requests; resumable.

Each field uses the 0.1° IMERG cell that contains its centre (fields are ~15 km apart,
so they fall in different or neighbouring cells).
Columns: date, precip_mm
"""
from __future__ import annotations

import io
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import requests  # noqa: E402

import config as C  # noqa: E402
from common import Skip, load_fields_draft, log, mark_exhausted, note_response, spend, write_csv  # noqa: E402

DIR = C.RAW / "imerg"
CELLS = DIR / "cells_daily.csv"   # resumable cache: date, cell, precip_mm
COMPLETE = DIR / ".complete"      # written once every granule has been fetched
COLUMNS = ["date", "precip_mm"]
OUTPUTS = [C.PROCESSED / fid / "precip_imerg_daily.csv" for fid in C.FIELD_IDS]
END = "2025-12-31"


def cell_index(lon: float, lat: float) -> tuple[int, int]:
    """IMERG 0.1° grid: lon -179.95..179.95 (3600), lat -89.95..89.95 (1800)."""
    return int(np.floor((lon + 180) / 0.1)), int(np.floor((lat + 90) / 0.1))


def parse_giovanni(p: Path) -> pd.DataFrame:
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    start = next(i for i, ln in enumerate(lines) if re.match(r"^(time|timestamp|date)\s*,", ln, re.I))
    df = pd.read_csv(io.StringIO("\n".join(lines[start:])))
    df.columns = ["date", "precip_mm"] + list(df.columns[2:])
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["precip_mm"] = pd.to_numeric(df["precip_mm"], errors="coerce").mask(lambda s: s < 0)
    return df[COLUMNS]


def _opendap_url(data_url: str) -> str:
    # https://data.gesdisc.earthdata.nasa.gov/data/GPM_L3/... -> https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/...
    return re.sub(r"^https://[^/]+/data/", "https://gpm1.gesdisc.eosdis.nasa.gov/opendap/", data_url)


def _parse_ascii(text: str) -> np.ndarray:
    """DAP2 .ascii body: rows like '[0][3], 0.12, 0, 1.5' (lon index, then lat values)."""
    rows = []
    for ln in text.splitlines():
        m = re.match(r"^\s*(?:precipitation)?(\[\d+\])+\s*,\s*(.*)$", ln)
        if m:
            rows.append([float(v) for v in m.group(2).split(",")])
    return np.array(rows)


URS_HOST = "urs.earthdata.nasa.gov"
WORKERS = 2          # GES DISC blocks clients that open many connections; spend() also paces to 4/s
MAX_FAILS = 25       # consecutive failures before the step gives up (resumable)


class URSSession(requests.Session):
    """GES DISC's documented login: basic auth sent only on the redirect to Earthdata Login."""

    def __init__(self, user: str, pw: str):
        super().__init__()
        self.auth = (user, pw)

    def rebuild_auth(self, prepared_request, response):
        new = requests.utils.urlparse(prepared_request.url).hostname
        old = requests.utils.urlparse(response.request.url).hostname
        if "Authorization" in prepared_request.headers and new != old and URS_HOST not in (new, old):
            del prepared_request.headers["Authorization"]


def _probe(url: str, sessions: list) -> requests.Session:
    """Return the first session that can read one granule; Skip with the reason otherwise."""
    last = None
    for s in sessions:
        spend("gesdisc")
        try:
            r = s.get(url, timeout=60)
        except requests.RequestException as e:
            raise Skip(f"GES DISC not reachable ({type(e).__name__}); it may be blocking this IP "
                       f"for a while after failed requests — rerun later") from e
        note_response("gesdisc", r)
        if r.ok and "precipitation" in r.text:
            return s
        last = r.status_code
    if last in (401, 403):
        raise Skip("GES DISC refused the Earthdata login (HTTP %s): in your Earthdata profile approve "
                   "'NASA GESDISC DATA ARCHIVE' under Applications -> Authorized Apps, then rerun" % last)
    raise Skip(f"GES DISC OPeNDAP returned HTTP {last} for a test granule")


def automated(cells: dict[str, tuple[int, int]]) -> pd.DataFrame:
    if not C.has_earthdata():
        raise Skip("Earthdata login needed for IMERG (or drop Giovanni CSVs in raw/imerg/)")
    import earthaccess

    earthaccess.login(strategy="environment" if C.EARTHDATA_USERNAME else "netrc")
    ix = [c[0] for c in cells.values()]
    iy = [c[1] for c in cells.values()]
    x0, x1, y0, y1 = min(ix), max(ix), min(iy), max(iy)

    done = pd.read_csv(CELLS) if CELLS.exists() else pd.DataFrame(columns=["date", "cell", "precip_mm"])
    have = set(done.date)
    spend("earthdata")
    grans = earthaccess.search_data(short_name="GPM_3IMERGDF", version="07", temporal=(C.IMERG_START, END))
    todo = []
    for g in grans:
        links = [u for u in g.data_links() if u.endswith(".nc4")]
        if not links:
            continue
        m = re.search(r"3IMERG\.(\d{8})", links[0])
        date = pd.to_datetime(m.group(1)).strftime("%Y-%m-%d")
        if date not in have:
            todo.append((date, _opendap_url(links[0])))
    log("imerg", f"{len(grans)} granules, {len(todo)} still to fetch")
    if not todo:
        DIR.mkdir(parents=True, exist_ok=True)
        COMPLETE.touch()
        return done

    def q(url):
        return f"{url}.ascii?precipitation[0:0][{x0}:{x1}][{y0}:{y1}]"

    sess = _probe(q(todo[0][1]), [URSSession(C.EARTHDATA_USERNAME, C.EARTHDATA_PASSWORD),
                                  earthaccess.get_requests_https_session()])

    def one(date, url):
        spend("gesdisc")
        r = sess.get(q(url), timeout=120)
        note_response("gesdisc", r)
        if r.status_code in (401, 403):   # login refused: stop at once, never hammer
            mark_exhausted("gesdisc", f"HTTP {r.status_code} login refused")
            raise Skip(f"GES DISC refused the login (HTTP {r.status_code}); check the GESDISC app approval")
        r.raise_for_status()
        arr = _parse_ascii(r.text)  # shape (nlon, nlat)
        return [(date, f"{x0 + i}_{y0 + j}", float(arr[i, j]))
                for i in range(arr.shape[0]) for j in range(arr.shape[1])]

    def save(new):
        df = pd.concat([done, pd.DataFrame(new, columns=done.columns)], ignore_index=True)
        DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(CELLS, index=False)

    new, fails, n_bad = [], 0, 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(one, d, u): d for d, u in todo}
        for n, f in enumerate(as_completed(futs), 1):
            try:
                new += f.result()
                fails = 0
            except Skip:
                for other in futs:
                    other.cancel()
                save(new)
                raise
            except Exception as e:
                fails += 1
                n_bad += 1
                log("imerg", f"{futs[f]}: {str(e)[:120]}")
                if fails >= MAX_FAILS:
                    for other in futs:
                        other.cancel()
                    save(new)
                    raise Skip(f"GES DISC: {MAX_FAILS} failures in a row after {n} days; "
                               f"progress saved, rerun later to resume")
            if n % 500 == 0 or n == len(futs):
                save(new)
                log("imerg", f"{n}/{len(futs)} days ({n_bad} failed, retried on the next run)")
    if n_bad == 0:
        COMPLETE.touch()
    return pd.read_csv(CELLS) if CELLS.exists() else done


def main(force: bool = False) -> None:
    gdf = load_fields_draft()
    cells = {fid: cell_index(g.representative_point().x, g.representative_point().y)
             for fid, g in gdf.geometry.items()}
    partial = CELLS.exists() and not COMPLETE.exists()   # automated download still has gaps
    todo = [fid for fid in C.FIELD_IDS
            if force or partial or not (C.PROCESSED / fid / "precip_imerg_daily.csv").exists()]
    if not todo:
        log("imerg", "exists: all precip_imerg_daily.csv")
        return
    manual = {fid: DIR / f"{fid}.csv" for fid in todo if (DIR / f"{fid}.csv").exists()}
    if not manual and (DIR / "county.csv").exists():
        manual = {fid: DIR / "county.csv" for fid in todo}
    if manual:
        for fid, p in manual.items():
            write_csv(C.PROCESSED / fid / "precip_imerg_daily.csv", parse_giovanni(p), COLUMNS)
            log("imerg", f"{fid}: parsed Giovanni export {p.name}")
        todo = [f for f in todo if f not in manual]
        if not todo:
            return
    df = automated({f: cells[f] for f in todo})
    df = df[df.precip_mm >= 0]
    for fid in todo:
        key = f"{cells[fid][0]}_{cells[fid][1]}"
        s = df[df.cell == key].drop_duplicates("date").sort_values("date")
        out = s[["date", "precip_mm"]].copy()
        out["precip_mm"] = out.precip_mm.round(2)
        write_csv(C.PROCESSED / fid / "precip_imerg_daily.csv", out, COLUMNS)
        log("imerg", f"{fid}: {len(out)} days, cell {key}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
