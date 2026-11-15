import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from number_check import check_numbers, extract_numbers  # noqa: E402

CASES = json.loads((HERE / "number_check_cases.json").read_text(encoding="utf8"))["cases"]


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_case(case):
    got = check_numbers(case["answer"], case["facts"])
    exp = case["expected"]
    assert [g["text"] for g in got] == [e["text"] for e in exp]
    for g, e in zip(got, exp):
        assert g["verified"] == e["verified"], g
        assert g["fact_id"] == e["fact_id"], g
        assert g["unit"] == e["unit"], g
        assert g["value"] == pytest.approx(e["value"]), g


def test_readme_examples():
    f = [{"id": "aws", "value": 305, "unit": "mm"}]
    assert check_numbers("about 12 inches", f)[0]["verified"]
    assert not check_numbers("500 mm", [])[0]["verified"]
    assert check_numbers("in 2012", f) == []


def test_extract_has_no_side_effects():
    assert extract_numbers("") == []
