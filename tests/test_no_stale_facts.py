"""Guard against stale facts creeping back into the repository.

Certification material rots quickly, and a retired model ID is worse than no
model ID at all: a learner will copy it, it will 404, and they will not know
whether the concept or the string was wrong.

The single source of truth for what is current is ``docs/VERIFIED_FACTS.md``,
which was built by querying the live Gemini ListModels API and by introspecting
an actual ADK installation. These tests make that document enforceable.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from common.models import KNOWN_STALE_MODEL_IDS, MODEL_CATALOG, EMBEDDING_MODELS

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories that are not ours to police.
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    ".venv-adk",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".github",
    "assets",
}

SCANNED_SUFFIXES = {".py", ".md", ".sh", ".yml", ".yaml", ".json", ".txt"}

# The one file allowed to name retired models: it exists to list them.
ALLOWED_STALE_MENTIONS = {
    REPO_ROOT / "common" / "models.py",
    REPO_ROOT / "docs" / "VERIFIED_FACTS.md",
    REPO_ROOT / "tests" / "test_no_stale_facts.py",
}


def _iter_repo_files() -> list[Path]:
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in SCANNED_SUFFIXES:
            continue
        if any(part in EXCLUDED_DIRS for part in path.relative_to(REPO_ROOT).parts):
            continue
        files.append(path)
    return files


REPO_FILES = _iter_repo_files()

# A line may name a retired model if its whole point is that the model is retired.
# "text-embedding-005 is stale, use gemini-embedding-2" is good teaching; silently
# passing it to a constructor is the bug we are hunting.
TEACHING_EXEMPTION = re.compile(
    r"\b(?:stale|retired|deprecated|no longer|superseded|obsolete|do not use|don't use|reappears)\b",
    re.IGNORECASE,
)


def _offenders(pattern: re.Pattern[str], allowed: set[Path] | None = None) -> list[str]:
    allowed = allowed or set()
    hits: list[str] = []
    for path in REPO_FILES:
        if path in allowed:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line) and not TEACHING_EXEMPTION.search(line):
                rel = path.relative_to(REPO_ROOT)
                hits.append(f"{rel}:{lineno}: {line.strip()[:120]}")
    return hits


def test_no_retired_model_ids_anywhere() -> None:
    """No lab, doc or script may reference a model that no longer exists."""
    assert KNOWN_STALE_MODEL_IDS, "the stale-model list should not be empty"

    pattern = re.compile("|".join(re.escape(m) for m in KNOWN_STALE_MODEL_IDS))
    offenders = _offenders(pattern, allowed=ALLOWED_STALE_MENTIONS)

    assert not offenders, (
        "Retired model IDs found. These models are no longer served; replace them "
        "with a constant from common.models (e.g. DEFAULT_AGENT_MODEL).\n  "
        + "\n  ".join(offenders)
    )


def test_no_references_to_the_retired_modules_tree() -> None:
    """The repo was restructured into tracks/; no path may still point at modules/."""
    pattern = re.compile(r"(?<![\w/.-])modules/\d\d_")
    offenders = _offenders(pattern)

    assert not offenders, (
        "References to the old modules/ layout remain. The labs now live under "
        "tracks/<NN_track>/lab_<NN>_<topic>/.\n  " + "\n  ".join(offenders)
    )


@pytest.mark.parametrize("model_id", sorted(MODEL_CATALOG))
def test_catalog_models_are_not_also_marked_stale(model_id: str) -> None:
    """The catalog and the stale list must not disagree with each other."""
    assert model_id not in KNOWN_STALE_MODEL_IDS


def test_embedding_models_are_current() -> None:
    """The retired text-embedding-005 must not be the configured default."""
    assert EMBEDDING_MODELS, "at least one embedding model must be catalogued"
    assert "text-embedding-005" not in EMBEDDING_MODELS
    assert "textembedding-gecko" not in EMBEDDING_MODELS


def test_verified_facts_document_exists_and_is_substantial() -> None:
    """Every factual claim in the repo is supposed to trace back to this file."""
    facts = REPO_ROOT / "docs" / "VERIFIED_FACTS.md"
    assert facts.is_file(), "docs/VERIFIED_FACTS.md is the authority document; it must exist"
    assert len(facts.read_text(encoding="utf-8").splitlines()) > 100
