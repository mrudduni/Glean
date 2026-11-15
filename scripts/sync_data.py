"""Copy every producer's output into the web app, exactly the README 6.5 mapping. No transformation.

Usage: python scripts/sync_data.py [--root REPO] [--strict]
  --strict  exit 1 if any source is missing
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TREE_COPIES = [("data-pipeline/out/web", "web/public/data"), ("model/out/web", "web/public/data")]
FILE_COPIES = [
    ("content/card_text.json", "web/public/data/content/card_text.json"),
    ("content/copy.json", "web/public/data/content/copy.json"),
    ("content/glossary.json", "web/public/data/content/glossary.json"),
    ("content/assistant_questions.json", "web/public/data/content/assistant_questions.json"),
    ("design/tokens.css", "web/styles/tokens.css"),
    ("design/tokens.json", "web/styles/tokens.json"),
]


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    root = a.root.resolve()
    missing, total = [], 0
    for src_rel, dst_rel in TREE_COPIES:
        src, dst = root / src_rel, root / dst_rel
        if not src.is_dir():
            missing.append(src_rel)
            print(f"MISSING  {src_rel}/")
            continue
        files = [p for p in src.rglob("*") if p.is_file()]
        for p in files:
            copy_file(p, dst / p.relative_to(src))
        total += len(files)
        print(f"copied   {len(files):3d} files  {src_rel}/ -> {dst_rel}/")
    for src_rel, dst_rel in FILE_COPIES:
        src = root / src_rel
        if not src.is_file():
            missing.append(src_rel)
            print(f"MISSING  {src_rel}")
            continue
        copy_file(src, root / dst_rel)
        total += 1
        print(f"copied     1 file   {src_rel} -> {dst_rel}")
    print(f"\n{total} files copied into {root / 'web'}; {len(missing)} sources missing")
    return 1 if (a.strict and missing) else 0


if __name__ == "__main__":
    sys.exit(main())
