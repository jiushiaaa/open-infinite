"""Retrieval Sample Replay Report MVP.

Replays local retrieval failure samples against the current deterministic
retrieval evaluation and turns them into stable cases for future comparison.
It never writes history, calls providers, or creates vector indexes.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.embedding_evaluation_samples import (
    get_embedding_evaluation_samples,
)

VERSION = "retrieval-sample-replay-report-mvp"


class RetrievalSampleReplayReportRequestError(ValueError):
    """Invalid retrieval sample replay report request, mapped to HTTP 400."""


def get_retrieval_sample_replay_report(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a read-only replay report for saved retrieval failure samples."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    evaluation = get_embedding_evaluation_samples(sid, projects_dir=projects_dir)
    cases = _cases(evaluation)
    summary = _summary(cases)
    status = _status(evaluation, summary)
    gate = _gate(status, summary)
    report_md = _report_md(sid, generated_at, status, summary, gate, cases)

    return {
        "version": VERSION,
        "mode": "read_only_retrieval_sample_replay_report",
        "status": status,
        "story_slug": sid,
        "source_kind": evaluation.get("source_kind", ""),
        "generated_at": generated_at,
        "summary": summary,
        "replay_gate": gate,
        "cases": cases,
        "report_md": report_md,
        "warnings": list(evaluation.get("warnings") or []),
        "boundaries": [
            "只读复跑本地失败样本，不写 replay 历史 artifact。",
            "不生成 embedding，不创建向量索引，不连接向量库或 reranker。",
            "不读取、不返回也不记录明文 Key。",
            "不替换 retrieve_context，不改变 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise RetrievalSampleReplayReportRequestError("invalid slug")
    return sid


def _cases(evaluation: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for index, sample in enumerate(evaluation.get("samples") or [], start=1):
        diagnosis = str(sample.get("diagnosis") or "")
        replay_status = _replay_status(diagnosis)
        cases.append(
            {
                "case_id": f"retrieval-case-{index:03d}",
                "query": sample.get("query", ""),
                "expected_entities": list(sample.get("expected_entities") or []),
                "current_chapter": sample.get("current_chapter", 1),
                "diagnosis": diagnosis,
                "replay_status": replay_status,
                "bm25_hit": bool(sample.get("bm25_hit")),
                "mock_embedding_hit": bool(sample.get("mock_embedding_hit")),
                "target_item_id": sample.get("target_item_id", ""),
                "target_statement": sample.get("target_statement", ""),
                "reason": sample.get("reason", ""),
            }
        )
    return cases[:50]


def _replay_status(diagnosis: str) -> str:
    return {
        "lexical_gap": "still_failing_lexically",
        "memory_gap": "missing_memory_target",
        "already_covered": "covered_by_current_retrieval",
        "invalid_sample": "invalid_case",
    }.get(diagnosis, "needs_review")


def _summary(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "case_count": len(cases),
        "still_failing_lexically_count": _count(cases, "still_failing_lexically"),
        "missing_memory_target_count": _count(cases, "missing_memory_target"),
        "covered_by_current_retrieval_count": _count(cases, "covered_by_current_retrieval"),
        "invalid_case_count": _count(cases, "invalid_case"),
        "needs_review_count": _count(cases, "needs_review"),
        "writes_artifacts": False,
        "external_services_required": False,
        "uses_embedding_provider": False,
        "uses_vector_store": False,
        "plaintext_key_returned": False,
    }


def _status(evaluation: dict[str, Any], summary: dict[str, Any]) -> str:
    if evaluation.get("status") == "blocked" or summary["invalid_case_count"] > 0:
        return "blocked"
    if summary["case_count"] == 0:
        return "empty"
    if summary["missing_memory_target_count"] > 0 or summary["needs_review_count"] > 0:
        return "attention"
    return "ready"


def _gate(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    status_map = {
        "ready": "clean",
        "empty": "needs_samples",
        "attention": "needs_review",
        "blocked": "blocked",
    }
    return {
        "id": "retrieval_sample_replay_clean",
        "status": status_map.get(status, status),
        "passed": status == "ready",
        "reason": _gate_reason(status),
        "case_count": summary["case_count"],
        "invalid_case_count": summary["invalid_case_count"],
    }


def _gate_reason(status: str) -> str:
    if status == "ready":
        return "样本可复跑，未发现损坏 case；当前词面缺口可作为后续 replay 趋势基线。"
    if status == "empty":
        return "暂无失败样本，无法生成 replay case。"
    if status == "attention":
        return "存在记忆缺口或未知诊断，需要人工复核。"
    return "存在损坏样本或无效 case，先修复样本。"


def _report_md(
    story_slug: str,
    generated_at: str,
    status: str,
    summary: dict[str, Any],
    gate: dict[str, Any],
    cases: list[dict[str, Any]],
) -> str:
    lines = [
        f"# {story_slug} 检索失败样本复跑报告",
        "",
        f"- 生成时间：{generated_at}",
        f"- 状态：{status}",
        f"- Case 数：{summary['case_count']}",
        f"- 仍是词面缺口：{summary['still_failing_lexically_count']}",
        f"- 已被当前检索覆盖：{summary['covered_by_current_retrieval_count']}",
        f"- Gate：{gate['status']}（{'通过' if gate['passed'] else '未通过'}）",
        "",
        "## Cases",
        "",
    ]
    if not cases:
        lines.append("暂无失败样本。")
    for case in cases:
        lines.append(
            f"- {case['case_id']} · {case['replay_status']}：{case['query']} -> "
            f"{case.get('target_item_id') or '无目标'}"
        )
    lines.extend(
        [
            "",
            "## 边界",
            "",
            "- 本报告只复跑当前本地检索与 mock 对照结果。",
            "- 不写历史记录，不调用真实 embedding，不连接向量库。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _next_steps(status: str) -> list[str]:
    if status == "ready":
        return [
            "把该报告作为当前 retrieval 行为的 replay 基线。",
            "后续检索策略变化后再复跑，比较仍失败、已覆盖和记忆缺口数量。",
            "样本稳定后可做 Migration Pack，形成跨项目评测集。",
        ]
    if status == "attention":
        return ["先复核 memory_gap 或 needs_review case，再进入迁移评测集。"]
    if status == "blocked":
        return ["先修复无效样本，再复跑 replay report。"]
    return ["先记录本地失败样本，再生成 replay report。"]


def _count(cases: list[dict[str, Any]], status: str) -> int:
    return sum(1 for case in cases if case.get("replay_status") == status)
