#!/usr/bin/env python3
"""Lab 11: RAG Engine, Two-Stage Reranking API & Vector Search 1.0 (Objective 3.2)."""

from __future__ import annotations

import math
import sys
import warnings
from typing import List

warnings.filterwarnings("ignore", category=UserWarning)

from common.config import load_config, require_live
from common.labkit import LabReport, banner, exam_note, section, step, table
from common.models import DEFAULT_EMBEDDING_MODEL, DEFAULT_FAST_MODEL
from google.adk.memory import VertexAiRagMemoryService
from google.adk.tools import VertexAiSearchTool
from google.auth.credentials import AnonymousCredentials
from google.cloud import discoveryengine_v1
from vertexai.preview import rag


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two dense vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    return dot / (mag1 * mag2) if mag1 * mag2 else 0.0


def reciprocal_rank_fusion(
    dense_ranked_ids: list[str],
    sparse_ranked_ids: list[str],
    rrf_k: int = 60,
) -> list[tuple[str, float]]:
    """Fuse dense ANN ranks and sparse BM25 ranks via Reciprocal Rank Fusion (RRF)."""
    scores: dict[str, float] = {}
    for rank_idx, doc_id in enumerate(dense_ranked_ids, start=1):
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (rrf_k + rank_idx)
    for rank_idx, doc_id in enumerate(sparse_ranked_ids, start=1):
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (rrf_k + rank_idx)
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)


def stub_bi_encoder(text: str) -> list[float]:
    """Deterministic coarse bi-encoder stub (ignores negation nuance on purpose)."""
    t = text.lower()
    return [
        1.0 if ("flight" in t or "ticket" in t) else 0.1,
        1.0 if ("refund" in t or "eligible" in t) else 0.1,
        1.0 if ("travel" in t or "policy" in t) else 0.1,
    ]


def stub_cross_encoder_rerank(query: str, records: list[discoveryengine_v1.RankingRecord]) -> list[tuple[str, float]]:
    """Deterministic cross-encoder simulation modeling joint (query, chunk) attention.

    Demonstrates why Stage-2 Reranking API beats raw bi-encoder cosine when queries
    contain negations ('not', 'non-refundable') or exact exception clauses.
    """
    q = query.lower()
    wants_negation = "not" in q or "non-refundable" in q or "exception" in q
    scored: list[tuple[str, float]] = []
    for rec in records:
        c = f"{rec.title} {rec.content}".lower()
        base = 0.50
        if "refund" in c and "policy" in c:
            base += 0.20
        has_negation = "non-refundable" in c or "not eligible" in c
        if wants_negation and has_negation:
            base += 0.28
        elif wants_negation and not has_negation:
            base -= 0.15
        scored.append((rec.id, round(base, 4)))
    return sorted(scored, key=lambda item: item[1], reverse=True)


def build_rag_engine_configs() -> dict[str, object]:
    """Instantiate real Vertex AI RAG Engine & Discovery Engine Reranking configs."""
    corpus = rag.RagCorpus(
        display_name="enterprise-travel-finance-kb",
        description="Managed RAG corpus with LayoutParser chunking and RankService reranking",
    )
    transform_cfg = rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(
            chunk_size=512,
            chunk_overlap=100,
        )
    )
    layout_parser_cfg = rag.LayoutParserConfig(
        processor_name="projects/proj-knowledge/locations/us/processors/docai-layout-v1",
        max_parsing_requests_per_min=120,
    )
    retrieval_cfg = rag.RagRetrievalConfig(
        top_k=50,
        filter=rag.Filter(vector_distance_threshold=0.45),
        hybrid_search=rag.HybridSearch(alpha=0.5),
        ranking=rag.Ranking(
            rank_service=rag.RankService(model_name="semantic-ranker-default@latest")
        ),
    )
    llm_ranker_cfg = rag.RagRetrievalConfig(
        top_k=25,
        ranking=rag.Ranking(
            llm_ranker=rag.LlmRanker(model_name=DEFAULT_FAST_MODEL)
        ),
    )
    return {
        "corpus": corpus,
        "transform_cfg": transform_cfg,
        "layout_parser_cfg": layout_parser_cfg,
        "retrieval_cfg": retrieval_cfg,
        "llm_ranker_cfg": llm_ranker_cfg,
    }


