"""Lab configuration and the offline/live safety gate.

Design rule for this repository
-------------------------------
**Every lab runs offline by default.** A lab may only touch Google Cloud (and
therefore spend money) when the learner passes ``--live`` *and* the required
environment variables are present. This makes the whole suite safe to run in CI
and safe to run on a laptop at 2am before the exam.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv() -> None:
    """Load ``.env`` from the repo root if python-dotenv is available.

    Falls back to a minimal parser so the labs work even with no extra deps.
    """
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path)
        return
    except ImportError:
        pass

    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class LabConfig:
    """Resolved configuration for a single lab run."""

    live: bool
    project_id: str
    location: str
    gemini_api_key: str
    staging_bucket: str

    @property
    def has_project(self) -> bool:
        return bool(self.project_id)

    @property
    def has_api_key(self) -> bool:
        return bool(self.gemini_api_key)

    def missing_for_live(self) -> list[str]:
        """Return the env vars that are required for live mode but absent."""
        missing = []
        if not self.project_id:
            missing.append("GOOGLE_CLOUD_PROJECT")
        if not self.gemini_api_key:
            missing.append("GOOGLE_API_KEY (or GEMINI_API_KEY)")
        return missing


def load_config(argv: list[str] | None = None) -> LabConfig:
    """Parse the standard lab flags and resolve environment configuration.

    Every lab exposes the same interface::

        python lab.py            # offline, free, deterministic
        python lab.py --live     # real Google Cloud calls, costs money
    """
    _load_dotenv()

    parser = argparse.ArgumentParser(
        description=(
            "Runs offline and free by default. Pass --live to make real "
            "Google Cloud API calls (this may incur charges)."
        )
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Opt in to real, potentially billable Google Cloud API calls.",
    )
    args, _unknown = parser.parse_known_args(argv)

    return LabConfig(
        live=args.live,
        project_id=(
            os.getenv("GOOGLE_CLOUD_PROJECT")
            or os.getenv("GCP_PROJECT_ID")
            or ""
        ),
        location=(
            os.getenv("GOOGLE_CLOUD_LOCATION")
            or os.getenv("GCP_REGION")
            or "us-central1"
        ),
        gemini_api_key=(
            os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
        ),
        staging_bucket=os.getenv("GOOGLE_CLOUD_STAGING_BUCKET", ""),
    )


def require_live(config: LabConfig) -> bool:
    """Return ``True`` when the lab may proceed with live cloud calls.

    Prints an actionable explanation and returns ``False`` otherwise, so the
    caller can fall back to the offline path instead of crashing.
    """
    if not config.live:
        return False

    missing = config.missing_for_live()
    if missing:
        print(
            "\n  --live was requested but the environment is incomplete.\n"
            f"  Missing: {', '.join(missing)}\n"
            "  Copy .env.example to .env and fill it in, then retry.\n"
            "  Continuing in OFFLINE mode.\n"
        )
        return False
    return True
