"""Run every pipeline step in order.

    python data-pipeline/run_all.py               # run everything; finished downloads are skipped
    python data-pipeline/run_all.py --force       # redo every step
    python data-pipeline/run_all.py --only power,build_fields
    python data-pipeline/run_all.py --skip modis_ornl   # leave out the slow no-login MODIS fallback
    python data-pipeline/run_all.py --list

Fetch steps skip when their output already exists (every download is also cached in raw/).
Build steps (build_*, harmonize, match) always rerun: they are fast and pick up inputs
that arrived since the last run. A step that cannot run yet (missing API key, AppEEARS
task still queued) is reported as SKIPPED and the rest of the pipeline continues.
"""
from __future__ import annotations

import argparse
import importlib
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

from common import Skip, usage_report  # noqa: E402

# (name, module, callable) — order matters
STEPS = [
    ("county", "fetch.county", "main"),
    ("csb", "fetch.csb", "main"),
    ("select_fields", "process.select_fields", "main"),
    ("pool_select", "neighbors.pool", "select"),
    ("appeears", "fetch.appeears", "main"),          # submit early: the queue can take hours
    ("power", "fetch.power", "main"),
    ("ssurgo", "fetch.ssurgo", "main"),
    ("terrain", "process.terrain", "main"),
    ("modis_ornl", "fetch.modis_ornl", "main"),      # fallback while AppEEARS is pending
    ("nass", "fetch.nass", "main"),
    ("prism", "fetch.prism", "main"),
    ("imerg", "fetch.imerg", "main"),
    ("openet", "fetch.openet", "main"),
    ("grace", "fetch.grace", "main"),
    ("wells", "fetch.wells", "main"),
    ("harmonize", "process.harmonize", "main"),
    ("build_fields", "process.build_fields", "main"),
    ("pool_features", "neighbors.pool", "features"),
    ("match", "neighbors.match", "main"),
    ("build_water", "process.build_water", "main"),
    ("build_observed", "process.build_observed", "main"),
    ("build_sources", "process.build_sources", "main"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="redo steps even if outputs exist")
    ap.add_argument("--only", help="comma-separated step names")
    ap.add_argument("--skip", help="comma-separated step names to leave out (e.g. modis_ornl)")
    ap.add_argument("--list", action="store_true", help="list steps and exit")
    a = ap.parse_args()
    if a.list:
        for n, m, f in STEPS:
            print(f"{n:16s} {m}.{f}")
        return 0
    only = set(a.only.split(",")) if a.only else None
    skip = set(a.skip.split(",")) if a.skip else set()
    if (bad := ((only or set()) | skip) - {n for n, _, _ in STEPS}):
        print(f"unknown steps: {sorted(bad)}")
        return 2
    results = []
    for name, mod, fn in STEPS:
        if (only and name not in only) or name in skip:
            continue
        t0 = time.time()
        print(f"\n=== {name}")
        try:
            getattr(importlib.import_module(mod), fn)(force=a.force)
            results.append((name, "ok", ""))
        except Skip as e:
            print(f"  SKIPPED: {e}")
            results.append((name, "skipped", str(e)))
        except Exception as e:  # keep going; report at the end
            traceback.print_exc()
            results.append((name, "FAILED", f"{type(e).__name__}: {e}"))
        results[-1] = (*results[-1], time.time() - t0)
    print("\n=== summary")
    for name, status, msg, dt in results:
        print(f"  {name:16s} {status:8s} {dt:6.1f}s  {msg[:110]}")
    print("\n=== API usage this period (budgets in common.BUDGETS; raw/usage.json)")
    for svc, (used, limit, period) in usage_report().items():
        print(f"  {svc:10s} {used:6d} / {limit:<6d} per {period}")
    return 1 if any(s == "FAILED" for _, s, _, _ in results) else 0


if __name__ == "__main__":
    sys.exit(main())
