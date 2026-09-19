"""Enforce the lab authoring contract.

Eighteen labs written by different hands still have to feel like one course, and
a learner has to be able to open any one of them cold. ``docs/LAB_AUTHORING_CONTRACT.md``
describes that contract in prose; this file makes it fail the build.
"""

from __future__ import annotations

import os
import re
import stat
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKS_DIR = REPO_ROOT / "tracks"

# The eleven README sections, in order. Matched on the numbered heading prefix so
# authors keep the shared shape without being forced into identical wording.
REQUIRED_SECTION_PREFIXES = [
    "1.",  # Exam objectives covered
    "2.",  # Explain it simply
    "3.",  # How it works
    "4.",  # The decision that matters
    "5.",  # Hands-on A - offline
    "6.",  # Hands-on B - live
    "7.",  # Verify it worked
    "8.",  # Troubleshooting
    "9.",  # Clean up
    "10.",  # Exam traps
    "11.",  # Check yourself
]

REQUIRED_FILES = ["README.md", "lab.py", "run_lab.sh", "cleanup.sh"]

# Every lab is deep-linkable, so every lab has to point back at the real thing.
OFFICIAL_CERT_URL = "https://cloud.google.com/learn/certification/agentic-architect"


def _lab_dirs() -> list[Path]:
    if not TRACKS_DIR.is_dir():
        return []
    return sorted(
        lab
        for track in TRACKS_DIR.iterdir()
        if track.is_dir()
        for lab in track.iterdir()
        if lab.is_dir() and lab.name.startswith("lab_")
    )


LAB_DIRS = _lab_dirs()
LAB_IDS = [f"{lab.parent.name}/{lab.name}" for lab in LAB_DIRS]


def test_all_twenty_labs_are_present() -> None:
    assert len(LAB_DIRS) == 20, f"expected 20 labs, found {len(LAB_DIRS)}: {LAB_IDS}"

    numbers = sorted(int(lab.name.split("_")[1]) for lab in LAB_DIRS)
    assert numbers == list(range(1, 21)), f"lab numbering has gaps or duplicates: {numbers}"


@pytest.mark.parametrize("lab", LAB_DIRS, ids=LAB_IDS)
def test_lab_has_every_required_file(lab: Path) -> None:
    missing = [name for name in REQUIRED_FILES if not (lab / name).is_file()]
    assert not missing, f"{lab.name} is missing: {missing}"

    tests_dir = lab / "tests"
    assert tests_dir.is_dir(), f"{lab.name} has no tests/ directory"

    test_files = list(tests_dir.glob("test_*.py"))
    assert test_files, f"{lab.name}/tests/ contains no test_*.py"


@pytest.mark.parametrize("lab", LAB_DIRS, ids=LAB_IDS)
def test_lab_scripts_are_executable(lab: Path) -> None:
    for name in ("run_lab.sh", "cleanup.sh"):
        script = lab / name
        if not script.is_file():
            pytest.skip(f"{name} missing; covered by test_lab_has_every_required_file")
        mode = script.stat().st_mode
        assert mode & stat.S_IXUSR, f"{lab.name}/{name} is not executable (chmod +x)"


@pytest.mark.parametrize("lab", LAB_DIRS, ids=LAB_IDS)
def test_readme_follows_the_eleven_section_skeleton(lab: Path) -> None:
    readme = lab / "README.md"
    if not readme.is_file():
        pytest.skip("README missing; covered by test_lab_has_every_required_file")

    headings = [
        line.lstrip("#").strip()
        for line in readme.read_text(encoding="utf-8").splitlines()
        if line.startswith("## ")
    ]

    missing = [
        prefix
        for prefix in REQUIRED_SECTION_PREFIXES
        if not any(h.startswith(prefix) for h in headings)
    ]
    assert not missing, (
        f"{lab.name}/README.md is missing sections {missing}. "
        f"Found headings: {headings}"
    )


@pytest.mark.parametrize("lab", LAB_DIRS, ids=LAB_IDS)
def test_readme_contains_a_diagram(lab: Path) -> None:
    """Section 3 must visualise the mechanics; the whole course promises diagrams."""
    readme = lab / "README.md"
    if not readme.is_file():
        pytest.skip("README missing; covered by test_lab_has_every_required_file")

    assert "```mermaid" in readme.read_text(encoding="utf-8"), (
        f"{lab.name}/README.md has no mermaid diagram"
    )


