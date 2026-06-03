"""Embedding / Vector Retrieval Readiness Probe.

This report is intentionally read-only. It measures whether the existing
BM25 + canon ledger + entity aliases stack has enough pressure to justify a
later embedding/vector-store spike, but it never creates embeddings, connects a
vector database, or writes project artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from living_novel_engine.retrieval.context_loader import (
    ContextCorpus,
    load_context_corpus,
)
from living_novel_engine.service.project_health import resolve_story_path
from living_novel_engine.service.retrieval_probe import evaluate_retrieval_probes

VERSION = "embedding-vector-readiness-probe-mvp"
LARGE_CHAPTER_THRESHOLD = 50
LARGE_CHARACTER_THRESHOLD = 1_000_000
CORPUS_ITEM_MONITOR_THRESHOLD = 250
FAILURE_SAMPLE_PATH = "memory/retrieval_failure_samples.jsonl"


def get_vector_retrieval_readiness(
    slug: str,
    projects_dir: Path | None = None,
    *,
    max_probes: int = 6,
    top_k: int = 5,
) -> dict[str, Any]:
    """Return a deterministic read-only readiness report for vector retrieval."""

    project_dir, source_kind = resolve_story_path(slug, projects_dir)
    import_status, import_report = _read_json(project_dir / "import_report.json")
    corpus = load_context_corpus(project_dir)
    retrieval_probe = evaluate_retrieval_probes(
        slug,
        projects_dir=projects_dir,
        max_probes=max_probes,
        top_k=top_k,
    )
    failure_status, failure_samples = _read_failure_samples(
        project_dir / FAILURE_SAMPLE_PATH
    )

    chapter_count = _chapter_count(import_report, project_dir)
    character_count = _character_count(import_report, project_dir)
    corpus_item_count = _corpus_item_count(corpus)
    ledger_entity_count = len(
        {
            str(entity)
            for item in corpus.canon_ledger
            for entity in item.entities
            if str(entity).strip()
        }
    )
    alias_entity_count = len(corpus.entity_aliases.entities)
    alias_coverage_ratio = _ratio(alias_entity_count, ledger_entity_count)
    probe_metrics = retrieval_probe.get("metrics") or {}
    probe_hit_rate = float(probe_metrics.get("hit_rate") or 0.0)
    saved_failure_count = len(failure_samples)
    large_project = (
        chapter_count >= LARGE_CHAPTER_THRESHOLD
        or character_count >= LARGE_CHARACTER_THRESHOLD
    )
    corpus_pressure = corpus_item_count >= CORPUS_ITEM_MONITOR_THRESHOLD
    status = _overall_status(
        large_project=large_project,
        corpus_pressure=corpus_pressure,
        retrieval_probe_status=str(retrieval_probe.get("status") or "unknown"),
        saved_failure_count=saved_failure_count,
        alias_status=corpus.entity_aliases.status,
        canon_ledger_count=len(corpus.canon_ledger),
    )
    signals = _signals(
        chapter_count=chapter_count,
        character_count=character_count,
        corpus_item_count=corpus_item_count,
        large_project=large_project,
        corpus_pressure=corpus_pressure,
        retrieval_probe=retrieval_probe,
        saved_failure_count=saved_failure_count,
        failure_status=failure_status,
        alias_status=corpus.entity_aliases.status,
        alias_entity_count=alias_entity_count,
        ledger_entity_count=ledger_entity_count,
        alias_coverage_ratio=alias_coverage_ratio,
    )
    warnings = _warnings(import_status, failure_status, corpus)

    return {
        "version": VERSION,
        "mode": "read_only_vector_retrieval_readiness",
        "status": status,
        "story_slug": slug,
        "source_kind": source_kind,
        "summary": {
            "chapter_count": chapter_count,
            "character_count": character_count,
            "corpus_item_count": corpus_item_count,
            "canon_ledger_count": len(corpus.canon_ledger),
            "legacy_fact_count": len(corpus.facts),
            "chapter_brief_count": len(corpus.summaries),
            "volume_brief_count": len(corpus.volumes),
            "entity_alias_count": alias_entity_count,
            "ledger_entity_count": ledger_entity_count,
            "alias_coverage_ratio": alias_coverage_ratio,
            "retrieval_probe_status": retrieval_probe.get("status") or "unknown",
            "retrieval_probe_sample_count": int(probe_metrics.get("sample_count") or 0),
            "retrieval_probe_hit_rate": probe_hit_rate,
            "saved_failure_sample_count": saved_failure_count,
            "large_project": large_project,
            "corpus_pressure": corpus_pressure,
            "writes_artifacts": False,
            "external_services_required": False,
            "uses_embedding": False,
            "uses_vector_store": False,
            "uses_reranker": False,
            "plaintext_key_returned": False,
        },
        "signals": signals,
        "candidate_layers": _candidate_layers(status, large_project, saved_failure_count),
        "retrieval_probe": _compact_retrieval_probe(retrieval_probe),
        "failure_samples": failure_samples,
        "warnings": warnings,
        "boundaries": [
            "只读读取 import_report、canon ledger、entity aliases、retrieval probe 与可选失败样本。",
            "不生成 embedding，不接向量库，不调用 GraphRAG、Zep、reranker 或真实 LLM。",
            "不写 artifact，不改变 run_scene 默认行为与既有检索注入链路。",
            "即便触发也只建议设计 embedding / 向量库 spike，不直接接生产向量库。",
        ],
        "next_steps": _next_steps(status),
    }


def _read_json(path: Path) -> tuple[str, dict[str, Any]]:
    if not path.exists():
        return "missing", {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "damaged", {}
    return ("ready", data) if isinstance(data, dict) else ("damaged", {})


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
            samples.append(
                {
                    "query": str(data.get("query") or "")[:160],
                    "expected_entities": [
                        str(item)
                        for item in data.get("expected_entities", []) or []
                        if str(item).strip()
                    ][:8],
                    "actual_top_sources": [
                        str(item)
                        for item in data.get("actual_top_sources", []) or []
                        if str(item).strip()
                    ][:8],
                    "reason": str(data.get("reason") or "未记录原因")[:200],
                }
            )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "damaged", []
    return "ready", samples[:8]


def _chapter_count(import_report: dict[str, Any], project_dir: Path) -> int:
    value = import_report.get("total_chapters")
    if isinstance(value, int):
        return max(0, value)
    chapters = import_report.get("chapters")
    if isinstance(chapters, list):
        return len(chapters)
    source_dir = project_dir / "source"
    if source_dir.is_dir():
        return len([path for path in source_dir.iterdir() if path.is_file()])
    return 0


def _character_count(import_report: dict[str, Any], project_dir: Path) -> int:
    value = import_report.get("total_characters")
    if isinstance(value, int):
        return max(0, value)
    source_dir = project_dir / "source"
    if not source_dir.is_dir():
        return 0
    total = 0
    for path in source_dir.iterdir():
        if not path.is_file():
            continue
        try:
            total += len(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
    return total


def _corpus_item_count(corpus: ContextCorpus) -> int:
    contract_count = 0
    if corpus.contract:
        contract_count += len(corpus.contract.world_rules)
        contract_count += len(corpus.contract.power_system_limits)
        contract_count += len(corpus.contract.forbidden_additions)
        contract_count += len(corpus.contract.unresolved_threads)
        contract_count += sum(
            len(boundaries)
            for boundaries in corpus.contract.character_boundaries.values()
        )
    return (
        len(corpus.facts)
        + len(corpus.canon_ledger)
        + len(corpus.summaries)
        + len(corpus.volumes)
        + contract_count
    )


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 1.0 if numerator > 0 else 0.0
    return round(min(1.0, numerator / denominator), 4)


def _overall_status(
    *,
    large_project: bool,
    corpus_pressure: bool,
    retrieval_probe_status: str,
    saved_failure_count: int,
    alias_status: str,
    canon_ledger_count: int,
) -> str:
    if saved_failure_count > 0 or retrieval_probe_status == "weak":
        return "triggered"
    if alias_status != "ready" or canon_ledger_count == 0:
        return "attention"
    if large_project or corpus_pressure:
        return "monitor"
    if retrieval_probe_status == "insufficient_samples":
        return "attention"
    return "ready"


def _signals(
    *,
    chapter_count: int,
    character_count: int,
    corpus_item_count: int,
    large_project: bool,
    corpus_pressure: bool,
    retrieval_probe: dict[str, Any],
    saved_failure_count: int,
    failure_status: str,
    alias_status: str,
    alias_entity_count: int,
    ledger_entity_count: int,
    alias_coverage_ratio: float,
) -> list[dict[str, Any]]:
    probe_status = str(retrieval_probe.get("status") or "unknown")
    probe_metrics = retrieval_probe.get("metrics") or {}
    return [
        {
            "id": "corpus_scale",
            "label": "长篇规模",
            "status": "attention" if large_project or corpus_pressure else "ready",
            "evidence": (
                f"{chapter_count} 章 / {character_count} 字 / {corpus_item_count} 条检索语料"
            ),
            "next_step": (
                "进入召回压力监控，不直接接向量库。"
                if large_project or corpus_pressure
                else "继续积累真实章节和检索样例。"
            ),
            "detail": {
                "large_chapter_threshold": LARGE_CHAPTER_THRESHOLD,
                "large_character_threshold": LARGE_CHARACTER_THRESHOLD,
                "corpus_item_monitor_threshold": CORPUS_ITEM_MONITOR_THRESHOLD,
            },
        },
        {
            "id": "bm25_probe",
            "label": "BM25 账本探针",
            "status": "attention" if probe_status in {"weak", "insufficient_samples"} else "ready",
            "evidence": (
                f"{probe_metrics.get('hit_count', 0)} / {probe_metrics.get('sample_count', 0)} 命中"
            ),
            "next_step": (
                "先保存失败 query 与期望实体，再评估 embedding / 向量检索。"
                if probe_status == "weak"
                else "补 canon ledger 与 entity aliases 后复跑。"
                if probe_status == "insufficient_samples"
                else "继续使用当前 BM25、canon ledger 与 entity aliases。"
            ),
            "detail": {
                "probe_status": probe_status,
                "hit_rate": probe_metrics.get("hit_rate", 0.0),
            },
        },
        {
            "id": "saved_failure_samples",
            "label": "召回失败样本",
            "status": "attention" if saved_failure_count > 0 else "ready",
            "evidence": (
                f"已记录 {saved_failure_count} 条换说法/语义召回失败"
                if saved_failure_count
                else f"{FAILURE_SAMPLE_PATH} 未记录失败样本"
            ),
            "next_step": (
                "用失败样本设计 mockable embedding / 向量库 spike。"
                if saved_failure_count
                else "出现换说法召回失败时先记录样本，不急着接重型服务。"
            ),
            "detail": {"source": FAILURE_SAMPLE_PATH, "source_status": failure_status},
        },
        {
            "id": "alias_coverage",
            "label": "别名覆盖",
            "status": "ready" if alias_status == "ready" and alias_coverage_ratio >= 0.8 else "attention",
            "evidence": (
                f"{alias_entity_count} 个别名实体覆盖 {ledger_entity_count} 个账本实体"
            ),
            "next_step": (
                "先补 entity aliases；别名问题不应直接归因给 embedding。"
                if alias_status != "ready" or alias_coverage_ratio < 0.8
                else "继续用别名归一化支撑 BM25。"
            ),
            "detail": {
                "alias_status": alias_status,
                "alias_coverage_ratio": alias_coverage_ratio,
            },
        },
    ]


def _candidate_layers(
    status: str, large_project: bool, saved_failure_count: int
) -> list[dict[str, Any]]:
    embedding_state = (
        "evaluate"
        if status == "triggered"
        else "monitor"
        if large_project
        else "deferred"
    )
    vector_state = "evaluate" if status == "triggered" and large_project else "deferred"
    if status == "triggered" and saved_failure_count > 0:
        vector_state = "design_spike"
    return [
        {
            "id": "embedding",
            "label": "Embedding",
            "readiness": embedding_state,
            "reason": (
                "已有换说法召回失败样本，可做 mockable embedding 对照实验。"
                if status == "triggered"
                else "项目规模进入监控，但尚无明确 BM25 失败证据。"
                if large_project
                else "当前 BM25 + 别名 + 账本仍够用。"
            ),
        },
        {
            "id": "vector_store",
            "label": "向量库",
            "readiness": vector_state,
            "reason": (
                "先用本地失败样本验证 embedding 收益，再决定是否需要 Qdrant/Milvus 等存储层。"
                if status == "triggered"
                else "未出现需要持久向量索引的召回压力。"
            ),
        },
        {
            "id": "reranker",
            "label": "Reranker",
            "readiness": "deferred",
            "reason": "Prompt Budget Pack 已做只读压缩；只有预算排除关键事实时再评估 reranker。",
        },
        {
            "id": "graphrag_zep",
            "label": "GraphRAG / Zep",
            "readiness": "deferred",
            "reason": "关系、伏笔和因果错乱继续走 Graph Memory Evaluation 触发式评估。",
        },
    ]


def _compact_retrieval_probe(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": report.get("status") or "unknown",
        "summary": report.get("summary") or "",
        "metrics": report.get("metrics") or {},
        "failure_samples": (report.get("failure_samples") or [])[:3],
    }


def _warnings(
    import_status: str, failure_status: str, corpus: ContextCorpus
) -> list[str]:
    warnings: list[str] = []
    if import_status == "missing":
        warnings.append("import_report.json 缺失，规模判断已降级。")
    elif import_status == "damaged":
        warnings.append("import_report.json 损坏，规模判断已降级。")
    if failure_status == "damaged":
        warnings.append(f"{FAILURE_SAMPLE_PATH} 损坏，已忽略失败样本。")
    if corpus.entity_aliases.status != "ready":
        warnings.append("entity_aliases.yaml 缺失或损坏，先修复别名层。")
    if not corpus.canon_ledger:
        warnings.append("canon_ledger.jsonl 缺失或为空，先修复正史账本。")
    return warnings


def _next_steps(status: str) -> list[str]:
    if status == "triggered":
        return [
            "先把失败 query、期望实体、实际 top item 固化为评测样本。",
            "做 deterministic/mockable 的 embedding / 向量库 spike，对比 BM25 命中率和 prompt budget 占用。",
            "spike 通过前继续使用当前 BM25、canon ledger 与 entity aliases。",
        ]
    if status == "monitor":
        return [
            "继续使用当前 BM25、canon ledger 与 entity aliases。",
            "开始记录换说法召回失败样本，避免过早接向量库。",
            "当失败样本稳定复现后，再进入 embedding / 向量检索 spike。",
        ]
    if status == "attention":
        return [
            "先修复 canon ledger、entity aliases 或检索探针样本。",
            "不要把基础记忆缺口误判为向量检索需求。",
        ]
    return [
        "继续使用当前 BM25、canon ledger 与 entity aliases。",
        "暂不接 embedding、向量库、GraphRAG、Zep 或 reranker。",
    ]
