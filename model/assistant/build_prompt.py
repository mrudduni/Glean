"""prompt.md -> out/web/assistant/prompt.json"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from paths import OUT_WEB

HERE = Path(__file__).resolve().parent
VERSION = "1.0.0"
PLACEHOLDERS = ["lang_name", "field_name", "scenario_label", "top_rotations", "facts_block"]


def build() -> Path:
    system = (HERE / "prompt.md").read_text(encoding="utf8").strip() + "\n"
    for p in PLACEHOLDERS:
        assert "{" + p + "}" in system, p
    out = OUT_WEB / "assistant" / "prompt.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "_meta": {
            "schema": "prompt@1",
            "mock": False,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generator": "model/assistant/build_prompt.py",
        },
        "version": VERSION,
        "system": system,
        "temperature": 0.2,
        "max_tokens": 600,
    }
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    return out


if __name__ == "__main__":
    print(build())
