"""
Unit Tests for Module 09: Enterprise RAG & Vector Search 1.0
"""

import sys
from pathlib import Path
import pytest

module_dir = Path(__file__).resolve().parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))

from vector_search_rag import (
    VectorSearchEngine,
    AgentRetrievalGrounder
)

def test_vector_indexing_and_query():
    engine = VectorSearchEngine(dimension=32)
    engine.index_document("doc1", "gs://bucket/doc1.pdf", "GKE sandbox with gVisor isolates untrusted code.")
    engine.index_document("doc2", "gs://bucket/doc2.pdf", "BigQuery ML supports logistic regression.")

    results = engine.query("gVisor code isolation", top_k=1)
    assert len(results) == 1
    assert results[0]["chunk_id"] == "doc1"
    assert "gVisor" in results[0]["text"]
    assert results[0]["score"] > 0

def test_grounded_answer_generation():
    engine = VectorSearchEngine(dimension=32)
    engine.index_document("pab_doc", "gs://sec/pab.pdf", "PAB enforces strict perimeter security boundaries.")

    grounder = AgentRetrievalGrounder(engine)
    res = grounder.answer_query("Tell me about PAB perimeter boundaries")

    assert "gs://sec/pab.pdf" in res["citations"]
    assert "perimeter security boundaries" in res["grounded_answer"]
