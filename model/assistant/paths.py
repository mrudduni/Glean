"""Paths and env loading for the assistant scripts. Secrets stay outside the repo."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[2]
ENV_FILE = Path(os.environ.get("FIELDSHIFT_ENV", Path.home() / ".fieldshift" / ".env"))
load_dotenv(ENV_FILE)

OUT_WEB = Path(os.environ.get("MODEL_OUT_WEB", REPO / "model" / "out" / "web"))
DATA_WEB = Path(
    os.environ.get(
        "DATA_WEB",
        Path.home() / "fieldshift-data" / "data-pipeline" / "out" / "web",
    )
)
CONTENT_DIR = Path(os.environ.get("CONTENT_DIR", REPO / "content"))
FIELDS = ["f1", "f2", "f3"]
SCENARIO = "cap300|actual"
