"""Embedding Mock Evaluation Report MVP.

Turns local retrieval failure samples into a read-only report that explains
whether deterministic mock semantic matching shows enough signal to continue
toward a real embedding spike. It never calls providers or writes artifacts.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.retrieval_sample_export_pack import (
    get_retrieval_sample_export_pack,
)

VERSION = "embedding-mock-evaluation-report-mvp"
DEFAULT_MIN_CANDIDATES = 1


class EmbeddingMockEvaluationReportRequestError(ValueError):
    """Invalid embedding mock evaluation report request, mapped to HTTP 400."""


def get_embedding_mock_evaluation_report(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
    min_candidates: int = DEFAULT_MIN_CANDIDATES,
) -> dict[str, Any]:
    """Return a read-only mock evaluation report for local failure samples."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    export_pack = get_retrieval_sample_export_pack(
        sid,
        projects_dir=projects_dir,
        now=now,
    )
    summary = _summary(export_pack)
    status = _status(export_pack, summary, min_candidates)
    buckets = _buckets(export_pack)
    gate = _gate(status, summary, min_candidates)
    report_md = _report_md(sid, generated_at, status, summary, gate, buckets)

    return {
        "version": VERSION,
        "mode": "read_only_embedding_mock_evaluation_report",
        "status": status,
        "story_slug": sid,
        "source_kind": export_pack.get("source_kind", ""),
        "generated_at": generated_at,
        "summary": summary,
        "gate": gate,
        "buckets": buckets,
        "report_md": report_md,
        "export_pack": {
            "status": export_pack.get("status", ""),
            "filename": export_pack.get("filename", ""),
            "content_type": export_pack.get("content_type", ""),
        },
        "warnings": list(export_pack.get("warnings") or []),
        "boundaries": [
            "只读汇总本地失败样本、BM25 命中与 mock semantic oracle。",
            "不写 artifact，不生成 embedding，不创建向量索引。",
            "不连接向量库、reranker、GraphRAG 或长期记忆服务。",
            "不读取、不返回也不记录明文 Key。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise EmbeddingMockEvaluationReportRequestError("invalid slug")
    return sid


def _summary(export_pack: dict[str, Any]) -> dict[str, Any]:
    raw = export_pack.get("summary") or {}
    sample_count = int(raw.get("sample_count") or 0)
    lexical_gap_count = int(raw.get("lexical_gap_count") or 0)
    memory_gap_count = int(raw.get("memory_gap_count") or 0)
    already_covered_count = int(raw.get("already_covered_count") or 0)
    invalid_sample_count = int(raw.get("invalid_sample_count") or 0)
    return {
        "sample_count": sample_count,
        "bm25_hit_count": int(raw.get("bm25_hit_count") or 0),
        "mock_embedding_hit_count": int(raw.get("mock_embedding_hit_count") or 0),
        "lexical_gap_count": lexical_gap_count,
        "memory_gap_count": memory_gap_count,
        "already_covered_count": already_covered_count,
        "invalid_sample_count": invalid_sample_count,
        "lexical_gap_rate": _ratio(lexical_gap_count, sample_count),
        "memory_gap_rate": _ratio(memory_gap_count, sample_count),
        "writes_artifacts": False,
        "external_services_required": False,
        "uses_embedding_provider": False,
        "uses_vector_store": False,
        "plaintext_key_returned": False,
    }


def _status(
    export_pack: dict[str, Any],
    summary: dict[str, Any],
    min_candidates: int,
) -> str:
    if export_pack.get("status") == "blocked" or summary["invalid_sample_count"] > 0:
        return "blocked"
    if summary["sample_count"] == 0:
        return "empty"
    if summary["lexical_gap_count"] >= max(1, min_candidates):
        return "candidate"
    if summary["memory_gap_count"] > 0:
        return "attention"
    return "covered"


def _gate(
    status: str,
    summary: dict[str, Any],
    min_candidates: int,
) -> dict[str, Any]:
    threshold = max(1, min_candidates)
    status_map = {
        "candidate": "candidate",
        "empty": "needs_samples",
        "attention": "needs_memory",
        "blocked": "blocked",
        "covered": "covered",
    }
    reason_map = {
        "candidate": "mock semantic oracle 能命中 BM25 未命中的本地失败样本。",
        "empty": "暂无失败样本，无法判断 embedding 收益。",
        "attention": "存在记忆缺口，先补 canon ledger 或 expected_entities。",
        "blocked": "样本损坏或必填字段缺失，先修复样本。",
        "covered": "当前样本已被 BM25 覆盖，暂不需要 embedding spike。",
    }
    return {
        "id": "mock_embedding_candidate",
        "status": status_map.get(status, status),
        "passed": status == "candidate",
        "reason": reason_map.get(status, "需要人工复核样本状态。"),
        "min_candidates_required": threshold,
        "sample_count": summary["sample_count"],
        "lexical_gap_count": summary["lexical_gap_count"],
    }


def _buckets(export_pack: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {
        "lexical_gap": [],
        "memory_gap": [],
        "already_covered": [],
        "invalid_sample": [],
    }
    manifest = export_pack.get("manifest") or {}
    for sample in manifest.get("samples") or []:
        diagnosis = str(sample.get("diagnosis") or "")
        item = {
            "query": sample.get("query", ""),
            "expected_entities": list(sample.get("expected_entities") or []),
            "target_item_id": sample.get("target_item_id", ""),
            "target_statement": sample.get("target_statement", ""),
            "reason": sample.get("reason", ""),
        }
        buckets.setdefault(diagnosis, []).append(item)
    return {key: value[:20] for key, value in buckets.items()}


def _report_md(
    story_slug: str,
    generated_at: str,
    status: str,
    summary: dict[str, Any],
    gate: dict[str, Any],
    buckets: dict[str, list[dict[str, Any]]],
) -> str:
    lines = [
        f"# {story_slug} Mock Embedding 对照报告",
        "",
        f"- 生成时间：{generated_at}",
        f"- 状态：{status}",
        f"- 样本数：{summary['sample_count']}",
        f"- 词面缺口：{summary['lexical_gap_count']}",
        f"- 记忆缺口：{summary['memory_gap_count']}",
        f"- Gate：{gate['status']}（{'通过' if gate['passed'] else '未通过'}）",
        "",
        "## 结论",
        "",
        _conclusion(status),
        "",
        "## 词面缺口样本",
        "",
    ]
    lexical_samples = buckets.get("lexical_gap") or []
    if not lexical_samples:
        lines.append("暂无失败样本。" if summary["sample_count"] == 0 else "暂无词面缺口样本。")
    else:
        for sample in lexical_samples:
            lines.append(
                f"- {sample.get('query', '')} -> {sample.get('target_item_id', '')}："
                f"{sample.get('target_statement', '')}"
            )
    lines.extend(
        [
            "",
            "## 边界",
            "",
            "- 本报告只比较 BM25 与 deterministic mock semantic oracle。",
            "- 不调用真实 embedding，不连接向量库，不改变当前检索链路。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _conclusion(status: str) -> str:
    if status == "candidate":
        return "mock embedding 值得进入下一步评估；先扩大样本并做批量 replay，再考虑真实 provider。"
    if status == "empty":
        return "暂无失败样本，先从工作台或 CLI 记录换说法召回失败 query。"
    if status == "attention":
        return "当前更像记忆资料缺口，先补账本事实，再判断 embedding 收益。"
    if status == "blocked":
        return "样本格式或必填字段需要修复，暂不进入 embedding 评估。"
    return "当前样本已被 BM25 覆盖，暂不需要 embedding spike。"


def _next_steps(status: str) -> list[str]:
    if status == "candidate":
        return [
            "继续增加不同章节、不同实体的 lexical_gap 样本。",
            "下一步做 Retrieval Sample Replay Report，批量复跑并记录趋势。",
            "真实 embedding provider 仍需等 mock report 稳定后再 opt-in。",
        ]
    if status == "attention":
        return [
            "先补 canon ledger 或 expected_entities，让样本能定位目标事实。",
            "不要把记忆缺口误判为 embedding 收益。",
        ]
    if status == "blocked":
        return ["先修复样本 JSONL 格式和必填字段。"]
    if status == "covered":
        return ["当前样本已被 BM25 覆盖，继续收集未覆盖的换说法失败 query。"]
    return ["先记录本地失败样本，再生成 mock 对照报告。"]


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)
