"""Rotation library R1-R6 (CONTRACT 7.2) and the per-field current rotation R0."""
from __future__ import annotations

from dataclasses import dataclass, field

from model import config
from model.contract import meta, write_json

CAP_ORDER = {c: i for i, c in enumerate(config.CAP_IDS)}


@dataclass(frozen=True)
class Step:
    crop: str
    cover_after: str | None = None

    def as_json(self) -> dict:
        return {"crop": self.crop, "cover_after": self.cover_after}


@dataclass(frozen=True)
class Rotation:
    id: str
    steps: tuple[Step, ...]
    irrigated: bool
    min_cap: str
    requires_equipment: tuple[str, ...] = ()
    needs_forage_market: bool = False
    tier: str = "must"
    rotation_class: str | None = None
    years: tuple[int, int] | None = field(default=None)

    @property
    def crops(self) -> list[str]:
        return [s.crop for s in self.steps]

    def feasible(self, cap: str) -> bool:
        return CAP_ORDER[cap] >= CAP_ORDER[self.min_cap]

    def as_json(self) -> dict:
        return {
            "id": self.id,
            "steps": [s.as_json() for s in self.steps],
            "irrigated": self.irrigated,
            "min_cap": self.min_cap,
            "requires_equipment": list(self.requires_equipment),
            "needs_forage_market": self.needs_forage_market,
            "tier": self.tier,
        }


def _s(*crops: str) -> tuple[Step, ...]:
    return tuple(Step(c) for c in crops)


LIBRARY: dict[str, Rotation] = {
    "R1": Rotation("R1", _s("corn", "wheat", "sorghum"), irrigated=True, min_cap="cap150"),
    "R2": Rotation("R2", _s("wheat", "sorghum", "fallow"), irrigated=False, min_cap="dryland"),
    # triticale is cut for forage (hay or silage), so it needs haying gear and a forage buyer
    "R3": Rotation("R3", _s("wheat", "sorghum", "triticale"), irrigated=False, min_cap="dryland",
                   requires_equipment=("hay",), needs_forage_market=True),
    "R4": Rotation("R4", _s("alfalfa", "alfalfa", "alfalfa", "alfalfa", "corn", "wheat"), irrigated=True,
                   min_cap="cap300", requires_equipment=("hay",), needs_forage_market=True),
    # corn-soybean in Finney County is mostly irrigated (NASS: 14,000 irrigated vs 3,000 dryland
    # soybean acres in 2001; dryland soybean averages about 19 bu/ac in the district), so R5 needs a well
    "R5": Rotation("R5", (Step("corn"), Step("soybean"), Step("wheat", "rye_cover")), irrigated=True,
                   min_cap="cap150"),
    "R6": Rotation("R6", _s("cotton", "wheat", "sorghum"), irrigated=False, min_cap="dryland",
                   requires_equipment=("cotton",), tier="could"),
}


def build_r0(field: dict) -> Rotation:
    """R0 from D's detected sequence. Irrigated fields need at least cap150 to keep running it."""
    det = field["detected"]
    seq = [c for c in det["sequence"] if c != "other"] or ["fallow"]
    irrigated = bool(field["irrigated"])
    return Rotation(
        "R0", _s(*seq), irrigated=irrigated, min_cap="cap150" if irrigated else "dryland",
        rotation_class=det["rotation_class"], years=tuple(det["years"]),
    )


def rotations_for_field(field: dict) -> dict[str, Rotation]:
    """All rotations the replay runs for one field, R0 first.

    A field without irrigation (fields.json irrigated: false) cannot pump, so every rotation whose
    min_cap is above dryland is infeasible there in every scenario.
    """
    out = {"R0": build_r0(field)}
    out.update(LIBRARY)
    return out


def write_rotations_json() -> None:
    payload = {"_meta": meta("rotations@1", "model/library/rotations.py"),
               "rotations": [r.as_json() for r in LIBRARY.values()]}
    write_json(config.OUT_DIR / "rotations.json", payload)
