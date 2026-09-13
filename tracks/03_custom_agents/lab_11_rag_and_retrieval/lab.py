import math
from typing import List

from google.adk.memory import VertexAiRagMemoryService
from common.config import load_config, require_live
from common.models import DEFAULT_EMBEDDING_MODEL
from common.labkit import banner, section, step, LabReport, exam_note

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    return dot / (mag1 * mag2) if mag1 * mag2 else 0.0

def chunk_text(text: str, max_words: int = 15) -> List[str]:
    """Naive text chunking for demonstration."""
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def stub_embed(text: str) -> List[float]:
    """Offline stub: simple heuristic vector mapping."""
    vector = [0.0] * 3
    t = text.lower()
    vector[0] = len(t) * 0.1
    if "agent" in t or "rag" in t:
        vector[1] = 1.0
    if "travel" in t or "policy" in t:
        vector[2] = 1.0
    return vector

def run_offline():
    banner("Lab 11", "RAG and Retrieval (Offline)")
    
    section("1. Chunking and Embedding")
    document = (
        "Agent Search is a managed service for enterprise retrieval. "
        "Our corporate travel policy allows booking flights under $500 without approval. "
        "RAG pipelines use embedding models to find similar text."
    )
    chunks = chunk_text(document)
    step(1, f"Chunked document into {len(chunks)} pieces.")
    
    vector_store = [(chunk, stub_embed(chunk)) for chunk in chunks]
    step(2, f"Embedded chunks (simulating {DEFAULT_EMBEDDING_MODEL}, 8192 dims).")

    section("2. Retrieval and Ranking")
    query = "What is the travel policy?"
    q_emb = stub_embed(query)
    
    ranked = sorted(
        [(cosine_similarity(q_emb, doc_emb), doc) for doc, doc_emb in vector_store],
        reverse=True
    )
    
    top_hit = ranked[0]
    step(3, f"Top match (score {top_hit[0]:.2f}): '{top_hit[1]}'")
    
    section("3. Grounding and ADK Memory")
    prompt = f"Use this context: [{top_hit[1]}]. Answer: {query}"
    step(4, "Assembled grounded prompt to prevent hallucination.")
    
    exam_note("ADK uses VertexAiRagMemoryService to manage this transparently.")
    
    rag_svc = VertexAiRagMemoryService(
        rag_corpus="projects/123/locations/us-central1/ragCorpora/abc",
        similarity_top_k=3
    )
    
    report = LabReport("RAG Pipeline Offline")
    report.check("Chunking works", len(chunks) > 0)
    report.check("Cosine similarity ranks correct chunk", "travel policy" in top_hit[1])
    report.check("ADK Service instantiated", type(rag_svc).__name__ == "VertexAiRagMemoryService")
    report.summary()

def run_live(config):
    banner("Lab 11", "RAG and Retrieval (Live)")
    section("Live API Call")
    step(1, f"Importing google-genai to call {DEFAULT_EMBEDDING_MODEL}")
    from google import genai
    
    client = genai.Client(api_key=config.gemini_api_key)
    query = "What is the travel policy?"
    
    response = client.models.embed_content(
        model=DEFAULT_EMBEDDING_MODEL,
        contents=query
    )
    
    vector = response.embeddings[0].values
    dims = len(vector)
    
    report = LabReport("Live Embedding")
    report.check("Model called successfully", dims > 0)
    report.check("Correct dimensions", dims == 8192, f"Got {dims} dims (expected 8192)")
    report.summary()

if __name__ == "__main__":
    config = load_config()
    if require_live(config):
        run_live(config)
    else:
        run_offline()
