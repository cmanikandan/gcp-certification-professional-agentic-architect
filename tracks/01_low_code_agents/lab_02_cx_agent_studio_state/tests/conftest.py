"""Test setup for lab_02_cx_agent_studio_state.

Each lab is self-contained, so many labs define a module called ``lab`` and some
define ``agent``. Python caches imported modules by name, so in a full-suite run
the first lab imported would otherwise be handed to every later lab's tests.

pytest loads this conftest immediately before importing this directory's test
modules, so evicting those names here guarantees ``import lab`` resolves to
*this* lab.
"""

from __future__ import annotations

import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = LAB_DIR.parent.parent.parent

# This lab's own modules take priority over any sibling already on the path.
for entry in (str(REPO_ROOT), str(LAB_DIR)):
    if entry in sys.path:
        sys.path.remove(entry)
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(LAB_DIR))

# Evict sibling labs' modules so this lab's versions are imported fresh.
for _name in ("lab", "agent", "mcp_server"):
    sys.modules.pop(_name, None)
