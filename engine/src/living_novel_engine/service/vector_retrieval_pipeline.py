"""Real vector retrieval pipeline.

This service is opt-in: it can build a Zilliz-backed vector index and query it
with DashScope embeddings/rerank, while keeping BM25 as fallback.
"""

from __future__ import annotations

import hashlib
import importlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from openai import OpenAI

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.retrieval import RetrievedContext, retrieve_context
from living_novel_engine.retrieval.context_loader import load_context_corpus
from living_novel_engine.retrieval.retriever import _build_corpus
from living_novel_engine.service import retrieval_provider_configuration as rpc
from living_novel_engine.service.project_health import resolve_story_path

VERSION = "vector-retrieval-pipeline-mvp"


class VectorRetrievalPipelineRequestError(ValueError):
    """Invalid vector retrieval pipeline request, mapped to HTTP 400."""


@dataclass
class HybridRetrievedContext(RetrievedContext):
    """Retrieved context with vector/rerank metadata."""

    retrieval_mode: str = "hybrid_vector_rerank"
    provider: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def as_prompt_block(self) -> str:
        if not self.items:
            return ""
        lines = [
            f"- [{item.get('source', '')}] {item.get('text', '')}"
            for item in self.items
            if str(item.get("text") or "").strip()
        ]
        if not lines:
            return ""
        return "【向量检索与重排结果】\n" + "\n".join(lines)

    def to_artifact(self) -> dict[str, Any]:
        artifact = super().to_artifact()
        artifact.update(
            {
                "retrieval_mode": self.retrieval_mode,
                "provider": self.provider,
                "warnings": self.warnings,
            }
        )
        return artifact


def build_vector_retrieval_index(
    slug: str,
    *,
    projects_dir: Path | None = None,
    refresh: bool = False,
    limit: int | None = None,
) -> dict[str, Any]:
    """Embed project memory and write the vectors to Zilliz Cloud."""

    sid = _safe_slug(slug)
    project_dir, source_kind = resolve_story_path(sid, projects_dir)
    settings = rpc.get_retrieval_provider_settings()
    documents = _project_documents(project_dir)
    if limit is not None:
        documents = documents[: max(0, int(limit))]

    summary = {
        "document_count": len(documents),
        "indexed_count": 0,
        "embedding_model": settings.embedding_model,
        "embedding_dimension": settings.embedding_dimension,
        "vector_store_provider": settings.vector_store_provider,
        "collection": settings.zilliz_collection,
        "writes_vector_store": False,
        "plaintext_key_returned": False,
    }

    if not documents:
        return _index_report(sid, source_kind, "empty", summary, [])
    _require_provider_settings(settings)

    vectors = _embed_texts([doc["document_text"] for doc in documents], settings)
    client = _new_milvus_client(settings)
    _ensure_collection(client, settings)
    rows = [
        _vector_row(document, vector, settings)
        for document, vector in zip(documents, vectors)
    ]
    if refresh:
        client.delete(
            collection_name=settings.zilliz_collection,
            ids=[int(row["id"]) for row in rows],
        )
    client.insert(collection_name=settings.zilliz_collection, data=rows)
    summary["indexed_count"] = len(rows)
    summary["writes_vector_store"] = True
    return _index_report(sid, source_kind, "ready", summary, _preview_docs(documents))


def retrieve_hybrid_vector_context(
    project_dir: Path,
    query: str,
    *,
    current_chapter: int = 1,
    top_k: int = 8,
) -> HybridRetrievedContext:
    """Retrieve from BM25 + Zilliz vectors, then rerank candidates when available."""

    settings = rpc.get_retrieval_provider_settings()
    bm25 = retrieve_context(
        project_dir,
        query,
        current_chapter=current_chapter,
        top_k=top_k,
    )
    provider = _provider_summary(settings)
    warnings: list[str] = []

    try:
        _require_provider_settings(settings)
        query_vector = _embed_texts([query], settings)[0]
        client = _new_milvus_client(settings)
        vector_items = _search_vector_items(client, settings, query_vector, top_k=top_k)
        merged = _merge_items(bm25.items, vector_items, top_k=max(top_k * 2, top_k))
        items = _rerank_items(query, merged, settings)[:top_k]
        mode = "hybrid_vector_rerank"
    except Exception as exc:
        warnings.append(f"向量检索不可用，已回退 BM25：{exc}")
        items = list(bm25.items[:top_k])
        mode = "bm25_fallback"

    return HybridRetrievedContext(
        facts_text="",
        summaries_text="",
        contract_text="",
        items=items,
        query=query,
        current_chapter=current_chapter,
        retrieval_mode=mode,
        provider=provider,
        warnings=warnings,
    )


