"""Readers for D's files under config.DATA_DIR. Missing optional files return None."""
from __future__ import annotations

import json
from functools import lru_cache

import pandas as pd

from model import config


def _json(rel: str) -> dict | None:
    path = config.DATA_DIR / rel
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


@lru_cache(maxsize=None)
def fields() -> dict:
    data = _json("web/fields.json")
    if data is None:
        raise FileNotFoundError(f"fields.json not found under {config.DATA_DIR}")
    return {f["id"]: f for f in data["fields"]}


def field(fid: str) -> dict:
    return fields()[fid]


def water(fid: str) -> dict | None:
    return _json(f"web/field/{fid}/water.json")


def observed(fid: str) -> dict | None:
    return _json(f"web/field/{fid}/observed.json")


def neighbors(fid: str) -> dict | None:
    return _json(f"web/field/{fid}/neighbors.json")


def sources() -> dict | None:
    return _json("web/sources.json")


def processed_csv(fid: str, name: str, date_col: str = "date") -> pd.DataFrame | None:
    path = config.DATA_DIR / "processed" / fid / name
    if not path.exists():
        return None
    df = pd.read_csv(path)
    if df.empty:
        return None
    if date_col in df:
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.set_index(date_col).sort_index()
    return df


def any_mock() -> list[str]:
    """Names of D files that still carry _meta.mock = true."""
    out = []
    for rel in ["web/fields.json", "processed/nass.json"] + [f"web/field/{f}/{n}.json" for f in config.FIELD_IDS
                                                                for n in ("water", "observed", "neighbors")]:
        d = _json(rel)
        if d and d.get("_meta", {}).get("mock"):
            out.append(rel)
    return out