def build_discovery_engine_rank_request(
    query: str,
    candidates: list[tuple[str, str, str]],
    top_n: int = 2,
) -> tuple[discoveryengine_v1.RankServiceClient, discoveryengine_v1.RankRequest]:
    """Construct an offline-safe RankServiceClient and RankRequest."""
    client = discoveryengine_v1.RankServiceClient(credentials=AnonymousCredentials())
    records = [
        discoveryengine_v1.RankingRecord(id=cid, title=title, content=body)
        for cid, title, body in candidates
    ]
    req = discoveryengine_v1.RankRequest(
        ranking_config="projects/proj-knowledge/locations/global/rankingConfigs/default_ranking_config",
        model="semantic-ranker-default@latest",
        top_n=top_n,
        query=query,
        records=records,
    )
    return client, req


def run_offline() -> LabReport:
    banner(
        "Lab 11 — RAG Engine, Two-Stage Reranking API & Vector Search 1.0",
        "Objective 3.2: RagCorpus, LayoutParser, HybridSearch & RankServiceClient (Offline)",
    )
    report = LabReport("Lab 11 — RAG & Two-Stage Reranking")

    section("1. Vertex AI RAG Engine Ingestion & Retrieval Configuration")
    cfgs = build_rag_engine_configs()
    transform_cfg: rag.TransformationConfig = cfgs["transform_cfg"]  # type: ignore[assignment]
    layout_cfg: rag.LayoutParserConfig = cfgs["layout_parser_cfg"]  # type: ignore[assignment]
    retrieval_cfg: rag.RagRetrievalConfig = cfgs["retrieval_cfg"]  # type: ignore[assignment]

    step(
        1,
        f"TransformationConfig: chunk_size={transform_cfg.chunking_config.chunk_size}, "
        f"chunk_overlap={transform_cfg.chunking_config.chunk_overlap}",
    )
    step(2, f"LayoutParserConfig: max_rpm={layout_cfg.max_parsing_requests_per_min} (preserves PDF tables)")
    step(
        3,
        f"RagRetrievalConfig: Stage-1 top_k={retrieval_cfg.top_k}, "
        f"HybridSearch(alpha={retrieval_cfg.hybrid_search.alpha}), "
        f"RankService='{retrieval_cfg.ranking.rank_service.model_name}'",
    )
    report.check(
        "Vertex AI RAG Engine chunking (512/100), LayoutParser, HybridSearch, and RankService configured",
        transform_cfg.chunking_config.chunk_size == 512
        and transform_cfg.chunking_config.chunk_overlap == 100
        and retrieval_cfg.top_k == 50
        and retrieval_cfg.hybrid_search.alpha == 0.5
        and retrieval_cfg.ranking.rank_service.model_name == "semantic-ranker-default@latest",
    )

    section("2. Two-Stage Retrieval: Bi-Encoder + Hybrid RRF -> Cross-Encoder Reranking API")
    candidates = [
        (
            "chunk_std_refund",
            "Standard Travel Refund Policy",
            "Corporate travel policy: refundable economy flight tickets are eligible for full refund within 24 hours.",
        ),
        (
            "chunk_negation_exc",
            "Basic Economy Exception Clause (ERR-409)",
            "Corporate travel policy exception: Basic Economy promotional flight tickets are non-refundable and NOT eligible for 24-hour refund.",
        ),
        (
            "chunk_hotel",
            "Hotel Per-Diem Guidelines",
            "Domestic hotel bookings under $250 per night do not require VP approval.",
        ),
    ]
    query = "Which flight tickets are NOT eligible for a 24-hour travel policy refund?"
    q_vec = stub_bi_encoder(query)

    bi_scores = sorted(
        [
            (cosine_similarity(q_vec, stub_bi_encoder(body)), cid)
            for cid, _title, body in candidates
        ],
        reverse=True,
    )
    dense_order = [cid for _s, cid in bi_scores]
    sparse_bm25_order = ["chunk_negation_exc", "chunk_std_refund", "chunk_hotel"]
    rrf_fused = reciprocal_rank_fusion(dense_order, sparse_bm25_order)

    rank_client, rank_req = build_discovery_engine_rank_request(
        query=query,
        candidates=candidates,
        top_n=1,
    )
    reranked = stub_cross_encoder_rerank(rank_req.query, list(rank_req.records))

    table(
        ["Stage", "Top-1 Selected Chunk", "Context Chunks Sent to LLM"],
        [
            [f"Stage 1 Bi-Encoder ({DEFAULT_EMBEDDING_MODEL}, 8192d)", dense_order[0], "Top-50 (coarse recall)"],
            ["Stage 1b Hybrid RRF (Dense + Sparse BM25)", rrf_fused[0][0], "Top-50 (lexical + semantic)"],
            [f"Stage 2 {type(rank_client).__name__} ({rank_req.model})", reranked[0][0], f"Top-{rank_req.top_n} (high precision)"],
        ],
    )
    exam_note(
        "Pruning Top-50 ANN recall candidates down to Top-5 via RankServiceClient "
        "cuts downstream LLM context tokens by 90% and rescues negation accuracy."
    )
    report.check(
        "Discovery Engine RankRequest & Cross-Encoder Reranker promote negation-accurate policy chunk",
        isinstance(rank_client, discoveryengine_v1.RankServiceClient)
        and rank_req.model == "semantic-ranker-default@latest"
        and len(rank_req.records) == 3
        and reranked[0][0] == "chunk_negation_exc",
    )

    section("3. ADK Retrieval Surface: Agent Search vs RAG Engine Memory")
    rag_mem = VertexAiRagMemoryService(
        rag_corpus="projects/proj-knowledge/locations/us-central1/ragCorpora/travel-kb",
        similarity_top_k=5,
        vector_distance_threshold=0.45,
    )
    agent_search_tool = VertexAiSearchTool(
        data_store_id="projects/proj-knowledge/locations/global/collections/default_collection/dataStores/sharepoint-acl-ds",
        max_results=5,
    )
    step(4, f"ADK RAG Engine memory service: {type(rag_mem).__name__}")
    step(5, f"ADK Agent Search ACL-aware tool: {type(agent_search_tool).__name__}")
    report.check(
        "Both VertexAiRagMemoryService and VertexAiSearchTool instantiate offline",
        isinstance(rag_mem, VertexAiRagMemoryService)
        and isinstance(agent_search_tool, VertexAiSearchTool),
    )

    report.summary()
    return report


def run_live(config) -> None:
    banner("Lab 11 — RAG and Retrieval (Live)", f"Project: {config.project_id}")
    step(1, f"Calling {DEFAULT_EMBEDDING_MODEL} via google-genai")
    from google import genai

    client = genai.Client(api_key=config.gemini_api_key)
    response = client.models.embed_content(
        model=DEFAULT_EMBEDDING_MODEL,
        contents="Which flight tickets are NOT eligible for a 24-hour refund?",
    )
    dims = len(response.embeddings[0].values)
    report = LabReport("Live Embedding Verification")
    report.check("Embedding vector returned", dims > 0)
    report.check("Verified 8192 embedding dimensions", dims == 8192, f"got {dims}")
    report.summary()


if __name__ == "__main__":
    cfg = load_config(sys.argv[1:])
    if require_live(cfg):
        run_live(cfg)
    else:
        result = run_offline()
        sys.exit(0 if result.passed else 1)
