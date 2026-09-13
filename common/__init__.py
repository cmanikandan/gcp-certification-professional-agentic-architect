"""Shared utilities for every lab in this repository.

Importing from ``common`` keeps the labs focused on the exam concept they teach
rather than on boilerplate.
"""

from common.config import LabConfig, load_config, require_live
from common.labkit import (
    LabReport,
    banner,
    exam_note,
    kv_table,
    section,
    step,
    warn,
)
from common.models import (
    DEFAULT_AGENT_MODEL,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_FAST_MODEL,
    DEFAULT_JUDGE_MODEL,
    DEFAULT_OSS_MODEL,
    DEFAULT_REASONING_MODEL,
    EMBEDDING_MODELS,
    MODEL_CATALOG,
    ModelProfile,
    get_profile,
    select_model,
)

__all__ = [
    "DEFAULT_AGENT_MODEL",
    "DEFAULT_EMBEDDING_MODEL",
    "DEFAULT_FAST_MODEL",
    "DEFAULT_JUDGE_MODEL",
    "DEFAULT_OSS_MODEL",
    "DEFAULT_REASONING_MODEL",
    "EMBEDDING_MODELS",
    "MODEL_CATALOG",
    "LabConfig",
    "LabReport",
    "ModelProfile",
    "banner",
    "exam_note",
    "get_profile",
    "kv_table",
    "load_config",
    "require_live",
    "section",
    "select_model",
    "step",
    "warn",
]
