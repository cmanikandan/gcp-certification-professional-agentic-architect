"""Test setup for lab_20_e2e_ai_threat_defense."""

from __future__ import annotations

import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = LAB_DIR.parent.parent.parent

for entry in (str(REPO_ROOT), str(LAB_DIR)):
    if entry in sys.path:
        sys.path.remove(entry)
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(LAB_DIR))

for _name in ("lab", "agent", "mcp_server"):
    sys.modules.pop(_name, None)
