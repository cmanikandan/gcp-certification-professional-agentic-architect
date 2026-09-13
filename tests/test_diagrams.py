"""Catch mermaid diagrams that will not render on GitHub.

A diagram that fails to parse renders as a red "Unable to render rich display"
box, which is worse than having no diagram at all: the reader loses the
explanation *and* trusts the page less.

The authoritative check is ``scripts/validate_mermaid.mjs``, which runs the real
mermaid parser. That needs node and two npm packages, so it lives in its own CI
job. These tests are the dependency-free first line of defence: they catch the
mistakes that actually happen, instantly, in the normal test run.

The dominant failure mode by far is an unquoted bracket inside a label.
``A[End User] -->|1. Request (User Token)| B`` fails because mermaid reads the
``(`` as the start of a node shape, not as a literal character.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    ".venv-adk",
    "node_modules",
    "scratch",
    "assets",
    "__pycache__",
}

# Diagram types used in this repo. A typo in the header silently produces an
# unrenderable block, so pin the allowed set.
KNOWN_DIAGRAM_TYPES = (
    "graph",
    "flowchart",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "journey",
    "gantt",
    "pie",
    "mindmap",
    "timeline",
    "quadrantChart",
    "gitGraph",
    "block-beta",
)

FLOWCHART_TYPES = ("graph", "flowchart")

# Characters that terminate a label unless the label is quoted.
RISKY_IN_LABEL = re.compile(r"[(){}\[\]]")

# An edge label: the text between a pair of pipes, as in  A -->|label| B
EDGE_LABEL = re.compile(r"\|([^|]*)\|")


class Block:
    def __init__(self, file: Path, line: int, source: str):
        self.file = file
        self.line = line
        self.source = source

    @property
    def where(self) -> str:
        return f"{self.file.relative_to(REPO_ROOT)}:{self.line}"

    @property
    def header(self) -> str:
        for raw in self.source.splitlines():
            if raw.strip():
                return raw.strip()
        return ""

    @property
    def is_flowchart(self) -> bool:
        return self.header.split()[0] in FLOWCHART_TYPES if self.header else False

    def __repr__(self) -> str:  # shows up in pytest ids
        return self.where


def _iter_markdown() -> list[Path]:
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*.md"):
        if any(part in EXCLUDED_DIRS for part in path.relative_to(REPO_ROOT).parts):
            continue
        files.append(path)
    return sorted(files)


def _extract_blocks() -> tuple[list[Block], list[str]]:
    blocks: list[Block] = []
    unterminated: list[str] = []

    for path in _iter_markdown():
        inside = False
        start = 0
        buffer: list[str] = []

        for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = raw.strip()
            if not inside and stripped == "```mermaid":
                inside, start, buffer = True, lineno, []
            elif inside and stripped == "```":
                inside = False
                blocks.append(Block(path, start, "\n".join(buffer)))
            elif inside:
                buffer.append(raw)

        if inside:
            unterminated.append(f"{path.relative_to(REPO_ROOT)}:{start}")

    return blocks, unterminated


BLOCKS, UNTERMINATED = _extract_blocks()
BLOCK_IDS = [b.where for b in BLOCKS]


def test_every_mermaid_fence_is_closed() -> None:
    assert not UNTERMINATED, f"unterminated ```mermaid fences: {UNTERMINATED}"


def test_repo_actually_has_diagrams() -> None:
    """Guards against the extractor silently breaking and vacuously passing."""
    assert len(BLOCKS) >= 20, f"only found {len(BLOCKS)} mermaid blocks"


@pytest.mark.parametrize("block", BLOCKS, ids=BLOCK_IDS)
def test_block_declares_a_known_diagram_type(block: Block) -> None:
    assert block.header, f"{block.where}: empty mermaid block"
    first_word = block.header.split()[0]
    assert first_word in KNOWN_DIAGRAM_TYPES, (
        f"{block.where}: unrecognised diagram type {first_word!r}. "
        f"Known types: {', '.join(KNOWN_DIAGRAM_TYPES)}"
    )


def _is_quoted(text: str) -> bool:
    return (text.startswith('"') and text.endswith('"')) or (
        text.startswith("'") and text.endswith("'")
    )


def edge_label_offenders(source: str) -> list[str]:
    """Lines whose edge label holds an unquoted bracket."""
    offenders: list[str] = []
    for raw in source.splitlines():
        line = raw.strip()
        if line.startswith("%%") or "|" not in line:
            continue
        for label in EDGE_LABEL.findall(line):
            text = label.strip()
            if text and not _is_quoted(text) and RISKY_IN_LABEL.search(text):
                offenders.append(line)
                break
    return offenders


# Node shapes, ordered most specific first. Each is validated and then removed
# from the working line, so that a cylinder `X[("label")]` is not subsequently
# re-matched by the broader rectangle pattern and wrongly reported.
NODE_SHAPES = (
    re.compile(r"[\w-]+\[\((?P<label>.*?)\)\]"),  # cylinder  id[(label)]
    re.compile(r"[\w-]+\(\[(?P<label>.*?)\]\)"),  # stadium   id([label])
    re.compile(r"[\w-]+\(\((?P<label>.*?)\)\)"),  # circle    id((label))
    re.compile(r"[\w-]+\{\{(?P<label>.*?)\}\}"),  # hexagon   id{{label}}
    re.compile(r"[\w-]+\[/(?P<label>.*?)/\]"),  # parallelogram
    re.compile(r"[\w-]+\[\\(?P<label>.*?)\\\]"),  # parallelogram alt
    re.compile(r"[\w-]+\((?P<label>[^()]*?)\)"),  # rounded   id(label)
    re.compile(r"[\w-]+\[(?P<label>[^\[\]]*?)\]"),  # rect      id[label]
    re.compile(r"[\w-]+\{(?P<label>[^{}]*?)\}"),  # rhombus   id{label}
)

SKIP_PREFIXES = ("%%", "style ", "class ", "linkStyle ", "classDef ")


def node_label_offenders(source: str) -> list[str]:
    """Lines whose node label holds an unquoted bracket."""
    offenders: list[str] = []
    for raw in source.splitlines():
        line = raw.strip()
        if any(line.startswith(prefix) for prefix in SKIP_PREFIXES):
            continue

        # Edge labels are checked separately; drop them so their contents are
        # not mistaken for node labels.
        working = EDGE_LABEL.sub("||", line)

        flagged = False

        def check(match: re.Match[str]) -> str:
            nonlocal flagged
            text = match.group("label").strip()
            if text and not _is_quoted(text) and RISKY_IN_LABEL.search(text):
                flagged = True
            return ""  # consume, so broader patterns cannot re-match it

        for pattern in NODE_SHAPES:
            working = pattern.sub(check, working)

        if flagged:
            offenders.append(line)
    return offenders


@pytest.mark.parametrize("block", BLOCKS, ids=BLOCK_IDS)
def test_edge_labels_with_brackets_are_quoted(block: Block) -> None:
    """`-->|1. Request (token)| B` is a parse error; quoting the label fixes it."""
    if not block.is_flowchart:
        return

    offenders = edge_label_offenders(block.source)
    assert not offenders, (
        f"{block.where}: edge label contains an unquoted bracket, which mermaid "
        f'reads as a node shape. Wrap it in quotes: -->|"1. Step (detail)"| B\n  '
        + "\n  ".join(offenders)
    )


@pytest.mark.parametrize("block", BLOCKS, ids=BLOCK_IDS)
def test_node_labels_with_parentheses_are_quoted(block: Block) -> None:
    """`A[Label (detail)]` is a parse error; `A["Label (detail)"]` is not."""
    if not block.is_flowchart:
        return

    offenders = node_label_offenders(block.source)
    assert not offenders, (
        f"{block.where}: node label contains an unquoted bracket. "
        f'Wrap it in quotes: A["Label (detail)"]\n  ' + "\n  ".join(offenders)
    )


# --------------------------------------------------------------------------
# Self-tests. A linter that cannot fail is not a linter, so pin both directions
# against the diagram that actually broke on GitHub.
# --------------------------------------------------------------------------

REGRESSION_BAD = """graph LR
    User[End User] -->|1. Request (User Token)| Gateway[Agent Gateway]
