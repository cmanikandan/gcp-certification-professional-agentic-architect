import pytest
import sys
import pathlib

# Add the lab directory to the path so we can import 'lab'
lab_dir = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(lab_dir))

import lab
from common.models import MODEL_CATALOG

def test_uses_only_verified_models():
    """Ensure the lab uses models that exist in the verified catalog."""
    assert lab.DEFAULT_AGENT_MODEL in MODEL_CATALOG

def test_prompt_templates_structured_correctly():
    """Verify that the prompt templates contain the expected markers."""
    assert "Examples:" in lab.FEW_SHOT_PROMPT
    assert "step-by-step" in lab.CHAIN_OF_THOUGHT_PROMPT

def test_offline_run_does_not_crash(capsys):
    """The offline run must complete successfully without network calls."""
    import asyncio
    asyncio.run(lab.run_offline())
    captured = capsys.readouterr()
    assert "All 3 checks passed" in captured.out
