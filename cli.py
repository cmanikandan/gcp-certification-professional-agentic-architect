#!/usr/bin/env python3
"""Interactive runner for the Professional Agentic Architect study labs.

Discovers labs from the filesystem rather than a hard-coded table, so adding a
lab directory is enough to make it appear here.

    python cli.py                 # interactive menu
    python cli.py --list          # list every track and lab
    python cli.py --lab 08        # run one lab offline
    python cli.py --lab 08 --live # run one lab against real Google Cloud
    python cli.py --track 3       # run every lab in a track
    python cli.py --all           # run every lab offline
    python cli.py --test          # run the whole pytest suite
    python cli.py --check         # environment / readiness check
    python cli.py --cleanup       # run every cleanup.sh
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:  # optional convenience only
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - dotenv is not required
    pass

REPO_ROOT = Path(__file__).resolve().parent
TRACKS_DIR = REPO_ROOT / "tracks"

# Weighting comes from the official exam guide; see docs/EXAM_GUIDE.md.
TRACK_WEIGHTS = {
    "01": ("Building agents using low-code tools", 13),
    "02": ("Using coding agents for application development", 17),
    "03": ("Developing custom agents", 33),
    "04": ("Evaluating and deploying agentic workflows", 22),
    "05": ("Securing and governing agentic workflows", 15),
}


# --------------------------------------------------------------------------
# Discovery
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Lab:
    number: str  # "08"
    title: str  # "ADK Fundamentals"
    path: Path
    track_number: str  # "03"

    @property
    def slug(self) -> str:
        return f"{self.track_number}/{self.path.name}"

    @property
    def runner(self) -> Path:
        return self.path / "run_lab.sh"

    @property
    def cleaner(self) -> Path:
        return self.path / "cleanup.sh"


@dataclass(frozen=True)
class Track:
    number: str  # "03"
    title: str
    weight: int
    path: Path
    labs: list[Lab]


def _title_from_readme(readme: Path, fallback: str) -> str:
    """Pull the human title out of the README's H1, e.g. '# Lab 08 - ADK Fundamentals'."""
    if not readme.is_file():
        return fallback
    try:
        first_line = readme.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, IndexError):
        return fallback
    heading = first_line.lstrip("#").strip()
    # Strip the "Lab 08 - " / "Track 3 - " prefix; we display the number separately.
    match = re.match(r"^(?:Lab|Track)\s+\d+\s*[-—:]\s*(.+)$", heading)
    return match.group(1).strip() if match else heading or fallback


def _prettify(dirname: str) -> str:
    """'lab_08_adk_fundamentals' -> 'Adk Fundamentals'."""
    parts = dirname.split("_")
    if parts and parts[0] in {"lab", "track"}:
        parts = parts[2:] if len(parts) > 1 and parts[1].isdigit() else parts[1:]
    return " ".join(parts).title()


def discover_tracks() -> list[Track]:
    if not TRACKS_DIR.is_dir():
        return []

    tracks: list[Track] = []
    for track_dir in sorted(p for p in TRACKS_DIR.iterdir() if p.is_dir()):
        track_number = track_dir.name.split("_")[0]
        default_title, weight = TRACK_WEIGHTS.get(track_number, (_prettify(track_dir.name), 0))
        title = _title_from_readme(track_dir / "README.md", default_title)

        labs: list[Lab] = []
        for lab_dir in sorted(p for p in track_dir.iterdir() if p.is_dir() and p.name.startswith("lab_")):
            lab_number = lab_dir.name.split("_")[1]
            labs.append(
                Lab(
                    number=lab_number,
                    title=_title_from_readme(lab_dir / "README.md", _prettify(lab_dir.name)),
                    path=lab_dir,
                    track_number=track_number,
                )
            )

        tracks.append(Track(track_number, title, weight, track_dir, labs))
    return tracks


def all_labs(tracks: list[Track]) -> list[Lab]:
    return [lab for track in tracks for lab in track.labs]


def find_lab(tracks: list[Track], wanted: str) -> Lab | None:
    normalised = wanted.strip().lstrip("0") or "0"
    for lab in all_labs(tracks):
        if lab.number.lstrip("0") == normalised:
            return lab
    return None


# --------------------------------------------------------------------------
# Presentation
# --------------------------------------------------------------------------

BOLD, DIM, RESET = "\033[1m", "\033[2m", "\033[0m"


def _supports_colour() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def style(text: str, code: str) -> str:
    return f"{code}{text}{RESET}" if _supports_colour() else text


def print_banner() -> None:
    line = "=" * 78
    print(f"\n{line}")
    print(style("  Google Cloud Professional Agentic Architect — study lab runner", BOLD))
    print("  Every lab runs offline and free by default. Add --live to hit real GCP.")
    print(f"{line}\n")


def print_catalogue(tracks: list[Track]) -> None:
    for track in tracks:
        header = f"Track {track.number} — {track.title}"
        weight = f"~{track.weight}% of the exam" if track.weight else ""
        print(f"\n{style(header, BOLD)}  {style(weight, DIM)}")
        if not track.labs:
            print("    (no labs yet)")
        for lab in track.labs:
            status = "" if lab.runner.is_file() else style("  [no run_lab.sh]", DIM)
            print(f"    {style(lab.number, BOLD)}  {lab.title}{status}")
    print()


# --------------------------------------------------------------------------
# Execution
# --------------------------------------------------------------------------


def _run(cmd: list[str], cwd: Path = REPO_ROOT) -> int:
    print(f"\n{style('$', DIM)} {' '.join(str(c) for c in cmd)}")
    try:
        return subprocess.call(cmd, cwd=cwd)
    except FileNotFoundError:
        print(f"  Not found: {cmd[0]}")
        return 127
    except KeyboardInterrupt:
        print("\n  Interrupted.")
        return 130


