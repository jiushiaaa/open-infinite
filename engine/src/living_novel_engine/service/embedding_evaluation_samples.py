"""Embedding Evaluation Samples MVP.

This module evaluates saved retrieval failure samples with the existing BM25
retriever and a deterministic mock semantic oracle. It never calls an
embedding provider, never creates vectors, and never writes artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from living_novel_engine.retrieval import retrieve_context
from living_novel_engine.retrieval.context_loader import (
    CanonLedgerItem,
    ContextCorpus,
    load_context_corpus,
)
from living_novel_engine.service.project_health import resolve_story_path

VERSION = "embedding-evaluation-samples-mvp"
FAILURE_SAMPLE_PATH = "memory/retrieval_failure_samples.jsonl"
DEFAULT_TOP_K = 5


def get_embedding_evaluation_samples(
    slug: str,
    projects_dir: Path | None = None,
    *,
    top_k: int = DEFAULT_TOP_K,
) -> dict[str, Any]:
    """Return a read-only BM25 vs mock embedding evaluation for saved samples."""

    project_dir, source_kind = resolve_story_path(slug, projects_dir)
    corpus = load_context_corpus(project_dir)
    sample_status, raw_samples = _read_failure_samples(project_dir / FAILURE_SAMPLE_PATH)
    samples = [
        _evaluate_sample(project_dir, corpus, sample, top_k=top_k)
        for sample in raw_samples
    ]
    summary = _summary(sample_status, samples)
    status = _status(sample_status, summary)

    return {
        "version": VERSION,
        "mode": "read_only_embedding_evaluation_samples",
        "status": status,
        "story_slug": slug,
        "source_kind": source_kind,
        "summary": summary,
        "samples": samples,
        "sample_schema": {
            "path": FAILURE_SAMPLE_PATH,
            "required": ["query", "expected_entities"],
            "optional": [
                "expected_item_id",
                "expected_source",
                "reason",
                "current_chapter",
                "actual_top_sources",
            ],
        },
        "warnings": _warnings(sample_status, corpus),
        "boundaries": [
            "只读读取 retrieval_failure_samples.jsonl 与本地记忆语料。",
            "不写失败样本，不生成 embedding，不创建向量索引。",
            "mock embedding oracle 只用于本地对照评估，不代表真实 provider 效果。",
            "不替换 retrieve_context，不改变 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _read_failure_samples(path: Path) -> tuple[str, list[dict[str, Any]]]:
    if not path.exists():
        return "missing", []
    samples: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            if not isinstance(data, dict):
                return "damaged", []
            query = str(data.get("query") or "").strip()
            expected_entities = [
                str(item)
                for item in data.get("expected_entities", []) or []
                if str(item).strip()
            ]
            if not query or not expected_entities:
                samples.append(
                    {
                        "query": query,
                        "expected_entities": expected_entities,
                        "invalid": True,
                        "reason": "缺少 query 或 expected_entities",
                    }
                )
                continue
            samples.append(
                {
                    "query": query[:180],
                    "expected_entities": expected_entities[:10],
                    "expected_item_id": str(data.get("expected_item_id") or ""),
                    "expected_source": str(data.get("expected_source") or "canon_ledger"),
                    "reason": str(data.get("reason") or "未记录原因")[:220],
                    "current_chapter": _int(data.get("current_chapter"), default=1),
                    "actual_top_sources": [
                        str(item)
                        for item in data.get("actual_top_sources", []) or []
                        if str(item).strip()
                    ][:8],
                }
            )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "damaged", []
    return "ready", samples[:20]


def _evaluate_sample(
    project_dir: Path,
    corpus: ContextCorpus,
    sample: dict[str, Any],
    *,
    top_k: int,
) -> dict[str, Any]:
    query = str(sample.get("query") or "")
    expected_entities = list(sample.get("expected_entities") or [])
    expected_item_id = str(sample.get("expected_item_id") or "")
    expected_source = str(sample.get("expected_source") or "canon_ledger")
    current_chapter = _int(sample.get("current_chapter"), default=1)
    invalid = bool(sample.get("invalid"))

    retrieval = (
        retrieve_context(project_dir, query, current_chapter=current_chapter, top_k=top_k)
        if query and not invalid
        else None
    )
    items = retrieval.items if retrieval else []
    bm25_hit = _matches_items(items, expected_entities, expected_item_id, expected_source)
    target = _mock_semantic_target(corpus, expected_entities, expected_item_id)
    mock_embedding_hit = target is not None
    diagnosis = _diagnosis(
        invalid=invalid,
        bm25_hit=bm25_hit,
        mock_embedding_hit=mock_embedding_hit,
    )

    return {
        "query": query,
        "expected_entities": expected_entities,
        "expected_item_id": expected_item_id,
        "expected_source": expected_source,
        "current_chapter": current_chapter,
        "reason": str(sample.get("reason") or ""),
        "bm25_hit": bm25_hit,
        "mock_embedding_hit": mock_embedding_hit,
        "diagnosis": diagnosis,
        "target_item_id": f"canon_ledger:{target.id}" if target else "",
        "target_statement": target.statement[:180] if target else "",
        "top_items": [_compact_item(item) for item in items[:top_k]],
        "actual_top_sources": _top_sources(items),
    }


def _matches_items(
    items: list[dict[str, Any]],
    expected_entities: list[str],
    expected_item_id: str,
    expected_source: str,
) -> bool:
    if expected_item_id and any(item.get("id") == expected_item_id for item in items):
        return True
    expected = set(expected_entities)
    for item in items:
        if expected_source and item.get("source") != expected_source:
            continue
        values = set(item.get("entities") or []) | set(item.get("resolved_entities") or [])
        if expected and expected.issubset(values):
            return True
    return False


def _mock_semantic_target(
    corpus: ContextCorpus,
    expected_entities: list[str],
    expected_item_id: str,
) -> CanonLedgerItem | None:
    expected = set(expected_entities)
    for item in corpus.canon_ledger:
        item_id = f"canon_ledger:{item.id}"
        if expected_item_id and item_id == expected_item_id:
            return item
        if expected and expected.issubset(set(item.entities)):
            return item
    return None


def _diagnosis(
    *, invalid: bool, bm25_hit: bool, mock_embedding_hit: bool
) -> str:
    if invalid:
        return "invalid_sample"
    if bm25_hit:
        return "already_covered"
    if mock_embedding_hit:
        return "lexical_gap"
    return "memory_gap"


def _summary(sample_status: str, samples: list[dict[str, Any]]) -> dict[str, Any]:
    sample_count = len(samples)
    bm25_hit_count = sum(1 for sample in samples if sample["bm25_hit"])
    mock_hit_count = sum(1 for sample in samples if sample["mock_embedding_hit"])
    lexical_gap_count = sum(1 for sample in samples if sample["diagnosis"] == "lexical_gap")
    memory_gap_count = sum(1 for sample in samples if sample["diagnosis"] == "memory_gap")
    invalid_count = sum(1 for sample in samples if sample["diagnosis"] == "invalid_sample")
    return {
        "sample_status": sample_status,
        "sample_count": sample_count,
        "bm25_hit_count": bm25_hit_count,
        "mock_embedding_hit_count": mock_hit_count,
        "lexical_gap_count": lexical_gap_count,
        "memory_gap_count": memory_gap_count,
        "invalid_sample_count": invalid_count,
        "bm25_hit_rate": _ratio(bm25_hit_count, sample_count),
        "mock_embedding_hit_rate": _ratio(mock_hit_count, sample_count),
        "writes_artifacts": False,
        "external_services_required": False,
        "uses_embedding_provider": False,
        "uses_vector_store": False,
        "plaintext_key_returned": False,
    }


def _status(sample_status: str, summary: dict[str, Any]) -> str:
    if sample_status == "damaged" or summary["invalid_sample_count"] > 0:
        return "blocked"
    if summary["sample_count"] == 0:
        return "insufficient_samples"
    if summary["lexical_gap_count"] > 0:
        return "candidate"
    if summary["memory_gap_count"] > 0:
        return "attention"
    return "covered"


def _warnings(sample_status: str, corpus: ContextCorpus) -> list[str]:
    warnings: list[str] = []
    if sample_status == "damaged":
        warnings.append(f"{FAILURE_SAMPLE_PATH} 损坏，无法评估样本。")
    if corpus.entity_aliases.status != "ready":
        warnings.append("entity_aliases.yaml 缺失或损坏，样本诊断可能不完整。")
    if not corpus.canon_ledger:
        warnings.append("canon_ledger.jsonl 缺失或为空，无法判断 mock semantic target。")
    return warnings


def _next_steps(status: str) -> list[str]:
    if status == "candidate":
        return [
            "把 lexical_gap 样本固化为回归评测集。",
            "下一步可做 mock embedding 对照报告，比较 BM25 与语义 oracle 的命中差异。",
            "真实 provider 或向量库仍需等 mock 对照证明收益后再接。",
        ]
    if status == "attention":
        return [
            "先补 canon ledger 或 expected_entities，让失败样本能定位到目标事实。",
            "不要把资料缺口误判为 embedding 收益。",
        ]
    if status == "blocked":
        return [
            "先修复 retrieval_failure_samples.jsonl 的 JSONL 格式和必填字段。",
        ]
    if status == "covered":
        return [
            "当前样本已被 BM25 命中，暂不需要 embedding 对照。",
        ]
    return [
        "先收集换说法召回失败样本，再评估 embedding 收益。",
        "每条样本至少包含 query 与 expected_entities。",
    ]


def _compact_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id", ""),
        "source": item.get("source", ""),
        "score": item.get("score", 0.0),
        "text": str(item.get("text") or "")[:120],
        "entities": item.get("entities") or item.get("resolved_entities") or [],
    }


def _top_sources(items: list[dict[str, Any]]) -> list[str]:
    sources: list[str] = []
    for item in items:
        source = str(item.get("source") or "")
        if source and source not in sources:
            sources.append(source)
    return sources[:6]


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def _int(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
