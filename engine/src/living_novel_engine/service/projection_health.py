"""Projection Health MVP：分支生成后的只读投影健康报告。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.project_health import resolve_story_path

VERSION = "projection-health-mvp"


class ProjectionHealthRequestError(ValueError):
    """Invalid projection health request, mapped to HTTP 400."""


def get_projection_health(
    run_id: str,
    branch_id: str,
    *,
    outputs_root: Path | None = None,
    projects_dir: Path | None = None,
) -> dict[str, Any]:
    """Return a read-only health report for one generated branch.

    The report checks whether chapter, event, state, ledger, and audit
    projections are present and parseable. It never writes artifacts, mutates
    ``state_snapshot.json``, replaces ``canon_ledger.jsonl``, or calls external
    services.
    """

    rid = _safe_id(run_id, "run_id")
    bid = _safe_id(branch_id, "branch_id")
    root = outputs_root or outputs_dir()
    run_dir = root / rid
    if not run_dir.is_dir():
        raise FileNotFoundError(f"运行不存在: {rid}")
    branch_dir = run_dir / bid
    if not branch_dir.is_dir():
        raise FileNotFoundError(f"分支不存在: {rid}/{bid}")

    story_slug = _infer_story_slug(run_dir)
    project_dir, source_kind, project_status = _resolve_project(
        story_slug,
        projects_dir=projects_dir,
    )
    checks = [
        _chapter_check(branch_dir),
        _events_check(branch_dir),
        _state_snapshot_check(branch_dir),
        _causal_diff_check(branch_dir),
        _multi_agent_trace_check(branch_dir),
        _runtime_memory_check(branch_dir),
        _narrative_diagnostics_check(branch_dir),
        _worldline_judgement_check(branch_dir),
        _canon_ledger_check(project_dir, project_status),
        _audit_log_check(project_dir, project_status),
    ]
    counts = {
        "ready": sum(1 for item in checks if item["status"] == "ready"),
        "attention": sum(1 for item in checks if item["status"] == "attention"),
        "blocked": sum(1 for item in checks if item["status"] == "blocked"),
    }
    status = "blocked" if counts["blocked"] else "attention" if counts["attention"] else "ready"
    return {
        "version": VERSION,
        "mode": "read_only_projection_health",
        "status": status,
        "run_id": rid,
        "branch_id": bid,
        "story_slug": story_slug or "",
        "source_kind": source_kind,
        "summary": {
            "check_count": len(checks),
            "ready_count": counts["ready"],
            "attention_count": counts["attention"],
            "blocked_count": counts["blocked"],
            "writes_artifacts": False,
            "mutates_state_snapshot": False,
            "replaces_canon_ledger": False,
            "external_services_required": False,
        },
        "checks": checks,
        "warnings": _warnings(checks),
        "boundaries": [
            "只读检查现有 branch/project artifact，不写入新文件。",
            "不替换 canon_ledger.jsonl，不覆盖 state_snapshot.json。",
            "不调用真实 LLM、Seedream、向量库、GraphRAG、Zep 或 reranker。",
            "HTTP 标识符先经过安全校验，再解析本地路径。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_id(value: str, label: str) -> str:
    checked = safe_id(str(value or ""))
    if checked is None:
        raise ProjectionHealthRequestError(f"invalid {label}")
    return checked


def _checkpoint(
    *,
    checkpoint_id: str,
    label: str,
    status: str,
    artifact: str,
    evidence: str,
    next_step: str,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": checkpoint_id,
        "label": label,
        "status": status,
        "status_label": {
            "ready": "已具备",
            "attention": "需留意",
            "blocked": "需修复",
        }.get(status, status),
        "source_artifact": artifact,
        "evidence": evidence,
        "next_step": next_step,
        "detail": detail or {},
    }


def _read_json_status(path: Path) -> tuple[str, dict[str, Any]]:
    if not path.exists():
        return "missing", {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "damaged", {}
    return ("ready", data) if isinstance(data, dict) else ("damaged", {})


def _count_jsonl(path: Path) -> tuple[str, int]:
    if not path.exists():
        return "missing", 0
    count = 0
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            json.loads(line)
            count += 1
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "damaged", 0
    return "ready", count


def _infer_story_slug(run_dir: Path) -> str | None:
    for filename in ("meta.json", "intervention.json"):
        status, data = _read_json_status(run_dir / filename)
        if status != "ready":
            continue
        raw = data.get("story_slug") or data.get("sample_slug")
        slug = safe_id(str(raw or ""))
        if slug:
            return slug
    return None


def _resolve_project(
    story_slug: str | None,
    *,
    projects_dir: Path | None,
) -> tuple[Path | None, str, str]:
    if not story_slug:
        return None, "unknown", "missing"
    try:
        project_dir, source_kind = resolve_story_path(story_slug, projects_dir)
    except FileNotFoundError:
        return None, "unknown", "missing"
    return project_dir, source_kind, "ready"


def _chapter_check(branch_dir: Path) -> dict[str, Any]:
    path = branch_dir / "chapter.md"
    if not path.exists():
        return _checkpoint(
            checkpoint_id="chapter",
            label="章节正文",
            status="blocked",
            artifact="chapter.md",
            evidence="chapter.md 缺失",
            next_step="先重新生成或修复分支正文，再进入提交或导出。",
            detail={"artifact_status": "missing", "char_count": 0},
        )
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return _checkpoint(
            checkpoint_id="chapter",
            label="章节正文",
            status="blocked",
            artifact="chapter.md",
            evidence="chapter.md 无法读取",
            next_step="修复章节文件编码或重新生成该分支。",
            detail={"artifact_status": "damaged", "char_count": 0},
        )
    char_count = len(text.strip())
    return _checkpoint(
        checkpoint_id="chapter",
        label="章节正文",
        status="ready" if char_count else "blocked",
        artifact="chapter.md",
        evidence=f"{char_count} 字符" if char_count else "chapter.md 为空",
        next_step="章节正文可用于后续导出与投影核对。" if char_count else "补齐正文后再继续。",
        detail={"artifact_status": "ready", "char_count": char_count},
    )


def _events_check(branch_dir: Path) -> dict[str, Any]:
    status, data = _read_json_status(branch_dir / "events.json")
    event_count = _list_count(data, ("accepted_events", "events", "generated_events"))
    return _checkpoint(
        checkpoint_id="events",
        label="事件投影",
        status="ready" if status == "ready" else "blocked",
        artifact="events.json",
        evidence=(
            f"{event_count} 条事件"
            if status == "ready"
            else "events.json 损坏"
            if status == "damaged"
            else "events.json 缺失"
        ),
        next_step=(
            "事件投影可用于节奏、因果和章节提交前核对。"
            if status == "ready"
            else "重新生成或修复 events.json，避免提交后事件链断裂。"
        ),
        detail={"artifact_status": status, "event_count": event_count},
    )


def _state_snapshot_check(branch_dir: Path) -> dict[str, Any]:
    status, data = _read_json_status(branch_dir / "state_snapshot.json")
    characters = data.get("characters")
    character_count = (
        len(characters)
        if isinstance(characters, (dict, list))
        else 0
    )
    open_threads = data.get("open_threads")
    thread_count = len(open_threads) if isinstance(open_threads, list) else 0
    return _checkpoint(
        checkpoint_id="state_snapshot",
        label="状态投影",
        status="ready" if status == "ready" else "blocked",
        artifact="state_snapshot.json",
        evidence=(
            f"{character_count} 个角色，{thread_count} 条线索"
            if status == "ready"
            else "state_snapshot.json 损坏"
            if status == "damaged"
            else "state_snapshot.json 缺失"
        ),
        next_step=(
            "状态投影只读可核对；如需应用 overlay，继续走显式 apply/rollback。"
            if status == "ready"
            else "修复状态快照后再继续，不自动覆盖任何状态。"
        ),
        detail={
            "artifact_status": status,
            "character_count": character_count,
            "open_thread_count": thread_count,
        },
    )


def _causal_diff_check(branch_dir: Path) -> dict[str, Any]:
    status, data = _read_json_status(branch_dir / "causal_diff.json")
    block_count = _list_count(data, ("blocks", "diffs", "changes"))
    return _optional_json_check(
        checkpoint_id="causal_diff",
        label="因果差异",
        artifact="causal_diff.json",
        status=status,
        ready_evidence=f"{block_count} 个差异块",
        missing_evidence="causal_diff.json 缺失",
        damaged_evidence="causal_diff.json 损坏",
        ready_next="因果差异可用于提交前复盘本章改变。",
        missing_next="没有因果差异时可继续，但提交前建议补跑因果审计。",
        damaged_next="修复因果差异报告，避免复盘视图误导。",
        detail={"artifact_status": status, "block_count": block_count},
    )


def _multi_agent_trace_check(branch_dir: Path) -> dict[str, Any]:
    status, data = _read_json_status(branch_dir / "multi_agent_trace.json")
    turn_count = _list_count(data, ("turn_plans", "turns", "agents"))
    return _optional_json_check(
        checkpoint_id="multi_agent_trace",
        label="多 Agent 轨迹",
        artifact="multi_agent_trace.json",
        status=status,
        ready_evidence=f"{turn_count} 条轨迹",
        missing_evidence="multi_agent_trace.json 缺失",
        damaged_evidence="multi_agent_trace.json 损坏",
        ready_next="可用轨迹回看本章生成决策。",
        missing_next="没有轨迹时不阻塞章节阅读，但调试能力会下降。",
        damaged_next="修复轨迹文件，避免右栏调试视图异常。",
        detail={"artifact_status": status, "turn_count": turn_count},
    )


def _runtime_memory_check(branch_dir: Path) -> dict[str, Any]:
    status, data = _read_json_status(branch_dir / "runtime_memory_context.json")
    layer_count = _list_count(data, ("consumed_layers", "layers", "items"))
    return _optional_json_check(
        checkpoint_id="runtime_memory",
        label="运行时记忆消费",
        artifact="runtime_memory_context.json",
        status=status,
        ready_evidence=f"{layer_count} 个记忆层",
        missing_evidence="runtime_memory_context.json 缺失",
        damaged_evidence="runtime_memory_context.json 损坏",
        ready_next="可核对本章实际消费了哪些长期记忆。",
        missing_next="没有记忆消费报告时可继续，但长篇一致性诊断会变弱。",
        damaged_next="修复运行时记忆报告后再排查召回链路。",
        detail={"artifact_status": status, "layer_count": layer_count},
    )


def _narrative_diagnostics_check(branch_dir: Path) -> dict[str, Any]:
    status, data = _read_json_status(branch_dir / "narrative_diagnostics.json")
    warnings = data.get("warnings")
    warning_count = len(warnings) if isinstance(warnings, list) else 0
    return _optional_json_check(
        checkpoint_id="narrative_diagnostics",
        label="叙事诊断",
        artifact="narrative_diagnostics.json",
        status=status,
        ready_evidence=f"{warning_count} 条诊断提醒",
        missing_evidence="narrative_diagnostics.json 缺失",
        damaged_evidence="narrative_diagnostics.json 损坏",
        ready_next="可结合诊断提醒决定是否进入修订实验室。",
        missing_next="没有叙事诊断时可继续，后续可补跑诊断。",
        damaged_next="修复叙事诊断报告，避免修订建议基于坏数据。",
        detail={"artifact_status": status, "warning_count": warning_count},
    )


def _worldline_judgement_check(branch_dir: Path) -> dict[str, Any]:
    status, data = _read_json_status(branch_dir / "worldline_judgement.json")
    judgement_status = str(data.get("status") or data.get("decision") or "")
    score = data.get("score")
    return _optional_json_check(
        checkpoint_id="worldline_judgement",
        label="世界线评估",
        artifact="worldline_judgement.json",
        status=status,
        ready_evidence=(
            f"{judgement_status or '已生成'}"
            + (f"，分数 {score}" if score is not None else "")
        ),
        missing_evidence="worldline_judgement.json 缺失",
        damaged_evidence="worldline_judgement.json 损坏",
        ready_next="世界线评估可用于选择续写起点。",
        missing_next="没有世界线评估时可继续，但选择依据会较弱。",
        damaged_next="修复世界线评估报告，避免选择面板误判。",
        detail={
            "artifact_status": status,
            "judgement_status": judgement_status,
            "score": score,
        },
    )


def _canon_ledger_check(project_dir: Path | None, project_status: str) -> dict[str, Any]:
    if project_status != "ready" or project_dir is None:
        return _checkpoint(
            checkpoint_id="canon_ledger",
            label="正史账本投影",
            status="attention",
            artifact="memory/canon_ledger.jsonl",
            evidence="未定位到项目正史账本",
            next_step="补齐 story_slug 或项目目录后，再核对章节是否能投影到正史账本。",
            detail={"artifact_status": "missing", "entry_count": 0},
        )
    status, count = _count_jsonl(project_dir / "memory" / "canon_ledger.jsonl")
    return _checkpoint(
        checkpoint_id="canon_ledger",
        label="正史账本投影",
        status="ready" if status == "ready" and count > 0 else "blocked" if status == "damaged" else "attention",
        artifact="memory/canon_ledger.jsonl",
        evidence=(
            f"{count} 条正史记录"
            if status == "ready"
            else "canon_ledger.jsonl 损坏"
            if status == "damaged"
            else "canon_ledger.jsonl 缺失"
        ),
        next_step=(
            "正史账本可用于提交前事实核对；本报告不会写入或替换账本。"
            if status == "ready" and count > 0
            else "先修复或补齐正史账本，再考虑 chapter commit 投影。"
        ),
        detail={"artifact_status": status, "entry_count": count},
    )


def _audit_log_check(project_dir: Path | None, project_status: str) -> dict[str, Any]:
    if project_status != "ready" or project_dir is None:
        return _checkpoint(
            checkpoint_id="audit_log",
            label="审计投影",
            status="attention",
            artifact="memory/project_audit_log.jsonl",
            evidence="未定位到项目审计日志",
            next_step="补齐项目目录后，再核对章节提交审计链。",
            detail={"artifact_status": "missing", "entry_count": 0},
        )
    status, count = _count_jsonl(project_dir / "memory" / "project_audit_log.jsonl")
    return _checkpoint(
        checkpoint_id="audit_log",
        label="审计投影",
        status="ready" if status == "ready" and count > 0 else "blocked" if status == "damaged" else "attention",
        artifact="memory/project_audit_log.jsonl",
        evidence=(
            f"{count} 条审计事件"
            if status == "ready"
            else "project_audit_log.jsonl 损坏"
            if status == "damaged"
            else "project_audit_log.jsonl 缺失"
        ),
        next_step=(
            "审计日志可追踪项目动作；本报告不追加新事件。"
            if status == "ready" and count > 0
            else "后续提交动作应追加审计日志，但本健康检查保持只读。"
        ),
        detail={"artifact_status": status, "entry_count": count},
    )


def _optional_json_check(
    *,
    checkpoint_id: str,
    label: str,
    artifact: str,
    status: str,
    ready_evidence: str,
    missing_evidence: str,
    damaged_evidence: str,
    ready_next: str,
    missing_next: str,
    damaged_next: str,
    detail: dict[str, Any],
) -> dict[str, Any]:
    return _checkpoint(
        checkpoint_id=checkpoint_id,
        label=label,
        status="ready" if status == "ready" else "blocked" if status == "damaged" else "attention",
        artifact=artifact,
        evidence=(
            ready_evidence
            if status == "ready"
            else damaged_evidence
            if status == "damaged"
            else missing_evidence
        ),
        next_step=(
            ready_next
            if status == "ready"
            else damaged_next
            if status == "damaged"
            else missing_next
        ),
        detail=detail,
    )


def _list_count(data: dict[str, Any], keys: tuple[str, ...]) -> int:
    for key in keys:
        value = data.get(key)
        if isinstance(value, (list, dict)):
            return len(value)
        if isinstance(value, int):
            return value
    return 0


def _warnings(checks: list[dict[str, Any]]) -> list[str]:
    return [
        f"{item['label']}：{item['evidence']}"
        for item in checks
        if item.get("status") in {"attention", "blocked"}
    ]


def _next_steps(status: str) -> list[str]:
    if status == "ready":
        return [
            "该分支核心投影完整，可继续进入章节导出、世界线选择或后续提交设计。",
            "Chapter Commit 仍保持后续 opt-in，不自动写正史账本或状态快照。",
        ]
    if status == "blocked":
        return [
            "先修复损坏或缺失的核心产物，再考虑提交或继续续写。",
            "如只需阅读章节，可继续查看 chapter.md，但不要把坏投影视为已提交事实。",
        ]
    return [
        "核心章节可继续阅读；缺失的辅助投影可按需要补跑。",
        "若缺的是正史账本或审计链，先补齐本地 artifact 再推进提交机制。",
    ]
