"""Crop sequence -> RotationClass (handover §6.12). Shared by demo fields and neighbours.

    classify(["corn","corn","wheat",...]) -> {"rotation_class", "sequence", "confidence"}

Rules are applied in order; the first that matches wins. `confidence` counts the
years whose crop belongs to the class's canonical sequence: >= 6 good, 4–5 fair,
otherwise limited.
"""
from __future__ import annotations

from collections import Counter

VALID = {"corn", "sorghum", "wheat", "soybean", "alfalfa", "triticale", "rye_cover", "cotton", "fallow"}


def _confidence(crops: list[str], seq: list[str]) -> str:
    s = set(seq)
    consistent = sum(1 for c in crops if c in s)
    return "good" if consistent >= 6 else "fair" if consistent >= 4 else "limited"


def _mixed_sequence(crops: list[str]) -> list[str]:
    known = [c for c in crops if c in VALID]
    windows = [tuple(known[i:i + 3]) for i in range(len(known) - 2)]
    if windows:
        counts = Counter(windows)
        best_n = max(counts.values())
        # tie-break: the earliest window among the most common
        return list(next(w for w in windows if counts[w] == best_n))
    if known:
        return [c for c, _ in Counter(known).most_common(3)]
    return ["fallow"]


def classify(crops: list[str]) -> dict:
    n = len(crops)
    k = Counter(crops)
    corn, soy, wheat, sorg, fal, alf = (k["corn"], k["soybean"], k["wheat"], k["sorghum"],
                                        k["fallow"], k["alfalfa"])
    if alf >= 3:
        cls, seq = "alfalfa", ["alfalfa", "alfalfa", "alfalfa", "alfalfa", "corn", "wheat"]
    elif n and corn >= 0.75 * n:
        cls, seq = "continuous_corn", ["corn"]
    elif corn >= 2 and soy >= 2:
        cls, seq = "corn_soy", (["corn", "soybean", "wheat"] if wheat else ["corn", "soybean"])
    elif wheat >= 2 and sorg >= 2 and fal >= 1 and corn <= 1:
        cls, seq = "wsf", ["wheat", "sorghum", "fallow"]
    elif wheat >= 3 and fal >= 3 and sorg <= 1:
        cls, seq = "wheat_fallow", ["wheat", "fallow"]
    elif corn >= 2 and (wheat >= 1 or sorg >= 1):
        cls, seq = "corn_wheat_sorghum", ["corn", "wheat", "sorghum"]
    else:
        cls, seq = "mixed", _mixed_sequence(crops)
    return {"rotation_class": cls, "sequence": seq, "confidence": _confidence(crops, seq)}


if __name__ == "__main__":
    tests = {
        "cc": ["corn"] * 7 + ["wheat"],
        "wsf": ["wheat", "sorghum", "fallow"] * 2 + ["wheat", "sorghum"],
        "wf": ["wheat", "fallow"] * 4,
        "cws": ["corn", "wheat", "sorghum"] * 2 + ["corn", "corn"],
        "alf": ["alfalfa"] * 4 + ["corn", "wheat", "alfalfa", "alfalfa"],
        "cs": ["corn", "soybean"] * 4,
        "mixed": ["sorghum", "other", "sorghum", "soybean", "other", "sorghum", "triticale", "sorghum"],
    }
    for name, seq in tests.items():
        print(name, classify(seq))
