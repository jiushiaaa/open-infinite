"""v0.9.3 Retrieval Probe-B.

The probe uses the existing BM25 / canon ledger / entity aliases stack only.
It does not connect graph databases, vector stores, rerankers, or external
services.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from living_novel_engine.retrieval import retrieve_context
from living_novel_engine.retrieval.context_loader import (
    CanonLedgerItem,
    ContextCorpus,
    load_context_corpus,
)
from living_novel_engine.service.project_health import resolve_story_path

MAX_PROBES = 6
TOP_K = 5


def evaluate_retrieval_probes(
    slug: str,
    projects_dir: Path | None = None,
    *,
    max_probes: int = MAX_PROBES,
    top_k: int = TOP_K,
) -> dict[str, Any]:
    """Run deterministic retrieval probes against the current file memory stack."""
    project_dir, source_kind = resolve_story_path(slug, projects_dir)
    corpus = load_context_corpus(project_dir)
    probe_specs = _build_probe_specs(corpus, limit=max_probes)
    probes = [
        _run_probe(project_dir, spec, top_k=top_k)
        for spec in probe_specs
    ]
    hit_count = sum(1 for probe in probes if probe["hit"])
    sample_count = len(probes)
    miss_count = sample_count - hit_count
    hit_rate = round(hit_count / sample_count, 4) if sample_count else 0.0
    failure_samples = [probe for probe in probes if not probe["hit"]]
    status = _status(sample_count, hit_rate)

    return {
        "version": "v0.9.3",
        "story_slug": slug,
        "source_kind": source_kind,
        "status": status,
        "summary": _summary(status),
        "metrics": {
            "sample_count": sample_count,
            "hit_count": hit_count,
            "miss_count": miss_count,
            "hit_rate": hit_rate,
            "canon_ledger_sample_count": len(probe_specs),
            "source_coverage": _source_coverage(probes),
        },
        "probes": probes,
        "failure_samples": failure_samples,
        "recommendations": _recommendations(status),
        "boundaries": [
            "不接 Zep / 图数据库 / GraphRAG。",
            "不接 embedding / 向量库 / reranker。",
            "不改变 run_scene 默认行为与既有 artifact 契约。",
        ],
    }


def _build_probe_specs(corpus: ContextCorpus, *, limit: int) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for item in corpus.canon_ledger:
        if len(specs) >= max(0, limit):
            break
        if not item.entities:
            continue
        query_parts = [
            _preferred_alias(corpus, entity_id)
            for entity_id in item.entities[:3]
        ]
        query = " ".join(part for part in query_parts if part).strip()
        if not query:
            query = item.statement[:40].strip()
        if not query:
            continue
        specs.append(_probe_spec(item, query))
    return specs


def _probe_spec(item: CanonLedgerItem, query: str) -> dict[str, Any]:
    return {
        "query": query,
        "current_chapter": item.chapter,
        "expected_source": "canon_ledger",
        "expected_item_id": f"canon_ledger:{item.id}",
        "expected_entities": list(item.entities),
    }


def _preferred_alias(corpus: ContextCorpus, entity_id: str) -> str:
    aliases = corpus.entity_aliases.aliases_for(entity_id)
    for alias in reversed(aliases):
        if alias and alias != entity_id:
            return alias
    return entity_id


def _run_probe(project_dir: Path, spec: dict[str, Any], *, top_k: int) -> dict[str, Any]:
    result = retrieve_context(
        project_dir,
        str(spec["query"]),
        current_chapter=int(spec["current_chapter"]),
        top_k=top_k,
    )
    items = result.items
    top_item = _compact_item(items[0]) if items else None
    expected_entities = list(spec.get("expected_entities") or [])
    expected_source = str(spec.get("expected_source") or "")
    expected_item_id = str(spec.get("expected_item_id") or "")
    hit = _matches(items, expected_item_id, expected_source, expected_entities)
    return {
        "query": spec["query"],
        "current_chapter": spec["current_chapter"],
        "expected_source": expected_source,
        "expected_item_id": expected_item_id,
        "expected_entities": expected_entities,
        "hit": hit,
        "failure_reason": "" if hit else _failure_reason(
            items,
            expected_item_id,
            expected_source,
            expected_entities,
        ),
        "top_item": top_item,
        "top_sources": _top_sources(items),
        "matched_entities": _matched_entities(items, expected_entities),
    }


def _matches(
    items: list[dict[str, Any]],
    expected_item_id: str,
    expected_source: str,
    expected_entities: list[str],
) -> bool:
    for item in items:
        if expected_item_id and item.get("id") == expected_item_id:
            return True
    has_source = any(item.get("source") == expected_source for item in items)
    matched_entities = _matched_entities(items, expected_entities)
    return has_source and set(expected_entities).issubset(set(matched_entities))


def _failure_reason(
    items: list[dict[str, Any]],
    expected_item_id: str,
    expected_source: str,
    expected_entities: list[str],
) -> str:
    if not items:
        return "no_results"
    if expected_item_id and all(item.get("id") != expected_item_id for item in items):
        return "expected_item_missing"
    if expected_source and all(item.get("source") != expected_source for item in items):
        return "expected_source_missing"
    matched = set(_matched_entities(items, expected_entities))
    if not set(expected_entities).issubset(matched):
        return "expected_entities_missing"
    return "unknown"


def _matched_entities(
    items: list[dict[str, Any]], expected_entities: list[str]
) -> list[str]:
    expected = set(expected_entities)
    matched: set[str] = set()
    for item in items:
        values = set(item.get("resolved_entities") or []) | set(item.get("entities") or [])
        matched.update(values & expected)
    return sorted(matched)


def _compact_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id", ""),
        "source": item.get("source", ""),
        "score": item.get("score", 0.0),
        "chapter": item.get("chapter", 1),
        "text": str(item.get("text") or "")[:160],
        "resolved_entities": item.get("resolved_entities", []),
    }


def _top_sources(items: list[dict[str, Any]]) -> list[str]:
    sources: list[str] = []
    for item in items[:TOP_K]:
        source = str(item.get("source") or "")
        if source and source not in sources:
            sources.append(source)
    return sources


def _source_coverage(probes: list[dict[str, Any]]) -> list[str]:
    sources: set[str] = set()
    for probe in probes:
        sources.update(probe.get("top_sources") or [])
    return sorted(sources)


def _status(sample_count: int, hit_rate: float) -> str:
    if sample_count == 0:
        return "insufficient_samples"
    if hit_rate >= 0.8:
        return "pass"
    return "weak"


def _summary(status: str) -> str:
    if status == "pass":
        return "代表性查询能被当前 BM25、canon ledger 与 entity aliases 命中，暂不触发图记忆替换。"
    if status == "weak":
        return "代表性查询出现召回缺口，应先保存失败样例并扩大评测，再考虑图记忆 spike。"
    return "代表性查询样本不足，尚不能判断当前检索底座是否需要图记忆增强。"


def _recommendations(status: str) -> list[str]:
    if status == "pass":
        return [
            "继续使用当前 BM25、canon ledger 与 entity aliases。",
            "后续只在真实长篇查询失败样例增加时继续 v0.9.3 图记忆评估。",
        ]
    if status == "weak":
        return [
            "先收集失败 query、期望实体与实际 top item，复核是否为别名或账本质量问题。",
            "只有文件型检索修复后仍召回不足，才进入 Zep / 图数据库 / GraphRAG spike。",
        ]
    return [
        "代表性查询样本不足，先补 canon ledger 与 entity aliases 后再复跑 probe。",
        "不要在样本不足时直接引入 Zep / 图数据库 / GraphRAG。",
    ]
