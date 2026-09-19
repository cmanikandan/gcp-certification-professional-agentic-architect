"""Verified Gemini model catalog — the single source of truth for this repository.

Every model ID below was confirmed present in the live Gemini API ``ListModels``
response (``generativelanguage.googleapis.com/v1beta``) on 2026-09-13.

Why this file exists
--------------------
Certification study material is worthless if the model IDs are wrong. Rather than
scattering string literals across 20 labs, every lab imports from here. If Google
ships a new model, you update one file.

Exam relevance
--------------
Objective 3.1 asks you to select "the appropriate language model (LLM vs. SLM,
self-hosted vs. SaaS, OSS vs. proprietary) considering cost, security, and agent
architecture". The :data:`MODEL_CATALOG` below encodes exactly those axes so the
selection logic in ``tracks/03_custom_agents`` can be tested deterministically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# ---------------------------------------------------------------------------
# Default models used across the labs
# ---------------------------------------------------------------------------

#: Balanced default for most agent work: strong tool-calling, 1M context.
DEFAULT_AGENT_MODEL = "gemini-3.7-flash"

#: Cheapest/fastest tier — classification, routing, extraction.
DEFAULT_FAST_MODEL = "gemini-3.5-flash-lite"

#: Deep reasoning / architectural planning.
DEFAULT_REASONING_MODEL = "gemini-3.1-pro-preview"

#: Judge model for evaluation (autorater). Deliberately a *different* model
#: than the one under test, to reduce self-preference bias.
DEFAULT_JUDGE_MODEL = "gemini-3.8-flash"

#: RAG embeddings.
DEFAULT_EMBEDDING_MODEL = "gemini-embedding-2"

#: Self-hosted / open-weights dense option (Model Garden, GKE, or Ollama).
DEFAULT_OSS_MODEL = "gemma-4-31b-it"

#: Self-hosted / open-weights Mixture-of-Experts (MoE) option for lower active-parameter latency on GKE GPUs.
DEFAULT_OSS_MOE_MODEL = "gemma-4-26b-a4b-it"


class Hosting(str, Enum):
    """How the model is served. Exam objective 3.1: self-hosted vs SaaS."""

    SAAS = "saas"
    SELF_HOSTED = "self_hosted"


class Licensing(str, Enum):
    """Exam objective 3.1: OSS vs proprietary."""

    PROPRIETARY = "proprietary"
    OPEN_WEIGHTS = "open_weights"


class Tier(str, Enum):
    """Rough capability/cost tier used by the selection heuristics."""

    LITE = "lite"
    STANDARD = "standard"
    PRO = "pro"


@dataclass(frozen=True)
class ModelProfile:
    """A verified model and the attributes the exam asks you to reason about."""

    model_id: str
    tier: Tier
    hosting: Hosting
    licensing: Licensing
    input_token_limit: int
    output_token_limit: int
    #: ``True`` when the model is a preview / pre-GA release.
    preview: bool = False
    #: Short note on where this model is the *right* answer.
    best_for: str = ""
    modalities: tuple[str, ...] = field(
        default=("text", "image", "audio", "video")
    )


# ---------------------------------------------------------------------------
# Catalog — token limits are the live API's reported values.
# ---------------------------------------------------------------------------

MODEL_CATALOG: dict[str, ModelProfile] = {
    "gemini-3.8-flash": ModelProfile(
        model_id="gemini-3.8-flash",
        tier=Tier.STANDARD,
        hosting=Hosting.SAAS,
        licensing=Licensing.PROPRIETARY,
        input_token_limit=1_048_576,
        output_token_limit=65_536,
        best_for="Newest Flash. Long-horizon autonomous agents and autorating.",
    ),
    "gemini-3.7-flash": ModelProfile(
        model_id="gemini-3.7-flash",
        tier=Tier.STANDARD,
        hosting=Hosting.SAAS,
        licensing=Licensing.PROPRIETARY,
        input_token_limit=1_048_576,
        output_token_limit=65_536,
        best_for="Balanced default for tool-calling agents.",
    ),
    "gemini-3.6-flash": ModelProfile(
        model_id="gemini-3.6-flash",
        tier=Tier.STANDARD,
        hosting=Hosting.SAAS,
        licensing=Licensing.PROPRIETARY,
        input_token_limit=1_048_576,
        output_token_limit=65_536,
        best_for="Prior-generation Flash; pin when you need behavioural stability.",
    ),
    "gemini-3.5-flash": ModelProfile(
        model_id="gemini-3.5-flash",
        tier=Tier.STANDARD,
        hosting=Hosting.SAAS,
        licensing=Licensing.PROPRIETARY,
        input_token_limit=1_048_576,
        output_token_limit=65_536,
        best_for="High-throughput general workloads.",
    ),
    "gemini-3.5-flash-lite": ModelProfile(
        model_id="gemini-3.5-flash-lite",
        tier=Tier.LITE,
        hosting=Hosting.SAAS,
        licensing=Licensing.PROPRIETARY,
        input_token_limit=1_048_576,
        output_token_limit=65_536,
        best_for="Cheapest/fastest: routing, classification, extraction.",
    ),
    "gemini-3.1-flash-lite": ModelProfile(
        model_id="gemini-3.1-flash-lite",
        tier=Tier.LITE,
        hosting=Hosting.SAAS,
        licensing=Licensing.PROPRIETARY,
        input_token_limit=1_048_576,
        output_token_limit=65_536,
        best_for="Low-cost tier with a long context window.",
    ),
    "gemini-3.1-pro-preview": ModelProfile(
        model_id="gemini-3.1-pro-preview",
        tier=Tier.PRO,
        hosting=Hosting.SAAS,
        licensing=Licensing.PROPRIETARY,
        input_token_limit=1_048_576,
        output_token_limit=65_536,
        preview=True,
        best_for="Deepest reasoning: architecture, complex planning, hard debugging.",
    ),
    "gemini-2.5-pro": ModelProfile(
        model_id="gemini-2.5-pro",
        tier=Tier.PRO,
        hosting=Hosting.SAAS,
        licensing=Licensing.PROPRIETARY,
        input_token_limit=1_048_576,
        output_token_limit=65_536,
        best_for="Stable GA Pro tier when preview models are not permitted.",
    ),
    "gemini-2.5-flash": ModelProfile(
        model_id="gemini-2.5-flash",
        tier=Tier.STANDARD,
        hosting=Hosting.SAAS,
        licensing=Licensing.PROPRIETARY,
        input_token_limit=1_048_576,
        output_token_limit=65_536,
        best_for="Stable GA Flash tier.",
    ),
    "gemini-2.5-flash-lite": ModelProfile(
        model_id="gemini-2.5-flash-lite",
        tier=Tier.LITE,
        hosting=Hosting.SAAS,
        licensing=Licensing.PROPRIETARY,
        input_token_limit=1_048_576,
        output_token_limit=65_536,
        best_for="Stable GA low-cost tier.",
    ),
    "gemma-4-31b-it": ModelProfile(
        model_id="gemma-4-31b-it",
        tier=Tier.STANDARD,
        hosting=Hosting.SELF_HOSTED,
        licensing=Licensing.OPEN_WEIGHTS,
        input_token_limit=262_144,
        output_token_limit=32_768,
        best_for=(
            "Air-gapped / data-residency / no-egress. "
            "Self-host on GKE or Model Garden."
        ),
        modalities=("text", "image"),
    ),
    "gemma-4-26b-a4b-it": ModelProfile(
        model_id="gemma-4-26b-a4b-it",
        tier=Tier.STANDARD,
        hosting=Hosting.SELF_HOSTED,
        licensing=Licensing.OPEN_WEIGHTS,
        input_token_limit=262_144,
        output_token_limit=32_768,
        best_for="Open-weights MoE variant; cheaper self-hosted inference.",
        modalities=("text", "image"),
    ),
}


#: Embedding models for RAG (objective 3.2), mapped to their input token limit.
EMBEDDING_MODELS: dict[str, int] = {
    "gemini-embedding-2": 8_192,
    "gemini-embedding-2-preview": 8_192,
    "gemini-embedding-001": 2_048,
}


#: Floating aliases. Convenient in dev, dangerous in prod and in reproducible labs.
FLOATING_ALIASES = (
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-pro-latest",
)


#: Model IDs that appear in older study material but are NOT in the live API.
#: The test suite asserts these never reappear in this repository.
KNOWN_STALE_MODEL_IDS = (
    "text-embedding-005",
    "textembedding-gecko",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemma-2-9b-it",
    "gemma-2-27b-it",
)


def get_profile(model_id: str) -> ModelProfile:
    """Return the verified profile for ``model_id``.

    Raises:
        KeyError: if the model is not in the verified catalog. This is
            deliberate — it stops unverified model IDs entering the labs.
    """
    try:
        return MODEL_CATALOG[model_id]
    except KeyError as exc:
        raise KeyError(
            f"{model_id!r} is not in the verified catalog. "
            f"Known models: {sorted(MODEL_CATALOG)}"
        ) from exc


def select_model(
    *,
    needs_deep_reasoning: bool = False,
    high_volume_simple_task: bool = False,
    data_cannot_leave_premises: bool = False,
    requires_ga_only: bool = False,
) -> tuple[str, str]:
    """Pick a model from the constraints the exam actually asks about.

    The order of checks matters and mirrors real architectural priority: a hard
    residency constraint outranks a cost preference, which outranks a capability
    preference.

    Args:
        needs_deep_reasoning: multi-step planning, architecture, hard debugging.
        high_volume_simple_task: classification, routing, extraction at scale.
        data_cannot_leave_premises: air-gapped or strict data-residency rules.
        requires_ga_only: preview / pre-GA models are not permitted.

    Returns:
        ``(model_id, rationale)``. The rationale is the justification an exam
        answer would need to give.
    """
    if data_cannot_leave_premises:
        return (
            DEFAULT_OSS_MODEL,
            "Data residency forbids a SaaS endpoint, so an open-weights model "
            "self-hosted on GKE or Model Garden is the only compliant option.",
        )

    if needs_deep_reasoning:
        if requires_ga_only:
            return (
                "gemini-2.5-pro",
                "Deep reasoning is required but preview models are not "
                "permitted, so the GA Pro tier is the correct choice.",
            )
        return (
            DEFAULT_REASONING_MODEL,
            "Deep multi-step reasoning justifies the Pro tier's higher cost "
            "and latency.",
        )

    if high_volume_simple_task:
        return (
            DEFAULT_FAST_MODEL,
            "A high-volume, low-complexity task is dominated by cost and "
            "latency, so the Lite tier is correct; the Pro tier would be "
            "over-provisioned.",
        )

    return (
        DEFAULT_AGENT_MODEL,
        "Balanced tool-calling agent workload: the standard Flash tier gives "
        "the best capability-per-dollar without Pro-tier latency.",
    )


def estimate_cost_ratio(model_id: str) -> float:
    """Relative cost weight for teaching trade-offs (Lite = 1.0).

    These are *ordinal* teaching values, not Google price-list figures. Always
    quote live pricing from
    https://cloud.google.com/vertex-ai/generative-ai/pricing
    """
    profile = get_profile(model_id)
    if profile.hosting is Hosting.SELF_HOSTED:
        # No per-token charge; you pay for the GPU/TPU instead.
        return 0.0
    return {Tier.LITE: 1.0, Tier.STANDARD: 4.0, Tier.PRO: 15.0}[profile.tier]