@pytest.mark.parametrize("lab", LAB_DIRS, ids=LAB_IDS)
def test_readme_states_objectives_time_and_cost(lab: Path) -> None:
    readme = lab / "README.md"
    if not readme.is_file():
        pytest.skip("README missing; covered by test_lab_has_every_required_file")

    text = readme.read_text(encoding="utf-8")
    for marker in ("Exam section:", "Objectives covered:", "Time:", "Cost:"):
        assert marker in text, f"{lab.name}/README.md does not state '{marker}'"


@pytest.mark.parametrize("lab", LAB_DIRS, ids=LAB_IDS)
def test_readme_points_at_the_official_certification_page(lab: Path) -> None:
    """Labs are read standalone and deep-linked, so each must disclaim on its own.

    Nobody should be able to land on a lab from a search result and mistake this
    personal repository for official Google Cloud material.
    """
    readme = lab / "README.md"
    if not readme.is_file():
        pytest.skip("README missing; covered by test_lab_has_every_required_file")

    text = readme.read_text(encoding="utf-8")
    assert "not affiliated with Google Cloud" in text, (
        f"{lab.name}/README.md does not disclaim affiliation"
    )
    assert OFFICIAL_CERT_URL in text, (
        f"{lab.name}/README.md does not link {OFFICIAL_CERT_URL}"
    )


@pytest.mark.parametrize("lab", LAB_DIRS, ids=LAB_IDS)
def test_labs_are_independent(lab: Path) -> None:
    """A learner must be able to open any lab cold, so no back-references."""
    readme = lab / "README.md"
    if not readme.is_file():
        pytest.skip("README missing; covered by test_lab_has_every_required_file")

    banned = re.compile(
        r"\b(?:as (?:you saw|we saw|shown) in (?:the )?(?:previous|last|earlier) lab"
        r"|in the previous lab"
        r"|continuing from lab)\b",
        re.IGNORECASE,
    )
    hits = [
        f"line {n}: {line.strip()}"
        for n, line in enumerate(readme.read_text(encoding="utf-8").splitlines(), 1)
        if banned.search(line)
    ]
    assert not hits, (
        f"{lab.name}/README.md depends on another lab; each lab must stand alone.\n  "
        + "\n  ".join(hits)
    )


@pytest.mark.parametrize("lab", LAB_DIRS, ids=LAB_IDS)
def test_lab_code_does_not_hard_code_model_ids(lab: Path) -> None:
    """Model IDs belong in common.models so one edit updates the whole course."""
    hard_coded = re.compile(r"""["'](?:gemini|gemma|text-embedding)[\w.-]*["']""")

    offenders: list[str] = []
    for source in lab.rglob("*.py"):
        if "__pycache__" in source.parts:
            continue
        for lineno, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            # Comments and docstring prose may name a model when explaining it.
            if stripped.startswith("#"):
                continue
            if hard_coded.search(line):
                offenders.append(
                    f"{source.relative_to(REPO_ROOT)}:{lineno}: {stripped[:100]}"
                )

    assert not offenders, (
        "Hard-coded model IDs found. Import a constant from common.models instead "
        "(DEFAULT_AGENT_MODEL, DEFAULT_FAST_MODEL, DEFAULT_REASONING_MODEL, "
        "DEFAULT_JUDGE_MODEL, DEFAULT_EMBEDDING_MODEL, DEFAULT_OSS_MODEL).\n  "
        + "\n  ".join(offenders)
    )


@pytest.mark.parametrize("lab", LAB_DIRS, ids=LAB_IDS)
def test_lab_respects_the_offline_contract(lab: Path) -> None:
    """`python lab.py` with no credentials must not attempt a live call."""
    source = lab / "lab.py"
    if not source.is_file():
        pytest.skip("lab.py missing; covered by test_lab_has_every_required_file")

    text = source.read_text(encoding="utf-8")
    assert "require_live" in text, (
        f"{lab.name}/lab.py does not use require_live(); it cannot be honouring "
        "the offline-by-default contract"
    )


def test_no_google_credentials_present_during_the_suite() -> None:
    """CI must prove the labs pass unauthenticated, so fail loudly if they leak in."""
    if os.environ.get("CI"):
        leaked = [
            var
            for var in ("GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_API_KEY", "GEMINI_API_KEY")
            if os.environ.get(var)
        ]
        assert not leaked, f"credentials present in CI, offline contract unproven: {leaked}"
