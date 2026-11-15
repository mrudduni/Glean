#!/usr/bin/env python3
"""Colour-blind check for design/tokens.json.

Simulates protanopia, deuteranopia and tritanopia (Machado et al. 2009, severity 1.0, linear RGB)
and prints the smallest CIE76 delta-E between any two colours in each group.
Rule of thumb: delta-E >= 12 is easy to tell apart; below 8 needs a second cue (label, dash, hatching).
Usage: python design/check_cvd.py [--min-rot 12] [--min-crop 6] [--min-risk 8]
Exit code 1 if a group is below its minimum under any simulation.
"""
import itertools
import json
import sys
from pathlib import Path

MATS = {
    "normal": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    "protan": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    "deutan": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    "tritan": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}


def to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_lin(h):
    h = h.lstrip("#")
    return [to_lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)]


def lab(rgb):
    r, g, b = rgb
    x = 0.4124 * r + 0.3576 * g + 0.1805 * b
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = 0.0193 * r + 0.1192 * g + 0.9505 * b

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x / 0.95047), f(y), f(z / 1.08883)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def simulate(h, m):
    v = hex_lin(h)
    out = [max(0.0, min(1.0, sum(m[i][j] * v[j] for j in range(3)))) for i in range(3)]
    return lab(out)


def de(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def worst(group):
    res = {}
    for name, m in MATS.items():
        labs = {k: simulate(v, m) for k, v in group.items()}
        pair = min(itertools.combinations(group, 2), key=lambda p: de(labs[p[0]], labs[p[1]]))
        res[name] = (round(de(labs[pair[0]], labs[pair[1]]), 1), pair)
    return res


if __name__ == "__main__":
    args = sys.argv[1:]

    def opt(n, d):
        return float(args[args.index(n) + 1]) if n in args else d
    mins = {"rot": opt("--min-rot", 12), "crop": opt("--min-crop", 6), "risk": opt("--min-risk", 8)}
    tj = json.loads((Path(__file__).parent / "tokens.json").read_text(encoding="utf-8"))
    bad = False
    for theme, src in (("light", tj), ("dark", tj.get("dark", {}))):
      for g in ("rot", "crop", "risk"):
        if g not in src:
            continue
        print(f"[{theme} {g}] need >= {mins[g]}")
        for sim, (d, pair) in worst(src[g]).items():
            flag = "" if d >= mins[g] else "  <-- LOW"
            bad |= d < mins[g]
            print(f"  {sim:7s} min dE {d:5.1f}  closest: {pair[0]} / {pair[1]}{flag}")
    sys.exit(1 if bad else 0)
