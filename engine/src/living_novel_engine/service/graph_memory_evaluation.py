"""v0.9.3 Graph Memory Evaluation trigger report.

This module does not connect Zep, GraphRAG, vector databases, or any external
service. It only checks whether the current file-based memory stack has enough
evidence to justify a later spike.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from living_novel_engine.service.project_health import resolve_story_path

LARGE_CHAPTER_THRESHOLD = 50
LARGE_CHARACTER_THRESHOLD = 1_000_000


def evaluate_graph_memory_trigger(
    slug: str, projects_dir: Path | None = None
) -> dict[str, Any]:
    """Return a deterministic v0.9.3 trigger report for graph memory evaluation."""
    project_dir, source_kind = resolve_story_path(slug, projects_dir)
    import_report = _read_json(project_dir / "import_report.json")
    consistency_report = _read_json(project_dir / "memory" / "consistency_report.json")
    canon_status, canon_count = _count_jsonl(project_dir / "memory" / "canon_ledger.jsonl")
    alias_status, alias_count = _count_aliases(
        project_dir / "memory" / "entity_aliases.yaml"
    )

    chapter_count = _chapter_count(import_report, project_dir)
    character_count = _character_count(import_report, project_dir)
    issue_count, severe_issue_count, risk_level = _consistency_metrics(
        consistency_report
    )

    reasons: list[str] = []
    large_project = (
        chapter_count >= LARGE_CHAPTER_THRESHOLD
        or character_count >= LARGE_CHARACTER_THRESHOLD
    )
    if large_project:
        reasons.append("large_project")
    if canon_status != "ready" or canon_count == 0:
        reasons.append("empty_canon_ledger")
    if alias_status != "ready" or alias_count == 0:
        reasons.append("missing_entity_aliases")
    if severe_issue_count > 0 or risk_level in {"medium", "high"}:
        reasons.append("audit_entity_gap")

    weakness_reasons = [
        r for r in reasons if r in {"empty_canon_ledger", "missing_entity_aliases", "audit_entity_gap"}
    ]
    if large_project and weakness_reasons:
        status = "triggered"
        should_evaluate = True
    elif large_project:
        status = "monitor"
        should_evaluate = False
    else:
        status = "not_triggered"
        should_evaluate = False

    return {
        "version": "v0.9.3",
        "story_slug": slug,
        "source_kind": source_kind,
        "status": status,
        "summary": _summary(status),
        "metrics": {
            "chapter_count": chapter_count,
            "character_count": character_count,
            "canon_ledger_count": canon_count,
            "canon_ledger_status": canon_status,
            "entity_alias_count": alias_count,
            "entity_alias_status": alias_status,
            "consistency_issue_count": issue_count,
            "consistency_severe_issue_count": severe_issue_count,
            "consistency_risk_level": risk_level,
        },
        "trigger": {
            "should_evaluate": should_evaluate,
            "reasons": reasons,
            "thresholds": {
                "large_chapter_count": LARGE_CHAPTER_THRESHOLD,
                "large_character_count": LARGE_CHARACTER_THRESHOLD,
            },
        },
        "next_steps": _next_steps(status),
        "warnings": _warnings(canon_status, alias_status, consistency_report),
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {"status": "damaged"}
    return data if isinstance(data, dict) else {"status": "damaged"}


def _chapter_count(import_report: dict[str, Any], project_dir: Path) -> int:
    value = import_report.get("total_chapters")
    if isinstance(value, int):
        return max(0, value)
    chapters = import_report.get("chapters")
    if isinstance(chapters, list):
        return len(chapters)
    source_dir = project_dir / "source"
    if source_dir.exists():
        return len([p for p in source_dir.iterdir() if p.is_file()])
    return 0


def _character_count(import_report: dict[str, Any], project_dir: Path) -> int:
    value = import_report.get("total_characters")
    if isinstance(value, int):
        return max(0, value)
    source_dir = project_dir / "source"
    if not source_dir.exists():
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


def _count_jsonl(path: Path) -> tuple[str, int]:
    if not path.exists():
        return "missing", 0
    count = 0
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            json.loads(raw)
            count += 1
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "damaged", 0
    return "ready", count


def _count_aliases(path: Path) -> tuple[str, int]:
    if not path.exists():
        return "missing", 0
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return "damaged", 0
    if not isinstance(data, dict):
        return "damaged", 0
    entities = data.get("entities")
    return "ready", len(entities) if isinstance(entities, list) else 0


def _consistency_metrics(report: dict[str, Any]) -> tuple[int, int, str]:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    issue_count = summary.get("issue_count")
    risk_level = str(summary.get("risk_level") or "unknown")
    severe = 0
    counted = 0
    for key in (
        "persona_drift",
        "timeline_conflicts",
        "resource_conflicts",
        "contract_violations",
        "forgotten_threads",
    ):
        items = report.get(key)
        if not isinstance(items, list):
            continue
        counted += len(items)
        for item in items:
            if not isinstance(item, dict):
                continue
            if str(item.get("severity") or "").lower() in {"medium", "high", "error", "critical"}:
                severe += 1
    if not isinstance(issue_count, int):
        issue_count = counted
    return max(0, issue_count), severe, risk_level


def _summary(status: str) -> str:
    if status == "triggered":
        return "当前项目已满足图记忆评估触发条件，先做 spike 设计，不直接替换现有记忆底座。"
    if status == "monitor":
        return "当前项目规模已接近图记忆评估门槛，但现有 BM25、账本与别名资料暂未暴露硬缺口。"
    return "当前项目规模尚未达到图记忆评估门槛，继续使用 BM25、canon ledger 与 entity aliases。"


def _next_steps(status: str) -> list[str]:
    if status == "triggered":
        return [
            "先用当前 BM25、canon ledger、entity aliases 复跑代表性查询并保存失败样例。",
            "再评估 Zep / 图数据库 / GraphRAG 是否能补足关系召回。",
            "任何 spike 都必须保持现有文件型 memory artifact 与 runner 契约不变。",
        ]
    if status == "monitor":
        return [
            "继续积累真实长篇样例和检索失败查询，不急于接入图数据库。",
            "优先补检索评测样本，再决定是否进入 Graph Memory spike。",
        ]
    return [
        "继续使用当前 BM25、canon ledger 与 entity aliases。",
        "等项目达到 50+ 章或百万字，并出现明确召回失败后再评估图记忆。",
    ]


def _warnings(
    canon_status: str, alias_status: str, consistency_report: dict[str, Any]
) -> list[str]:
    warnings: list[str] = []
    if canon_status != "ready":
        warnings.append("canon ledger 缺失或损坏，图记忆评估前应先修复现有账本。")
    if alias_status != "ready":
        warnings.append("entity aliases 缺失或损坏，图记忆评估前应先修复别名层。")
    if consistency_report.get("status") == "damaged":
        warnings.append("consistency_report.json 损坏，当前审计缺口判断可能不完整。")
    return warnings
