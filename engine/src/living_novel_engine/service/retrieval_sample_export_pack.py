"""Retrieval Sample Export Pack MVP.

Builds a read-only Markdown/manifest export from local retrieval failure
samples and the deterministic embedding evaluation report. It never writes
artifacts, creates embeddings, connects vector stores, or reads provider keys.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.embedding_evaluation_samples import (
    get_embedding_evaluation_samples,
)

VERSION = "retrieval-sample-export-pack-mvp"


class RetrievalSampleExportPackRequestError(ValueError):
    """Invalid retrieval sample export request, mapped to HTTP 400."""


def get_retrieval_sample_export_pack(
    slug: str,
    *,
    projects_dir: Any | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a read-only Markdown and manifest export for failure samples."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    evaluation = get_embedding_evaluation_samples(sid, projects_dir=projects_dir)
    summary = _summary(evaluation)
    status = _status(evaluation, summary)
    manifest = _manifest(sid, generated_at, evaluation, summary, status)
    content_md = _content_md(sid, generated_at, evaluation, summary, status)

    return {
        "version": VERSION,
        "mode": "read_only_retrieval_sample_export_pack",
        "status": status,
        "story_slug": sid,
        "source_kind": evaluation.get("source_kind", ""),
        "filename": f"{sid}-retrieval-samples.md",
        "content_type": "text/markdown; charset=utf-8",
        "summary": summary,
        "manifest": manifest,
        "content_md": content_md,
        "warnings": list(evaluation.get("warnings") or []),
        "boundaries": [
            "只读整理本地失败样本与 deterministic 对照结果。",
            "不写 artifact，不生成 embedding，不创建向量索引。",
            "不连接向量库、reranker、GraphRAG 或长期记忆服务。",
            "不读取、不返回也不记录明文 Key。",
        ],
        "next_steps": _next_steps(status, summary),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise RetrievalSampleExportPackRequestError("invalid slug")
    return sid


def _summary(evaluation: dict[str, Any]) -> dict[str, Any]:
    raw = evaluation.get("summary") or {}
    sample_count = int(raw.get("sample_count") or 0)
    lexical_gap_count = int(raw.get("lexical_gap_count") or 0)
    memory_gap_count = int(raw.get("memory_gap_count") or 0)
    already_covered_count = sum(
        1
        for sample in evaluation.get("samples") or []
        if sample.get("diagnosis") == "already_covered"
    )
    invalid_sample_count = int(raw.get("invalid_sample_count") or 0)
    return {
        "sample_status": raw.get("sample_status") or "unknown",
        "sample_count": sample_count,
        "bm25_hit_count": int(raw.get("bm25_hit_count") or 0),
        "mock_embedding_hit_count": int(raw.get("mock_embedding_hit_count") or 0),
        "lexical_gap_count": lexical_gap_count,
        "memory_gap_count": memory_gap_count,
        "already_covered_count": already_covered_count,
        "invalid_sample_count": invalid_sample_count,
        "writes_artifacts": False,
        "external_services_required": False,
        "uses_embedding_provider": False,
        "uses_vector_store": False,
        "plaintext_key_returned": False,
    }


def _status(evaluation: dict[str, Any], summary: dict[str, Any]) -> str:
    if evaluation.get("status") == "blocked" or summary["invalid_sample_count"] > 0:
        return "blocked"
    if summary["sample_count"] == 0:
        return "empty"
    if summary["lexical_gap_count"] > 0:
        return "ready"
    return "attention"


def _manifest(
    story_slug: str,
    generated_at: str,
    evaluation: dict[str, Any],
    summary: dict[str, Any],
    status: str,
) -> dict[str, Any]:
    samples = [
        {
            "query": sample.get("query", ""),
            "expected_entities": list(sample.get("expected_entities") or []),
            "expected_item_id": sample.get("expected_item_id", ""),
            "expected_source": sample.get("expected_source", ""),
            "current_chapter": sample.get("current_chapter", 1),
            "reason": sample.get("reason", ""),
            "diagnosis": sample.get("diagnosis", ""),
            "bm25_hit": bool(sample.get("bm25_hit")),
            "mock_embedding_hit": bool(sample.get("mock_embedding_hit")),
            "target_item_id": sample.get("target_item_id", ""),
            "target_statement": sample.get("target_statement", ""),
            "actual_top_sources": list(sample.get("actual_top_sources") or []),
        }
        for sample in evaluation.get("samples") or []
    ]
    return {
        "version": VERSION,
        "story_slug": story_slug,
        "generated_at": generated_at,
        "status": status,
        "summary": summary,
        "sample_schema": evaluation.get("sample_schema") or {},
        "samples": samples,
    }


def _content_md(
    story_slug: str,
    generated_at: str,
    evaluation: dict[str, Any],
    summary: dict[str, Any],
    status: str,
) -> str:
    lines = [
        f"# {story_slug} 检索失败样本导出包",
        "",
        f"- 生成时间：{generated_at}",
        f"- 状态：{status}",
        f"- 样本数：{summary['sample_count']}",
        f"- 词面缺口：{summary['lexical_gap_count']}",
        f"- 记忆缺口：{summary['memory_gap_count']}",
        f"- 已覆盖：{summary['already_covered_count']}",
        "",
        "## 边界",
        "",
        "- 只读导出，不写项目 artifact。",
        "- 不生成 embedding，不连接向量库，不调用外部 provider。",
        "- 本报告用于迁移失败 query、形成 mock 对照评测集或人工复盘。",
        "",
    ]
    samples = list(evaluation.get("samples") or [])
    if not samples:
        lines.extend(
            [
                "## 样本",
                "",
                "暂无失败样本。先在工作台或 `lne memory add-sample` 记录换说法失败 query。",
                "",
            ]
        )
        return "\n".join(lines).rstrip() + "\n"

    lines.extend(["## 样本", ""])
    for index, sample in enumerate(samples, start=1):
        lines.extend(
            [
                f"### {index}. {sample.get('diagnosis', 'unknown')}",
                "",
                f"- 查询：{_inline(sample.get('query'))}",
                f"- 期望实体：{_join(sample.get('expected_entities'))}",
                f"- 当前章节：{sample.get('current_chapter', 1)}",
                f"- BM25 命中：{'是' if sample.get('bm25_hit') else '否'}",
                f"- Mock 语义命中：{'是' if sample.get('mock_embedding_hit') else '否'}",
                f"- 目标项：{_inline(sample.get('target_item_id'))}",
                f"- 目标事实：{_inline(sample.get('target_statement'))}",
                f"- 原因：{_inline(sample.get('reason'))}",
                "",
            ]
        )
        top_items = list(sample.get("top_items") or [])[:3]
        if top_items:
            lines.extend(["Top BM25 结果：", ""])
            for item in top_items:
                lines.append(
                    f"- `{item.get('source', '')}` {round(float(item.get('score') or 0.0), 4)}："
                    f"{_inline(item.get('text'))}"
                )
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _next_steps(status: str, summary: dict[str, Any]) -> list[str]:
    if status == "ready":
        return [
            "把该导出包作为 mock embedding 对照评测集输入。",
            "继续积累不同换说法 query，避免单一样本驱动真实向量化决策。",
            "样本稳定后再评估真实 embedding provider 或向量库。",
        ]
    if status == "attention":
        return [
            "先区分样本是已被 BM25 覆盖还是 canon ledger 缺事实。",
            "不要把记忆缺口直接归因给 embedding 能力缺口。",
        ]
    if status == "blocked":
        return [
            "先修复 retrieval_failure_samples.jsonl 的格式或必填字段。",
        ]
    return [
        "先记录换说法召回失败样本。",
        "再用 `lne memory samples --require-candidate` 复跑候选检查。",
    ]


def _inline(value: Any) -> str:
    text = str(value or "").strip()
    return text if text else "无"


def _join(value: Any) -> str:
    items = [str(item) for item in value or [] if str(item).strip()]
    return "、".join(items) if items else "无"