def search_vector_retrieval(
    slug: str,
    query: str,
    *,
    projects_dir: Path | None = None,
    current_chapter: int = 1,
    top_k: int = 8,
) -> dict[str, Any]:
    """Return a secret-safe hybrid retrieval report for UI/API preview."""

    sid = _safe_slug(slug)
    project_dir, source_kind = resolve_story_path(sid, projects_dir)
    ctx = retrieve_hybrid_vector_context(
        project_dir,
        query,
        current_chapter=current_chapter,
        top_k=top_k,
    )
    artifact = ctx.to_artifact()
    status = "ready" if artifact["items"] else "empty"
    if artifact["retrieval_mode"] == "bm25_fallback":
        status = "fallback"
    return {
        "version": VERSION,
        "mode": "hybrid_vector_retrieval_preview",
        "status": status,
        "story_slug": sid,
        "source_kind": source_kind,
        "summary": {
            "item_count": len(artifact["items"]),
            "retrieval_mode": artifact["retrieval_mode"],
            "uses_embedding_provider": artifact["retrieval_mode"] != "bm25_fallback",
            "uses_vector_store": artifact["retrieval_mode"] != "bm25_fallback",
            "uses_reranker": artifact["retrieval_mode"] == "hybrid_vector_rerank",
            "writes_vector_store": False,
            "default_retrieval_changed": False,
            "plaintext_key_returned": False,
        },
        "query": query,
        "current_chapter": current_chapter,
        "provider": artifact["provider"],
        "items": artifact["items"],
        "prompt_block": artifact["prompt_block"],
        "warnings": artifact["warnings"],
        "boundaries": [
            "该预览会调用真实 embedding / Zilliz / reranker，但不写入向量库。",
            "运行时只有 LNE_RETRIEVAL_STRATEGY=hybrid_vector 时才消费该链路。",
            "任一 provider 失败时回退 BM25，不改变 run_scene 默认行为。",
        ],
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise VectorRetrievalPipelineRequestError("invalid slug")
    return sid


def _project_documents(project_dir: Path) -> list[dict[str, Any]]:
    corpus = load_context_corpus(project_dir)
    documents, doc_ids, doc_chapters, doc_types, doc_meta = _build_corpus(corpus)
    rows: list[dict[str, Any]] = []
    for index, doc_id in enumerate(doc_ids):
        meta = doc_meta[index] if index < len(doc_meta) else {}
        text = str(meta.get("text") or documents[index] or "").strip()
        if not text:
            continue
        rows.append(
            {
                "doc_id": doc_id,
                "source": doc_types[index],
                "chapter": int(doc_chapters[index] or 1),
                "text": text,
                "document_text": documents[index],
                "evidence": str(meta.get("evidence") or ""),
                "entities": list(meta.get("entities") or []),
                "resolved_entities": list(meta.get("resolved_entities") or []),
            }
        )
    return rows


def _embed_texts(
    texts: list[str],
    settings: rpc.RetrievalProviderSettings,
) -> list[list[float]]:
    client = OpenAI(
        api_key=settings.embedding_api_key,
        base_url=settings.embedding_base_url,
    )
    vectors: list[list[float]] = []
    batch_size = max(1, int(settings.embedding_batch_size))
    for offset in range(0, len(texts), batch_size):
        batch = texts[offset : offset + batch_size]
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=batch,
            dimensions=settings.embedding_dimension,
        )
        vectors.extend([list(item.embedding) for item in response.data])
    return vectors


def _new_milvus_client(settings: rpc.RetrievalProviderSettings):
    pymilvus = importlib.import_module("pymilvus")
    return pymilvus.MilvusClient(
        uri=settings.zilliz_uri,
        token=settings.zilliz_token,
        timeout=60,
    )


def _ensure_collection(client, settings: rpc.RetrievalProviderSettings) -> None:
    if client.has_collection(settings.zilliz_collection):
        return
    client.create_collection(
        collection_name=settings.zilliz_collection,
        dimension=settings.embedding_dimension,
        metric_type="COSINE",
        consistency_level="Strong",
    )


def _vector_row(
    document: dict[str, Any],
    vector: list[float],
    settings: rpc.RetrievalProviderSettings,
) -> dict[str, Any]:
    return {
        "id": _stable_int_id(document["doc_id"]),
        "vector": vector,
        "doc_id": document["doc_id"],
        "source": document["source"],
        "chapter": document["chapter"],
        "text": document["text"],
        "document_text": document["document_text"],
        "evidence": document["evidence"],
        "entities": document["entities"],
        "resolved_entities": document["resolved_entities"],
        "embedding_model": settings.embedding_model,
    }


