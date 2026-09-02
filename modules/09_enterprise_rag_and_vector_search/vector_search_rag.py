"""
Module 09: Enterprise RAG & Vector Search 1.0
Demonstrates:
1. Embedding Generation & Dimensionality Normalization (text-embedding-005)
2. Vertex AI Vector Search 1.0 Simulation (Cosine Similarity & Threshold Filtering)
3. Reranking & Grounded Answer Generation with Explicit Citations
"""

import os
import math
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class DocumentChunk:
    chunk_id: str
    source_uri: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]

class VectorSearchEngine:
    """Simulates Vertex AI Vector Search 1.0 ScaNN indexing and query retrieval."""

    def __init__(self, dimension: int = 64):
        self.dimension = dimension
        self.index: List[DocumentChunk] = []

    def _generate_synthetic_embedding(self, text: str) -> List[float]:
        """Generates deterministic unit-normalized pseudo-embeddings for testing."""
        # Compute repeatable pseudo-random vector based on hash
        vec = []
        for i in range(self.dimension):
            h = hashlib.sha256(f"{text}_{i}".encode()).hexdigest()
            val = (int(h[:8], 16) / 0xFFFFFFFF) * 2.0 - 1.0
            vec.append(val)

        # Normalize to unit length (L2 norm) for fast cosine dot-product
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def index_document(self, chunk_id: str, source_uri: str, text: str, metadata: Optional[Dict[str, Any]] = None):
        emb = self._generate_synthetic_embedding(text)
        chunk = DocumentChunk(
            chunk_id=chunk_id,
            source_uri=source_uri,
            text=text,
            embedding=emb,
            metadata=metadata or {}
        )
        self.index.append(chunk)

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        return sum(a * b for a, b in zip(v1, v2))

    def query(self, query_text: str, top_k: int = 3, similarity_threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Queries vector index and returns top-k nearest neighbors."""
        query_emb = self._generate_synthetic_embedding(query_text)
        scored_chunks: List[Tuple[float, DocumentChunk]] = []

        for chunk in self.index:
            sim = self._cosine_similarity(query_emb, chunk.embedding)
            # Add semantic keyword boost if query terms appear in text
            query_terms = set(query_text.lower().split())
            text_terms = set(chunk.text.lower().split())
            overlap = len(query_terms.intersection(text_terms))
            boosted_sim = sim + (0.15 * overlap)

            if boosted_sim >= similarity_threshold:
                scored_chunks.append((boosted_sim, chunk))

        # Sort descending by similarity
        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, chunk in scored_chunks[:top_k]:
            results.append({
                "chunk_id": chunk.chunk_id,
                "source_uri": chunk.source_uri,
                "score": round(score, 4),
                "text": chunk.text,
                "metadata": chunk.metadata
            })
        return results

class AgentRetrievalGrounder:
    """Synthesizes grounded agent answers with explicit source citations."""

    def __init__(self, vector_engine: VectorSearchEngine):
        self.vector_engine = vector_engine

    def answer_query(self, query: str) -> Dict[str, Any]:
        retrieved = self.vector_engine.query(query, top_k=2)
        if not retrieved:
            return {
                "answer": "I do not have sufficient information in the enterprise repository to answer this query.",
                "citations": []
            }

        citations = [r["source_uri"] for r in retrieved]
        context_snippets = "\n".join([f"[{r['source_uri']}]: {r['text']}" for r in retrieved])

        grounded_answer = (
            f"Based on enterprise policy, {retrieved[0]['text']} "
            f"(Source: {retrieved[0]['source_uri']})"
        )

        return {
            "query": query,
            "grounded_answer": grounded_answer,
            "retrieved_context": context_snippets,
            "citations": citations
        }

def main():
    print("====================================================================")
    print("Module 09: Enterprise RAG & Vector Search 1.0")
    print("====================================================================\n")

    engine = VectorSearchEngine(dimension=64)

    # Index sample enterprise policy chunks
    print("--- 1. Indexing Enterprise Architecture Documents ---")
    engine.index_document(
        chunk_id="chk_01",
        source_uri="gs://corp-docs/iam-policies/pab-guidelines.pdf",
        text="Principal Access Boundary (PAB) policies cap the Google Cloud resources an IAM principal can access; they do not grant permissions.",
        metadata={"category": "security"}
    )
    engine.index_document(
        chunk_id="chk_02",
        source_uri="gs://corp-docs/compute/cloud-run-best-practices.pdf",
        text="Cloud Run services hosting Agent Gateway APIs should configure min-instances=1 to avoid cold start latency.",
        metadata={"category": "compute"}
    )
    engine.index_document(
        chunk_id="chk_03",
        source_uri="gs://corp-docs/databases/alloydb-scalability.pdf",
        text="AlloyDB columnar engine accelerates analytical agent queries up to 100x over standard transactional engines.",
        metadata={"category": "database"}
    )
    print(f"Total documents indexed: {len(engine.index)}")

    # Query Retrieval
    print("\n--- 2. Executing Agent Retrieval Query ---")
    grounder = AgentRetrievalGrounder(engine)
    query = "How do Principal Access Boundary policies protect agent credentials?"
    result = grounder.answer_query(query)

    print(f"Query           : {result['query']}")
    print(f"Grounded Answer : {result['grounded_answer']}")
    print(f"Citations       : {result['citations']}")

if __name__ == "__main__":
    main()
