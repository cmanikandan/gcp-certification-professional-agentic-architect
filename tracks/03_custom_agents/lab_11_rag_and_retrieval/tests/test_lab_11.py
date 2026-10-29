import warnings

warnings.filterwarnings("ignore", category=UserWarning)

import lab
from common.models import DEFAULT_EMBEDDING_MODEL, EMBEDDING_MODELS
from google.adk.memory import VertexAiRagMemoryService
from google.adk.tools import VertexAiSearchTool
from google.cloud import discoveryengine_v1
from vertexai.preview import rag


def test_uses_only_verified_models():
    assert DEFAULT_EMBEDDING_MODEL in EMBEDDING_MODELS
    assert EMBEDDING_MODELS[DEFAULT_EMBEDDING_MODEL] == 8192


def test_adk_memory_imports():
    svc = VertexAiRagMemoryService(rag_corpus="abc")
    assert hasattr(svc, "add_memory")
    assert hasattr(svc, "search_memory")

    search_tool = VertexAiSearchTool(data_store_id="projects/p/locations/global/collections/default_collection/dataStores/ds")
    assert search_tool.max_results is None or isinstance(search_tool.max_results, int)


def test_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    assert lab.cosine_similarity(v1, v2) == 1.0
    assert lab.cosine_similarity(v1, v3) == 0.0


def test_rag_engine_chunking_layout_hybrid_and_ranker_configs():
    cfgs = lab.build_rag_engine_configs()
    corpus = cfgs["corpus"]
    transform = cfgs["transform_cfg"]
    layout = cfgs["layout_parser_cfg"]
    retrieval = cfgs["retrieval_cfg"]
    llm_ranker_cfg = cfgs["llm_ranker_cfg"]

    assert isinstance(corpus, rag.RagCorpus)
    assert transform.chunking_config.chunk_size == 512
    assert transform.chunking_config.chunk_overlap == 100
    assert layout.max_parsing_requests_per_min == 120
    assert retrieval.top_k == 50
    assert retrieval.hybrid_search.alpha == 0.5
    assert retrieval.ranking.rank_service.model_name == "semantic-ranker-default@latest"
    assert llm_ranker_cfg.ranking.llm_ranker.model_name is not None


def test_discovery_engine_reranking_and_rrf():
    candidates = [
        ("c1", "General Refund", "Refundable tickets qualify for 24-hour refund."),
        ("c2", "Exception Policy", "Basic economy tickets are non-refundable and NOT eligible."),
    ]
    client, req = lab.build_discovery_engine_rank_request(
        query="Which tickets are NOT eligible for refund?",
        candidates=candidates,
        top_n=1,
    )
    assert isinstance(client, discoveryengine_v1.RankServiceClient)
    assert req.model == "semantic-ranker-default@latest"
    assert req.top_n == 1
    assert len(req.records) == 2

    ranked = lab.stub_cross_encoder_rerank(req.query, list(req.records))
    assert ranked[0][0] == "c2"

    fused = lab.reciprocal_rank_fusion(["c1", "c2"], ["c2", "c1"])
    assert len(fused) == 2


def test_offline_report_passes():
    report = lab.run_offline()
    assert report.passed