def _stable_int_id(doc_id: str) -> int:
    digest = hashlib.sha256(doc_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") & ((1 << 63) - 1)


def _search_vector_items(
    client,
    settings: rpc.RetrievalProviderSettings,
    query_vector: list[float],
    *,
    top_k: int,
) -> list[dict[str, Any]]:
    result = client.search(
        collection_name=settings.zilliz_collection,
        data=[query_vector],
        anns_field="vector",
        limit=top_k,
        output_fields=[
            "doc_id",
            "source",
            "chapter",
            "text",
            "evidence",
            "entities",
            "resolved_entities",
        ],
    )
    hits = result[0] if result else []
    return [_item_from_hit(hit) for hit in hits]


def _item_from_hit(hit: Any) -> dict[str, Any]:
    entity = hit.get("entity") if isinstance(hit, dict) else getattr(hit, "entity", {})
    if entity is None:
        entity = {}
    if not isinstance(entity, Mapping):
        entity = {}
    score = hit.get("distance", 0.0) if isinstance(hit, dict) else getattr(hit, "distance", 0.0)
    hit_id = hit.get("id") if isinstance(hit, dict) else getattr(hit, "id", "")
    return {
        "id": str(entity.get("doc_id") or hit_id or ""),
        "source": str(entity.get("source") or "vector"),
        "type": str(entity.get("source") or "vector"),
        "score": round(float(score or 0.0), 4),
        "vector_score": round(float(score or 0.0), 4),
        "text": str(entity.get("text") or ""),
        "chapter": int(entity.get("chapter") or 1),
        "evidence": str(entity.get("evidence") or ""),
        "entities": list(entity.get("entities") or []),
        "resolved_entities": list(entity.get("resolved_entities") or []),
        "retrieval_path": "vector",
    }


def _merge_items(
    bm25_items: list[dict[str, Any]],
    vector_items: list[dict[str, Any]],
    *,
    top_k: int,
) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for item in bm25_items:
        doc_id = str(item.get("id") or "")
        if not doc_id:
            continue
        row = dict(item)
        row["bm25_score"] = float(row.get("score") or 0.0)
        row["retrieval_path"] = "bm25"
        merged[doc_id] = row
    for item in vector_items:
        doc_id = str(item.get("id") or "")
        if not doc_id:
            continue
        if doc_id in merged:
            merged[doc_id].update(
                {
                    "vector_score": item.get("vector_score", item.get("score", 0.0)),
                    "retrieval_path": "hybrid",
                }
            )
        else:
            merged[doc_id] = dict(item)
    candidates = list(merged.values())
    candidates.sort(
        key=lambda item: (
            float(item.get("rerank_score") or 0.0),
            float(item.get("vector_score") or 0.0),
            float(item.get("bm25_score") or item.get("score") or 0.0),
        ),
        reverse=True,
    )
    return candidates[:top_k]


def _rerank_items(
    query: str,
    items: list[dict[str, Any]],
    settings: rpc.RetrievalProviderSettings,
) -> list[dict[str, Any]]:
    if not items or not settings.rerank_api_key:
        return items
    data = rpc._call_dashscope_rerank(
        api_key=settings.rerank_api_key,
        endpoint=settings.rerank_endpoint,
        model=settings.rerank_model,
        query=query,
        documents=[str(item.get("text") or "") for item in items],
        top_n=min(len(items), settings.rerank_top_n),
    )
    rows = rpc._extract_rerank_rows(data)
    reranked: list[dict[str, Any]] = []
    for row in rows:
        index = int(row.get("index") or 0)
        if index < 0 or index >= len(items):
            continue
        item = dict(items[index])
        item["rerank_score"] = round(float(row.get("relevance_score") or 0.0), 4)
        item["retrieval_path"] = (
            "hybrid_rerank"
            if item.get("retrieval_path") == "hybrid"
            else "vector_rerank"
            if item.get("retrieval_path") == "vector"
            else "bm25_rerank"
        )
        reranked.append(item)
    return reranked or items


def _require_provider_settings(settings: rpc.RetrievalProviderSettings) -> None:
    if not settings.embedding_api_key:
        raise VectorRetrievalPipelineRequestError("embedding provider not configured")
    if not settings.zilliz_uri or not settings.zilliz_token:
        raise VectorRetrievalPipelineRequestError("zilliz provider not configured")


def _provider_summary(settings: rpc.RetrievalProviderSettings) -> dict[str, Any]:
    return {
        "embedding_provider": "aliyun_bailian",
        "embedding_model": settings.embedding_model,
        "embedding_dimension": settings.embedding_dimension,
        "vector_store": settings.vector_store_provider,
        "collection": settings.zilliz_collection,
        "reranker_provider": "aliyun_bailian",
        "reranker_model": settings.rerank_model,
    }


def _index_report(
    story_slug: str,
    source_kind: str,
    status: str,
    summary: dict[str, Any],
    documents: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "mode": "write_vector_retrieval_index",
        "status": status,
        "story_slug": story_slug,
        "source_kind": source_kind,
        "summary": summary,
        "documents": documents,
        "boundaries": [
            "只写当前项目的检索语料向量，不读取 holdout_private。",
            "不覆盖 canon_ledger.jsonl、retrieval_context.json 或 state_snapshot.json。",
            "不返回明文 Key；运行时消费仍由 LNE_RETRIEVAL_STRATEGY 显式控制。",
        ],
    }


def _preview_docs(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "doc_id": doc["doc_id"],
            "source": doc["source"],
            "chapter": doc["chapter"],
            "text": str(doc["text"])[:160],
        }
        for doc in documents[:20]
    ]