def run_lab(lab: Lab, live: bool = False) -> int:
    print(f"\n{'-' * 78}")
    print(style(f"Lab {lab.number} — {lab.title}", BOLD))
    print(f"{'-' * 78}")

    if not lab.runner.is_file():
        print(f"  {lab.runner.relative_to(REPO_ROOT)} is missing; skipping.")
        return 1

    cmd = [str(lab.runner)]
    if live:
        cmd.append("--live")
    return _run(cmd)


def run_many(labs: list[Lab], live: bool = False) -> int:
    results: list[tuple[Lab, int]] = [(lab, run_lab(lab, live)) for lab in labs]

    print(f"\n{'=' * 78}")
    print(style("  Summary", BOLD))
    print(f"{'=' * 78}")
    failed = 0
    for lab, code in results:
        mark = "PASS" if code == 0 else "FAIL"
        if code != 0:
            failed += 1
        print(f"  {mark}  Lab {lab.number} — {lab.title}")
    print(f"\n  {len(results) - failed}/{len(results)} labs passed.\n")
    return 1 if failed else 0


def run_tests() -> int:
    return _run([sys.executable, "-m", "pytest", "tracks/", "tests/", "-q"])


def run_cleanup(labs: list[Lab]) -> int:
    worst = 0
    for lab in labs:
        if lab.cleaner.is_file():
            worst = max(worst, _run([str(lab.cleaner)]))
    print("\n  Cleanup complete.\n")
    return worst


# --------------------------------------------------------------------------
# Environment check
# --------------------------------------------------------------------------


def check_environment() -> int:
    print_banner()
    print(style("  Environment check", BOLD))
    print(f"  {'-' * 40}")

    ok = True

    print(f"  Python              {sys.version.split()[0]}")
    if sys.version_info < (3, 10):
        print("    ! Python 3.10+ is required.")
        ok = False

    for package, label in [
        ("google.adk", "google-adk"),
        ("google.genai", "google-genai"),
        ("pytest", "pytest"),
    ]:
        try:
            __import__(package)
            print(f"  {label:<20}installed")
        except ImportError:
            print(f"  {label:<20}MISSING — pip install -r requirements.txt")
            ok = False

    print(f"\n  {style('Live-path configuration (optional)', BOLD)}")
    print(f"  {'-' * 40}")
    for var in ("GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION", "GOOGLE_API_KEY"):
        value = os.environ.get(var)
        shown = "set" if value else "not set — labs will run offline"
        print(f"  {var:<26}{shown}")

    tracks = discover_tracks()
    labs = all_labs(tracks)
    runnable = sum(1 for lab in labs if lab.runner.is_file())
    print(f"\n  Labs discovered     {len(labs)} ({runnable} runnable)")

    print("\n  " + ("Ready." if ok else "Not ready — fix the items marked above.") + "\n")
    return 0 if ok else 1


# --------------------------------------------------------------------------
# Interactive menu
# --------------------------------------------------------------------------


def interactive_menu(tracks: list[Track]) -> int:
    while True:
        print_banner()
        print_catalogue(tracks)
        print("  Enter a lab number (e.g. 08), or:")
        print("    t<n>  run a whole track, e.g. t3")
        print("    a     run every lab offline")
        print("    p     run the pytest suite")
        print("    e     environment check")
        print("    c     run every cleanup script")
        print("    q     quit")

        try:
            choice = input("\n  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if choice in {"q", "quit", "exit"}:
            return 0
        if choice == "a":
            run_many(all_labs(tracks))
        elif choice == "p":
            run_tests()
        elif choice == "e":
            check_environment()
        elif choice == "c":
            run_cleanup(all_labs(tracks))
        elif choice.startswith("t") and choice[1:].isdigit():
            number = choice[1:].zfill(2)
            match = next((t for t in tracks if t.number == number), None)
            if match:
                run_many(match.labs)
            else:
                print(f"  No track {number}.")
        elif choice.isdigit():
            lab = find_lab(tracks, choice)
            if lab:
                run_lab(lab)
            else:
                print(f"  No lab {choice}.")
        else:
            print("  Unrecognised option.")

        try:
            input("\n  Press Enter to continue...")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0


# --------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Professional Agentic Architect study labs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--list", action="store_true", help="list every track and lab")
    parser.add_argument("--lab", metavar="NN", help="run a single lab by number")
    parser.add_argument("--track", metavar="N", help="run every lab in a track")
    parser.add_argument("--all", action="store_true", help="run every lab")
    parser.add_argument("--test", action="store_true", help="run the pytest suite")
    parser.add_argument("--check", action="store_true", help="environment check")
    parser.add_argument("--cleanup", action="store_true", help="run every cleanup script")
    parser.add_argument("--live", action="store_true", help="use the live Google Cloud path")
    args = parser.parse_args()

    tracks = discover_tracks()
    if not tracks:
        print(f"No tracks found under {TRACKS_DIR}.")
        return 1

    if args.check:
        return check_environment()
    if args.list:
        print_banner()
        print_catalogue(tracks)
        return 0
    if args.test:
        return run_tests()
    if args.cleanup:
        return run_cleanup(all_labs(tracks))
    if args.lab:
        lab = find_lab(tracks, args.lab)
        if not lab:
            print(f"No lab {args.lab}. Try --list.")
            return 1
        return run_lab(lab, args.live)
    if args.track:
        number = args.track.zfill(2)
        match = next((t for t in tracks if t.number == number), None)
        if not match:
            print(f"No track {number}. Try --list.")
            return 1
        return run_many(match.labs, args.live)
    if args.all:
        return run_many(all_labs(tracks), args.live)

    return interactive_menu(tracks)


if __name__ == "__main__":
    sys.exit(main())
