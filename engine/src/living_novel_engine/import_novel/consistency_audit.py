"""Deterministic consistency audit for long novel memory (v0.8.4-A)."""

from __future__ import annotations

from datetime import datetime

AUDIT_VERSION = "v0.8.4"


def build_consistency_report(
    *,
    story_slug: str,
    import_report: dict | None,
    canon_ledger_count: int,
    open_threads: list[dict],
) -> dict:
    import_report = import_report or {}
    risks = import_report.get("risks", {}) or {}

    persona_drift: list[dict] = []
    timeline_conflicts: list[dict] = []
    resource_conflicts: list[dict] = []
    contract_violations: list[dict] = []
    forgotten_threads: list[dict] = []
    repair_suggestions: list[str] = []

    missing = risks.get("missing_chapter_numbers", []) or []
    if missing:
        timeline_conflicts.append(_issue(
            "missing_chapter_numbers",
            "medium",
            f"疑似缺章编号：{', '.join(map(str, missing))}",
            "import_report.json",
        ))
        repair_suggestions.append("核对原文目录，补齐缺失章节或在导入报告中标记为作者跳章。")

    duplicates = risks.get("duplicate_titles", []) or []
    if duplicates:
        timeline_conflicts.append(_issue(
            "duplicate_titles",
            "low",
            f"疑似重复章名：{', '.join(duplicates)}",
            "import_report.json",
        ))
        repair_suggestions.append("检查重复章名是否为番外/同名章节，必要时手动改名。")

    garbled = risks.get("garbled_chapters", []) or []
    if garbled:
        resource_conflicts.append(_issue(
            "garbled_text",
            "medium",
            f"疑似乱码章节：{', '.join(map(str, garbled))}",
            "import_report.json",
        ))
        repair_suggestions.append("重新确认文件编码，优先使用 UTF-8 文本后再导入。")

    if canon_ledger_count == 0:
        contract_violations.append(_issue(
            "empty_canon_ledger",
            "high",
            "正史账本为空，后续审计缺少证据源。",
            "memory/canon_ledger.jsonl",
        ))
        repair_suggestions.append("重新生成 canon ledger，至少保留章节事件与角色状态记录。")

    for thread in open_threads:
        title = str(thread.get("title") or thread.get("id") or "").strip()
        if not title:
            continue
        forgotten_threads.append(_issue(
            "open_thread",
            "info",
            f"开放伏笔待追踪：{title}",
            "open_threads.yaml",
        ))

    issue_count = sum(
        len(items)
        for items in (
            persona_drift,
            timeline_conflicts,
            resource_conflicts,
            contract_violations,
            forgotten_threads,
        )
    )
    if not repair_suggestions:
        repair_suggestions.append("当前未发现导入级静态风险；后续运行后再做写后审计。")

    return {
        "version": AUDIT_VERSION,
        "story_slug": story_slug,
        "created_at": datetime.now().isoformat(),
        "scope": "import_static",
        "summary": {
            "issue_count": issue_count,
            "risk_level": _risk_level(
                timeline_conflicts, resource_conflicts, contract_violations
            ),
        },
        "persona_drift": persona_drift,
        "timeline_conflicts": timeline_conflicts,
        "resource_conflicts": resource_conflicts,
        "contract_violations": contract_violations,
        "forgotten_threads": forgotten_threads,
        "repair_suggestions": repair_suggestions,
    }


def _issue(kind: str, severity: str, detail: str, evidence: str) -> dict:
    return {
        "kind": kind,
        "severity": severity,
        "detail": detail,
        "evidence": evidence,
    }


def _risk_level(
    timeline_conflicts: list[dict],
    resource_conflicts: list[dict],
    contract_violations: list[dict],
) -> str:
    if contract_violations:
        return "high"
    if timeline_conflicts or resource_conflicts:
        return "medium"
    return "low"
