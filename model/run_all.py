"""M entry point: library -> replay -> validation -> calendar -> scoring -> summary -> assistant.

Run from the repo root:  python model/run_all.py [--fields f1 f2] [--skip-assistant]
Writes model/out/web/** (README 8.4) and model/out/run_log.json (diagnostics for docs/METHODS.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    _here = Path(__file__).resolve().parent
    # model/ must not be on sys.path: model/calendar would shadow the stdlib calendar module
    sys.path[:] = [p for p in sys.path if Path(p or ".").resolve() != _here]
    sys.path.insert(0, str(_here.parent))

import argparse
import importlib.util
import json
import time

from model import config, inputs
from model.calendar.build import build_calendar, write_calendar
from model.contract import now_utc
from model.library.load_crops import load_crops, write_crops_json
from model.library.rotations import rotations_for_field, write_rotations_json
from model.replay.run import run_field, write_replay
from model.scoring.facts import build_strategies, top3, write_strategies
from model.scoring.summary import build_summary, write_summary
from model.validate.run import build_validation, write_validation


def run(fields: list[str], skip_assistant: bool = False) -> dict:
    t0 = time.time()
    mocks = inputs.any_mock()
    if mocks:
        print(f"warning: D files still marked mock: {mocks}")
    crops, prov = load_crops()
    write_crops_json(crops)
    write_rotations_json()
    print(f"crops from {prov['crops_yaml']}; data from {config.DATA_DIR}")
    log: dict = {"generated_at": now_utc(), "data_dir": str(config.DATA_DIR), "crops_yaml": prov["crops_yaml"],
                 "yields": prov["yields"], "prices": prov["prices"], "local_market": prov["local_market"],
                 "d_mock_files": mocks, "fields": {}}
    for fid in fields:
        t = time.time()
        field = inputs.field(fid)
        rots = rotations_for_field(field)
        result = run_field(fid, rots, crops)
        write_replay(fid, result)
        validation, vlog = build_validation(fid, crops, result)
        write_validation(fid, validation)
        write_calendar(fid, build_calendar(fid, result, rots, crops))
        strategies = build_strategies(fid, result, rots, crops, prov, inputs.neighbors(fid), validation)
        write_strategies(fid, strategies)
        summary, slog = build_summary(fid, rots["R0"])
        write_summary(fid, summary)
        flog = {"r0": [s.crop for s in rots["R0"].steps], "drought_years": result["drought_years"],
                "worst_drought_year": result["worst_drought_year"], "storm_precip": result["weather"]["actual"].storm_source,
                "validation": vlog, "climate_change": slog, "top3": {}, "summaries": {}}
        for sk in config.SCENARIOS:
            flog["top3"][sk] = top3(strategies["scenarios"][sk], rots)
            flog["summaries"][sk] = {rid: {k: round(float(v), 2) for k, v in run["summary"].items()} | {"feasible": run["feasible"]}
                                     for rid, run in result["scenarios"][sk].items()}
        log["fields"][fid] = flog
        print(f"{fid}: done in {time.time() - t:.0f}s; top3 cap300|actual = {flog['top3']['cap300|actual']}")
    if not skip_assistant:
        run_assistant()
    out = config.MODEL_DIR / "out" / "run_log.json"
    out.write_text(json.dumps(log, indent=1, default=str), encoding="utf-8")
    print(f"all done in {time.time() - t0:.0f}s; log at {out}")
    return log


def run_assistant() -> None:
    """The assistant step lives in model/assistant (owned by its own work stream). Run it if present."""
    if importlib.util.find_spec("model.assistant") is None or importlib.util.find_spec("model.assistant.__main__") is None:
        print("assistant: model/assistant/__main__.py not found; skipped (assistant files unchanged)")
        return
    import runpy
    runpy.run_module("model.assistant", run_name="__main__")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fields", nargs="*", default=config.FIELD_IDS)
    ap.add_argument("--skip-assistant", action="store_true")
    a = ap.parse_args()
    run(a.fields, a.skip_assistant)
