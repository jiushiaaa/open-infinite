"""Runtime Preflight MVP：创作前只读运行时健康检查。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from living_novel_engine.browser.paths import outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.entity_aliases import load_entity_aliases
from living_novel_engine.service.commercial_audit_log import get_project_audit_log
from living_novel_engine.service.copyright_statement import (
    get_project_copyright_statement,
)
from living_novel_engine.service.project_health import resolve_story_path
from living_novel_engine.service.project_retention_policy import (
    get_project_retention_policy,
)
from living_novel_engine.service.retrieval_probe import evaluate_retrieval_probes
from living_novel_engine.service.runtime_settings import get_provider_gateway_summary
from living_novel_engine.service.worldline_selection import get_selected_worldline

VERSION = "runtime-preflight-mvp"


class RuntimePreflightRequestError(ValueError):
    """Invalid runtime preflight request, mapped to HTTP 400."""


def get_runtime_preflight(
    story_slug: str,
    *,
    projects_dir: Path | None = None,
) -> dict[str, Any]:
    """Return a read-only runtime preflight report for one story.

    The report aggregates existing local artifacts and service summaries only.
    It does not persist artifacts, call model providers, read plaintext keys into
    the response, or change ``run_scene`` behavior.
    """

    slug = _safe_slug(story_slug)
    project_dir, source_kind = resolve_story_path(slug, projects_dir)
    selected = get_selected_worldline(
        slug,
        project_dir=project_dir if source_kind == "imported" else None,
    )

    checkpoints = [
        _import_review_checkpoint(project_dir, source_kind),
        _master_setting_checkpoint(project_dir),
        _canon_ledger_checkpoint(project_dir),
        _entity_alias_checkpoint(project_dir),
        _retrieval_probe_checkpoint(slug, projects_dir=projects_dir),
        _selected_worldline_checkpoint(selected),
        _state_overlay_checkpoint(selected),
        _copyright_checkpoint(slug, projects_dir=projects_dir),
        _retention_checkpoint(slug, projects_dir=projects_dir),
        _audit_log_checkpoint(slug, projects_dir=projects_dir),
        _provider_checkpoint(),
    ]
    counts = {
        "ready": sum(1 for item in checkpoints if item["status"] == "ready"),
        "attention": sum(1 for item in checkpoints if item["status"] == "attention"),
        "blocked": sum(1 for item in checkpoints if item["status"] == "blocked"),
    }
    status = "blocked" if counts["blocked"] else "attention" if counts["attention"] else "ready"
    warnings = _warnings(checkpoints)
    return {
        "version": VERSION,
        "mode": "read_only_runtime_preflight",
        "status": status,
        "story_slug": slug,
        "source_kind": source_kind,
        "summary": {
            "checkpoint_count": len(checkpoints),
            "ready_count": counts["ready"],
            "attention_count": counts["attention"],
            "blocked_count": counts["blocked"],
            "external_services_required": False,
            "writes_artifacts": False,
        },
        "checkpoints": checkpoints,
        "warnings": warnings,
        "boundaries": [
            "只读聚合现有 artifact 与服务摘要，不写入新文件。",
            "不调用真实 LLM、Seedream、向量库、GraphRAG、Zep 或 reranker。",
            "不读取或返回明文 API Key；provider 只展示路由与降级状态。",
            "不改变 run_scene 默认行为，不覆盖 state_snapshot.json。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(story_slug: str) -> str:
    slug = safe_id(str(story_slug or ""))
    if slug is None:
        raise RuntimePreflightRequestError("invalid slug")
    return slug


def _checkpoint(
    *,
    checkpoint_id: str,
    label: str,
    status: str,
    evidence: str,
    source_endpoint: str,
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
        "evidence": evidence,
        "source_endpoint": source_endpoint,
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


def _read_yaml_status(path: Path) -> tuple[str, dict[str, Any]]:
    if not path.exists():
        return "missing", {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
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


def _import_review_checkpoint(project_dir: Path, source_kind: str) -> dict[str, Any]:
    if source_kind == "builtin":
        return _checkpoint(
            checkpoint_id="import_review",
            label="导入检查",
            status="ready",
            evidence="内置样例无需导入报告",
            source_endpoint="GET /api/stories/<slug>/project-workspace",
            next_step="如使用自有长篇项目，先完成导入检查。",
        )
    status, report = _read_json_status(project_dir / "import_report.json")
    if status == "ready":
        summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
        total = report.get("total_chapters") or summary.get("total_chapters") or 0
        return _checkpoint(
            checkpoint_id="import_review",
            label="导入检查",
            status="ready",
            evidence=f"{total} 章已导入",
            source_endpoint="GET /api/stories/<slug>/project-workspace",
            next_step="继续核对章节片段和导入风险。",
            detail={"artifact_status": status, "chapter_count": total},
        )
    return _checkpoint(
        checkpoint_id="import_review",
        label="导入检查",
        status="blocked" if status == "damaged" else "attention",
        evidence="import_report.json 损坏" if status == "damaged" else "import_report.json 缺失",
        source_endpoint="GET /api/stories/<slug>/project-workspace",
        next_step="重新导入或修复导入报告后再续写长篇。",
        detail={"artifact_status": status},
    )


def _master_setting_checkpoint(project_dir: Path) -> dict[str, Any]:
    status, master = _read_yaml_status(project_dir / "memory" / "master_setting.yaml")
    rules = master.get("world_rules") if isinstance(master.get("world_rules"), list) else []
    return _checkpoint(
        checkpoint_id="master_setting",
        label="设定工作台",
        status="ready" if status == "ready" else "blocked" if status == "damaged" else "attention",
        evidence=(
            f"{len(rules)} 条世界规则"
            if status == "ready"
            else "master_setting.yaml 损坏"
            if status == "damaged"
            else "master_setting.yaml 缺失"
        ),
        source_endpoint="GET /api/stories/<slug>/project-workspace",
        next_step=(
            "继续使用设定工作台核对角色、世界规则和伏笔。"
            if status == "ready"
            else "先修复或补齐 MasterSetting 设定文件。"
        ),
        detail={"artifact_status": status, "world_rule_count": len(rules)},
    )


def _canon_ledger_checkpoint(project_dir: Path) -> dict[str, Any]:
    status, count = _count_jsonl(project_dir / "memory" / "canon_ledger.jsonl")
    return _checkpoint(
        checkpoint_id="canon_ledger",
        label="正史账本",
        status="ready" if status == "ready" and count > 0 else "blocked" if status == "damaged" else "attention",
        evidence=(
            f"{count} 条正史记录"
            if status == "ready"
            else "canon_ledger.jsonl 损坏"
            if status == "damaged"
            else "canon_ledger.jsonl 缺失"
        ),
        source_endpoint="GET /api/stories/<slug>/project-workspace",
        next_step=(
            "继续用正史账本参与检索和创作前核对。"
            if status == "ready" and count > 0
            else "先补齐或修复 canon ledger，再评估 embedding / GraphRAG。"
        ),
        detail={"artifact_status": status, "entry_count": count},
    )


def _entity_alias_checkpoint(project_dir: Path) -> dict[str, Any]:
    summary = load_entity_aliases(project_dir).to_summary()
    status = summary.get("status")
    count = int(summary.get("count") or 0)
    return _checkpoint(
        checkpoint_id="entity_aliases",
        label="实体别名",
        status="ready" if status == "ready" and count > 0 else "blocked" if status == "damaged" else "attention",
        evidence=(
            f"{count} 个实体别名"
            if status == "ready"
            else "entity_aliases.yaml 损坏"
            if status == "damaged"
            else "entity_aliases.yaml 缺失"
        ),
        source_endpoint="GET /api/stories/<slug>/project-workspace",
        next_step=(
            "继续用别名层做检索归一化。"
            if status == "ready" and count > 0
            else "先修复实体别名，避免换说法召回失败。"
        ),
        detail=summary,
    )


def _retrieval_probe_checkpoint(
    slug: str, *, projects_dir: Path | None
) -> dict[str, Any]:
    try:
        report = evaluate_retrieval_probes(slug, projects_dir=projects_dir)
    except Exception as exc:
        return _checkpoint(
            checkpoint_id="retrieval_probe",
            label="检索探针",
            status="blocked",
            evidence=f"检索探针失败：{exc}",
            source_endpoint="GET /api/stories/<slug>/retrieval-probes",
            next_step="先修复记忆/账本/别名层，再决定是否进入 embedding 或 GraphRAG spike。",
        )
    status = str(report.get("status") or "unknown")
    metrics = report.get("metrics") if isinstance(report.get("metrics"), dict) else {}
    return _checkpoint(
        checkpoint_id="retrieval_probe",
        label="检索探针",
        status="ready" if status == "pass" else "attention",
        evidence=f"{metrics.get('hit_count', 0)} / {metrics.get('sample_count', 0)} 命中",
        source_endpoint="GET /api/stories/<slug>/retrieval-probes",
        next_step=_first_text(
            report.get("recommendations"),
            "先复跑现有 BM25 + canon ledger + entity aliases，再评估重型记忆。",
        ),
        detail={
            "probe_status": status,
            "hit_rate": metrics.get("hit_rate", 0),
            "failure_count": len(report.get("failure_samples") or []),
        },
    )


def _selected_worldline_checkpoint(selected: dict[str, Any]) -> dict[str, Any]:
    status = str(selected.get("status") or "missing")
    return _checkpoint(
        checkpoint_id="selected_worldline",
        label="续写起点",
        status="ready" if status == "ready" else "blocked" if status == "damaged" else "attention",
        evidence=(
            f"{selected.get('run_id')}/{selected.get('branch_id')}"
            if status == "ready"
            else "selected_worldline.json 损坏"
            if status == "damaged"
            else "尚未选择续写起点"
        ),
        source_endpoint="GET /api/stories/<slug>/selected-worldline",
        next_step=(
            "从该世界线继续生成下一章。"
            if status == "ready"
            else "先在创作闭环中选择一条世界线作为下一章起点。"
        ),
        detail={k: selected.get(k) for k in ("status", "run_id", "branch_id", "branch_label")},
    )


def _state_overlay_checkpoint(selected: dict[str, Any]) -> dict[str, Any]:
    if selected.get("status") != "ready":
        return _checkpoint(
            checkpoint_id="state_overlay",
            label="状态覆盖",
            status="attention",
            evidence="等待选择世界线后核对 overlay",
            source_endpoint="GET /api/runs/<run_id>/branches/<branch_id>",
            next_step="未选择续写起点时，不强制要求状态 overlay。",
        )
    run_id = str(selected.get("run_id") or "")
    branch_id = str(selected.get("branch_id") or "")
    path = outputs_dir() / run_id / branch_id / "state_execution_overlay.json"
    status, overlay = _read_json_status(path)
    if status == "missing":
        return _checkpoint(
            checkpoint_id="state_overlay",
            label="状态覆盖",
            status="ready",
            evidence="未应用状态 overlay",
            source_endpoint="GET /api/runs/<run_id>/branches/<branch_id>",
            next_step="没有 overlay 时继续使用原 state_snapshot；需要连续状态演化再显式 apply。",
            detail={"artifact_status": status, "run_id": run_id, "branch_id": branch_id},
        )
    return _checkpoint(
        checkpoint_id="state_overlay",
        label="状态覆盖",
        status="ready" if status == "ready" else "blocked",
        evidence=(
            f"{len(overlay.get('applied_candidate_ids') or [])} 个候选已覆盖"
            if status == "ready"
            else "state_execution_overlay.json 损坏"
        ),
        source_endpoint="GET /api/runs/<run_id>/branches/<branch_id>",
        next_step=(
            "overlay 只作为可回滚覆盖层，不覆盖 state_snapshot。"
            if status == "ready"
            else "先回滚或修复损坏 overlay，避免误判下一章状态。"
        ),
        detail={"artifact_status": status, "run_id": run_id, "branch_id": branch_id},
    )


def _copyright_checkpoint(
    slug: str, *, projects_dir: Path | None
) -> dict[str, Any]:
    report = get_project_copyright_statement(slug, projects_dir=projects_dir)
    status = str(report.get("status") or "missing")
    return _checkpoint(
        checkpoint_id="copyright_statement",
        label="版权/来源声明",
        status="ready" if status in {"declared", "builtin_sample"} else "blocked" if status == "damaged" else "attention",
        evidence=status,
        source_endpoint="GET /api/stories/<slug>/copyright-statement",
        next_step=_first_text(report.get("next_steps"), "补充项目版权/来源声明。"),
        detail={"artifact_status": status},
    )


def _retention_checkpoint(slug: str, *, projects_dir: Path | None) -> dict[str, Any]:
    report = get_project_retention_policy(slug, projects_dir=projects_dir)
    status = str(report.get("status") or "missing")
    return _checkpoint(
        checkpoint_id="retention_policy",
        label="保留策略",
        status="ready" if status in {"declared", "builtin_sample"} else "blocked" if status == "damaged" else "attention",
        evidence=status,
        source_endpoint="GET /api/stories/<slug>/retention-policy",
        next_step=_first_text(report.get("next_steps"), "补充项目删除/保留策略。"),
        detail={"artifact_status": status},
    )


def _audit_log_checkpoint(slug: str, *, projects_dir: Path | None) -> dict[str, Any]:
    report = get_project_audit_log(slug, projects_dir=projects_dir)
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    warnings = report.get("warnings") if isinstance(report.get("warnings"), list) else []
    event_count = int(summary.get("event_count") or 0)
    return _checkpoint(
        checkpoint_id="audit_log",
        label="审计日志",
        status="ready" if event_count > 0 and not warnings else "attention",
        evidence=f"{event_count} 条审计事件",
        source_endpoint="GET /api/stories/<slug>/audit-log",
        next_step=_first_text(report.get("next_steps"), "补齐关键写操作的审计证据。"),
        detail={"event_count": event_count, "warning_count": len(warnings)},
    )


def _provider_checkpoint() -> dict[str, Any]:
    report = get_provider_gateway_summary()
    routing = report.get("routing") if isinstance(report.get("routing"), dict) else {}
    warnings = report.get("warnings") if isinstance(report.get("warnings"), list) else []
    llm_route = str(routing.get("llm_route") or "unknown")
    visual_route = str(routing.get("visual_route") or "unknown")
    return _checkpoint(
        checkpoint_id="provider_status",
        label="模型与降级",
        status="attention" if warnings else "ready",
        evidence=f"文本：{llm_route}；视觉：{visual_route}",
        source_endpoint="GET /api/settings/providers",
        next_step=(
            "确认 mock/真实模型路由符合本次试用预期；真实调用前检查预算和密钥。"
            if warnings
            else "provider 路由已具备，继续按当前设置运行。"
        ),
        detail={
            "llm_route": llm_route,
            "visual_route": visual_route,
            "warning_codes": [
                str(item.get("code") or "")
                for item in warnings
                if isinstance(item, dict)
            ],
        },
    )


def _warnings(checkpoints: list[dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    for item in checkpoints:
        if item["status"] == "blocked":
            warnings.append(f"{item['label']} 损坏或不可用：{item['evidence']}")
        elif item["status"] == "attention":
            warnings.append(f"{item['label']} 需留意：{item['evidence']}")
    return warnings[:12]


def _next_steps(status: str) -> list[str]:
    if status == "blocked":
        return [
            "先修复需修复项，再继续长篇续写或状态执行。",
            "优先修复现有文件型记忆、账本、别名和 overlay，不直接接重型外部服务。",
        ]
    if status == "attention":
        return [
            "可继续本地试跑，但建议先核对需留意项。",
            "如果检索探针持续 weak，再收集失败样例评估 embedding / GraphRAG。",
        ]
    return [
        "运行前证据已具备，可继续发起长篇续写或读者干预。",
        "继续保持只读预检，不把 overlay 自动喂回 runner。",
    ]


def _first_text(items: Any, fallback: str) -> str:
    if isinstance(items, list) and items:
        value = items[0]
        if isinstance(value, str) and value:
            return value
    return fallback