"""

REGRESSION_FIXED = """graph LR
    User["End User"] -->|"1. Request (User Token)"| Gateway["Agent Gateway"]
"""


def test_linter_catches_the_edge_label_that_broke_github() -> None:
    assert edge_label_offenders(REGRESSION_BAD), (
        "the linter no longer catches an unquoted bracket in an edge label"
    )


def test_linter_accepts_the_fixed_version() -> None:
    assert not edge_label_offenders(REGRESSION_FIXED)
    assert not node_label_offenders(REGRESSION_FIXED)


def test_linter_catches_unquoted_node_label() -> None:
    assert node_label_offenders("graph TD\n    A[Model (Pro tier)] --> B\n")


@pytest.mark.parametrize(
    "line",
    [
        'A["Label (detail)"] --> B',
        "A[Plain label] --> B",
        'DB[("Enterprise data")] --> B',
        'S(["Stadium node"]) --> B',
        'H{{"Hexagon (special)"}} --> B',
        'A -->|"1. Step (detail)"| B',
        "A -->|plain label| B",
        "style A fill:#fff,stroke:#000",
    ],
)
def test_linter_does_not_flag_valid_shapes(line: str) -> None:
    source = f"graph TD\n    {line}\n"
    assert not node_label_offenders(source), f"false positive on: {line}"
    assert not edge_label_offenders(source), f"false positive on: {line}"


@pytest.mark.parametrize("block", BLOCKS, ids=BLOCK_IDS)
def test_no_self_referential_edges(block: Block) -> None:
    """`Gateway --> Gateway` renders as an unreadable loop; use a distinct node."""
    if not block.is_flowchart:
        return

    edge = re.compile(r"^([\w-]+)\s*(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\})?\s*-->(?:\|[^|]*\|)?\s*([\w-]+)")
    offenders = [
        f"line {block.line + offset}: {line}"
        for offset, raw in enumerate(block.source.splitlines(), 1)
        if (line := raw.strip())
        and (m := edge.match(line))
        and m.group(1) == m.group(2)
    ]

    assert not offenders, (
        f"{block.where}: an edge points a node at itself.\n  " + "\n  ".join(offenders)
    )
