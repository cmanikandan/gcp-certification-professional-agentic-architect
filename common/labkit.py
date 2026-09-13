"""Console presentation helpers so every lab has a consistent, readable output.

Deliberately dependency-free (no ``rich`` requirement) so labs run anywhere,
including a bare CI container.
"""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass, field

_NO_COLOR = bool(os.getenv("NO_COLOR")) or not sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return text if _NO_COLOR else f"\033[{code}m{text}\033[0m"


def _width(default: int = 78) -> int:
    return min(shutil.get_terminal_size((default, 24)).columns, 100)


def banner(title: str, subtitle: str = "") -> None:
    """Print the lab's opening banner."""
    w = _width()
    print()
    print(_c("36", "=" * w))
    print(_c("1;36", f" {title}"))
    if subtitle:
        print(_c("36", f" {subtitle}"))
    print(_c("36", "=" * w))


def section(title: str) -> None:
    """Print a major section heading inside a lab."""
    w = _width()
    print()
    print(_c("1;34", f"── {title} " + "─" * max(0, w - len(title) - 4)))


def step(number: int | str, text: str) -> None:
    """Print a numbered step."""
    print(f"  {_c('1;32', f'[{number}]')} {text}")


def detail(text: str, indent: int = 6) -> None:
    """Print an indented detail line."""
    print(" " * indent + text)


def warn(text: str) -> None:
    """Print a warning."""
    print(f"  {_c('1;33', '!')} {text}")


def exam_note(text: str) -> None:
    """Highlight a point that is directly examinable."""
    print(f"  {_c('1;35', 'EXAM')} {text}")


def kv_table(rows: dict[str, object], indent: int = 4) -> None:
    """Print aligned key/value pairs."""
    if not rows:
        return
    pad = max(len(str(k)) for k in rows)
    for key, value in rows.items():
        print(" " * indent + f"{str(key).ljust(pad)}  {value}")


def table(headers: list[str], rows: list[list[object]], indent: int = 4) -> None:
    """Print a simple aligned text table."""
    cells = [[str(c) for c in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in cells:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))

    pad = " " * indent
    print(pad + "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers)))
    print(pad + "  ".join("-" * w for w in widths))
    for row in cells:
        print(pad + "  ".join(c.ljust(widths[i]) for i, c in enumerate(row)))


@dataclass
class LabReport:
    """Collects assertions so a lab can end with a verifiable summary.

    Labs use this instead of bare ``print`` for their checks, so the same code
    path proves correctness both interactively and under pytest.
    """

    title: str
    checks: list[tuple[str, bool, str]] = field(default_factory=list)

    def check(self, name: str, passed: bool, detail_text: str = "") -> bool:
        """Record a named check and echo it immediately."""
        self.checks.append((name, bool(passed), detail_text))
        mark = _c("1;32", "PASS") if passed else _c("1;31", "FAIL")
        line = f"  {mark}  {name}"
        if detail_text:
            line += f" — {detail_text}"
        print(line)
        return bool(passed)

    @property
    def passed(self) -> bool:
        return all(ok for _, ok, _ in self.checks)

    def summary(self) -> None:
        """Print the closing summary block."""
        total = len(self.checks)
        ok = sum(1 for _, passed, _ in self.checks if passed)
        section("Result")
        if self.passed:
            print(f"  {_c('1;32', f'All {total} checks passed.')}")
        else:
            print(f"  {_c('1;31', f'{ok}/{total} checks passed.')}")
            for name, passed, detail_text in self.checks:
                if not passed:
                    print(f"    - {name}: {detail_text or 'failed'}")
        print()
