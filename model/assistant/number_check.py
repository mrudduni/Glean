"""Python port of the number check in README section 9.

The TypeScript port in web/lib/numberCheck.ts must pass the same cases in
number_check_cases.json. Where this file refines the README text, the
refinement is written in REFINEMENTS and covered by a case.
"""
from __future__ import annotations

import re
from typing import Iterable

NUMBER = r"\$?-?\d{1,3}(?:,\d{3})*(?:\.\d+)?(?!\d)|\$?-?\d+(?:\.\d+)?"
UNITS = r"mm|inches|in|%|°C|°F|days?|years?|cm|ft|m|acres|ac|bu|tons?|/ac"
# unit must not run into a following letter ("5 increase" is not "5 in")
PATTERN = re.compile(
    rf"(?<![A-Za-z0-9_.$])(?P<num>{NUMBER})(?:\s?(?P<unit>(?:{UNITS})(?:/ac)?)(?![A-Za-z]))?"
)
TAG_SPAN = re.compile(r"\[[A-Za-z0-9_]+\]")
FACT_ID_SPAN = re.compile(r"\([A-Za-z0-9_|:-]+(?:\.[A-Za-z0-9_|:-]+)+\)")

REFINEMENTS = [
    "The comma-thousands branch must not end inside a digit run (so 2012 is one number, not 201 and 2).",
    "U+2212 minus is read as '-'.",
    "A '-' directly after a letter or digit is a hyphen or range dash, not a sign.",
    "A 4-digit integer 1980-2035 is skipped only when it has no $ and no unit.",
    "Without an explicit minus the check compares magnitudes (a fall of 0.86 cm matches -0.86).",
    "A unit may carry '/ac' (bu/ac, tons/ac); a bare '/ac' reads as usd.",
    "Digits glued to a letter, digit, underscore, dot or $ are part of an identifier (R2, cap300), not a number.",
]

_MM_PER_IN = 25.4
_M_PER_FT = 0.3048


def _canon_unit(unit: str | None) -> str | None:
    if unit is None:
        return None
    u = unit.strip().lower()
    table = {
        "mm": "mm", "mm_per_yr": "mm", "mm_per_day": "mm",
        "in": "in", "inch": "in", "inches": "in",
        "ft": "ft", "feet": "ft",
        "cm": "cm", "cm_per_yr": "cm",
        "m": "m", "m_per_yr": "m",
        "%": "pct", "pct": "pct", "percent": "pct",
        "usd": "usd", "usd_ac": "usd", "$": "usd", "/ac": "usd", "usd/ac": "usd",
        "day": "days", "days": "days",
        "year": "years", "years": "years", "yr": "years",
        "°c": "c", "c": "c", "degc": "c",
        "°f": "f", "f": "f", "degf": "f",
        "ac": "ac", "acre": "ac", "acres": "ac", "area_ac": "ac",
        "bu": "bu", "bu/ac": "bu", "bu_ac": "bu",
        "ton": "tons", "tons": "tons", "t_ac_yr": "tons", "tons/ac": "tons", "tons_ac": "tons",
    }
    return table.get(u, u)


def _to_base(value: float, unit: str | None) -> tuple[float, str | None, float]:
    """Return (value, unit, scale) in base units. scale converts the rounding step."""
    if unit == "in":
        return value * _MM_PER_IN, "mm", _MM_PER_IN
    if unit == "ft":
        return value * _M_PER_FT, "m", _M_PER_FT
    if unit == "f":
        return (value - 32) * 5 / 9, "c", 5 / 9
    return value, unit, 1.0


def _decimals(num_text: str) -> int:
    m = re.search(r"\.(\d+)$", num_text)
    return len(m.group(1)) if m else 0


def _skip_spans(text: str) -> list[tuple[int, int]]:
    return [m.span() for m in TAG_SPAN.finditer(text)] + [
        m.span() for m in FACT_ID_SPAN.finditer(text)
    ]


def extract_numbers(text: str) -> list[dict]:
    """Return numbers to check: {text, value, unit, step, signed}. Skips applied."""
    text = text.replace("−", "-")
    # a '-' glued to a letter, digit or % is a hyphen or range dash, not a sign
    text = re.sub(r"(?<=[A-Za-z0-9%])-(?=\d)", " ", text)
    spans = _skip_spans(text)
    found: list[dict] = []
    pos = 0
    while pos <= len(text):
        m = PATTERN.search(text, pos)
        if not m:
            break
        start, end = m.span()
        pos = max(end, start + 1)
        raw = m.group("num")
        if any(a <= start < b for a, b in spans):
            continue
        unit = m.group("unit")
        has_dollar = raw.startswith("$")
        digits = raw.lstrip("$")
        explicit_neg = digits.startswith("-")
        digits_abs = digits.lstrip("-")
        # list marker: number at line start followed by '.' or ')'
        line_start = text.rfind("\n", 0, start) + 1
        if not text[line_start:start].strip() and not unit and end < len(text) and text[end] in ".)":
            if not has_dollar:
                continue
        # year
        plain = digits_abs.replace(",", "")
        if (
            not has_dollar and not unit and "," not in digits_abs and "." not in digits_abs
            and len(plain) == 4 and 1980 <= int(plain) <= 2035
        ):
            continue
        value = float(plain) * (-1 if explicit_neg else 1)
        if has_dollar:
            cu = "usd"
            unit_out = "usd"
        else:
            cu = _canon_unit(unit)
            unit_out = cu
        found.append(
            {
                "text": text[start:end].strip(),
                "value": value,
                "unit": unit_out,
                "step": 10 ** -_decimals(plain),
                "signed": explicit_neg,
            }
        )
    return found


def _units_compatible(a: str | None, b: str | None) -> bool:
    return a is None or b is None or a == b


def check_numbers(answer: str, facts: Iterable[dict]) -> list[dict]:
    """Facts: dicts with id, value, unit. Returns AskResponse.numbers entries."""
    facts = list(facts)
    prepared = []
    for f in facts:
        v, u, _ = _to_base(float(f["value"]), _canon_unit(f.get("unit")))
        prepared.append((f["id"], v, u))
    out = []
    for n in extract_numbers(answer):
        v, u, scale = _to_base(n["value"], n["unit"])
        step = n["step"] * scale
        hit = None
        for fid, fv, fu in prepared:
            if not _units_compatible(u, fu):
                continue
            x, y = (v, fv) if n["signed"] else (abs(v), abs(fv))
            if abs(x - y) <= max(0.05 * abs(fv), step) + 1e-9:
                hit = fid
                break
        out.append(
            {
                "text": n["text"],
                "value": n["value"],
                "unit": n["unit"],
                "verified": hit is not None,
                "fact_id": hit,
            }
        )
    return out


def unverified(answer: str, facts: Iterable[dict]) -> list[dict]:
    return [n for n in check_numbers(answer, facts) if not n["verified"]]
