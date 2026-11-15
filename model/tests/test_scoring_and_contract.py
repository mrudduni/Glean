"""Scoring rules (handover 5.5) and the contract check on the committed outputs."""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

from model import config
from model.library.load_crops import load_crops
from model.library.rotations import LIBRARY, Rotation, Step
from model.scoring.criteria import max_host_run, normalise

ROOT = config.REPO_DIR


@pytest.fixture(scope="module")
def crops():
    return load_crops()[0]


def test_pest_run(crops):
    assert max_host_run(Rotation("R0", (Step("corn"),), True, "cap150"), crops) == config.PEST_RUN_CAP
    assert max_host_run(LIBRARY["R1"], crops) == 1
    assert max_host_run(LIBRARY["R2"], crops) == 1
    assert max_host_run(LIBRARY["R3"], crops) == 2        # triticale then wheat: both small grains
    assert max_host_run(LIBRARY["R4"], crops) == 4


def test_normalise_inverts_and_handles_ties():
    raws = {"A": {c: 1.0 for c in config.CRITERIA}, "B": {c: 1.0 for c in config.CRITERIA}}
    raws["A"]["water_use"], raws["B"]["water_use"] = 100.0, 300.0
    raws["A"]["income_mean"], raws["B"]["income_mean"] = 100.0, 300.0
    n = normalise(raws, {"A": True, "B": True})
    assert n["A"]["water_use"] == 100 and n["B"]["water_use"] == 0       # lower is better
    assert n["A"]["income_mean"] == 0 and n["B"]["income_mean"] == 100
    assert n["A"]["soil_health"] == 50                                    # best == worst


def test_rotations_library_matches_readme():
    seq = {rid: [s.crop for s in r.steps] for rid, r in LIBRARY.items()}
    assert seq == {"R1": ["corn", "wheat", "sorghum"], "R2": ["wheat", "sorghum", "fallow"],
                   "R3": ["wheat", "sorghum", "triticale"], "R4": ["alfalfa"] * 4 + ["corn", "wheat"],
                   "R5": ["corn", "soybean", "wheat"], "R6": ["cotton", "wheat", "sorghum"]}
    assert LIBRARY["R5"].steps[2].cover_after == "rye_cover"


def _out(fid, name):
    p = config.OUT_DIR / "field" / fid / name
    if not p.exists():
        pytest.skip("run model/run_all.py first")
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.mark.parametrize("fid", config.FIELD_IDS)
def test_outputs_real_and_complete(fid):
    for name in ("replay.json", "strategies.json", "calendar.json", "summary.json", "validation.json"):
        d = _out(fid, name)
        assert d["_meta"]["mock"] is False, name
    rp = _out(fid, "replay.json")
    assert set(rp["scenarios"]) == set(config.SCENARIOS)
    for runs in rp["scenarios"].values():
        assert {"R0", "R1", "R2", "R3", "R4", "R5"} <= set(runs)
        for run in runs.values():
            assert len(run["by_year"]) == config.N_YEARS


@pytest.mark.parametrize("fid", config.FIELD_IDS)
def test_dryland_never_ranks_irrigated_first(fid):
    st = _out(fid, "strategies.json")
    for sk in ("dryland|actual", "dryland|hotdry"):
        for e in st["scenarios"][sk]:
            rot = LIBRARY.get(e["rotation_id"])
            if rot and rot.irrigated:
                assert not e["feasible"], (sk, e["rotation_id"])


def test_check_contract_only_model_passes():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_contract.py"), "--data-dir",
                        str(config.OUT_DIR), "--only-model", "--allow-mock"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:]
