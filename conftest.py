"""Repo-wide pytest configuration.

Two things every lab depends on:

1. The repository root must be importable, so ``from common import ...`` works
   no matter which directory pytest was invoked from.
2. Labs are deliberately self-contained, which means eighteen of them each have
   a module called ``lab`` and several have one called ``agent``. Python caches
   modules by name, so without intervention the first ``lab`` imported would be
   silently reused for every other lab in the same session. Each lab's
   ``tests/conftest.py`` evicts those names; this file makes the repo root
   available to all of them.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
