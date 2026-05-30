from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from living_novel_engine.emergence_mining.models import EmergenceNode, EmergenceReport

_REPORT_NAME = "emergence_nodes.json"


def mine_emergence_nodes(run_dir: Path) -> EmergenceReport:
    """从一个 run 的现有 artifact 中挖掘候选涌现节点。

    第一刀只做 deterministic 汇总，不调用模型、不改正文、不改 state。
    """
    run_dir = Path(run_dir)
    intervention = _read_json(run_dir / "intervention.json")
    meta = _read_json(run_dir / "meta.json")
    compilation = _read_json(run_dir / "intervention_compilation.json")
    registry = _read_yaml(run_dir / "dynamic_action_registry.yaml")
    story_slug = _infer_story_slug(intervention, meta)
    nodes: list[EmergenceNode] = []
    warnings: list[str] = []

    if intervention:
        nodes.append(_intervention_node(intervention, compilation))
    if registry:
        nodes.extend(_registry_nodes(registry))

    for branch_dir in _branch_dirs(run_dir):
        nodes.extend(_branch_nodes(branch_dir))

    if not nodes:
        warnings.append("未找到可挖掘的干预、分歧、评审或诊断 artifact。")

    nodes = _dedupe_nodes(nodes)
    high_value_count = sum(1 for node in nodes if node.status == "high_value")
    return EmergenceReport(
        story_slug=story_slug,
        run_id=run_dir.name,
        nodes=nodes,
        warnings=warnings,
        summary={
            "node_count": len(nodes),
            "high_value_count": high_value_count,
            "branch_count": len(_branch_dirs(run_dir)),
            "sources": _source_summary(nodes),
        },
    )


def write_emergence_nodes(run_dir: Path) -> dict[str, Any]:
    report = mine_emergence_nodes(run_dir)
    payload = report.model_dump(mode="json")
    (Path(run_dir) / _REPORT_NAME).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (yaml.YAMLError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _infer_story_slug(*payloads: dict[str, Any]) -> str:
    for payload in payloads:
        slug = payload.get("story_slug") or payload.get("sample_slug")
        if slug:
            return str(slug)
    return ""


def _branch_dirs(run_dir: Path) -> list[Path]:
    return sorted(
        p for p in run_dir.iterdir()
        if p.is_dir() and (p.name.startswith("branch_") or p.name == "baseline")
    )


def _intervention_node(
    intervention: dict[str, Any], compilation: dict[str, Any]
) -> EmergenceNode:
    content = str(intervention.get("content") or "")
    lineage = str(compilation.get("lineage_type") or "divergent_worldline")
    risk = _nested(compilation, "compatibility", "risk") or "low"
    score = 0.45
    tags = ["reader_intervention", lineage]
    if lineage == "alternate_novel":
        score += 0.2
        tags.append("alternate_novel")
    if risk == "high":
        score += 0.1
        tags.append("high_risk")
    return EmergenceNode(
        node_id="emg_reader_intervention",
        node_type="reader_intervention",
        title="读者干预触发新世界线",
        description=content[:120],
        score=_clamp(score),
        evidence=[content[:80]] if content else [],
        source_artifacts=["intervention.json", "intervention_compilation.json"],
        tags=tags,
        recommendation="保留为候选分歧入口，后续可结合评审分数判断是否继续。",
        status=_status(score),
        metadata={"target": intervention.get("target"), "lineage_type": lineage},
    )


def _registry_nodes(registry: dict[str, Any]) -> list[EmergenceNode]:
    nodes: list[EmergenceNode] = []
    for action in registry.get("actions") or []:
        if not isinstance(action, dict):
            continue
        risk = str(action.get("risk") or "low")
        score = 0.42 + (0.18 if risk == "high" else 0.08 if risk == "medium" else 0)
        title = str(action.get("action_label") or action.get("action_type") or "动态动作")
        nodes.append(
            EmergenceNode(
                node_id=f"emg_action_{_slug(action.get('action_type'))}",
                node_type="dynamic_action",
                title=f"动态动作：{title}",
                description="该动作由读者干预临时沉淀，可作为后续动作执行层的候选模板。",
                score=_clamp(score),
                evidence=list(action.get("effects") or [])[:3],
                source_artifacts=["dynamic_action_registry.yaml", "act_director_plan.json"],
                tags=["dynamic_action", risk],
                recommendation="先保留为动作注册表候选，不直接执行状态变化。",
                status=_status(score),
                metadata={
                    "action_type": action.get("action_type"),
                    "aliases": action.get("aliases") or [],
                },
            )
        )
    return nodes


def _branch_nodes(branch_dir: Path) -> list[EmergenceNode]:
    nodes: list[EmergenceNode] = []
    branch_id = branch_dir.name
    diff = _read_json(branch_dir / "causal_diff.json")
    judgement = _read_json(branch_dir / "worldline_judgement.json")
    diagnostics = _read_json(branch_dir / "narrative_diagnostics.json")
    events = _read_json(branch_dir / "events.json")

    blocks = diff.get("blocks") if isinstance(diff.get("blocks"), list) else []
    if blocks:
        score = min(0.75, 0.38 + len(blocks) * 0.08)
        nodes.append(
            EmergenceNode(
                node_id=f"emg_{branch_id}_diff",
                branch_id=branch_id,
                node_type="worldline_divergence",
                title=f"{branch_id} 产生时空差异",
                description=f"本分支形成 {len(blocks)} 个 causal diff block。",
                score=_clamp(score),
                evidence=[str((b or {}).get("summary") or "") for b in blocks[:3]],
                source_artifacts=[f"{branch_id}/causal_diff.json"],
                tags=["worldline_divergence"],
                recommendation="优先观察这些差异是否带来后续状态债务。",
                status=_status(score),
                metadata={"block_count": len(blocks)},
            )
        )

    emergence_score = _nested(judgement, "scores", "emergence_score")
    overall = _nested(judgement, "scores", "overall")
    if emergence_score is not None:
        score = _clamp(float(emergence_score) * 0.7 + float(overall or 0) * 0.3)
        nodes.append(
            EmergenceNode(
                node_id=f"emg_{branch_id}_judgement",
                branch_id=branch_id,
                node_type="judged_emergence",
                title=f"{branch_id} 评审确认涌现价值",
                description=str(judgement.get("interpretation") or ""),
                score=score,
                evidence=list(judgement.get("strengths") or [])[:3],
                source_artifacts=[f"{branch_id}/worldline_judgement.json"],
                tags=["worldline_judge"],
                recommendation=str(judgement.get("recommendation") or ""),
                status=_status(score),
            )
        )

    warnings = diagnostics.get("warnings") or []
    tension_curve = diagnostics.get("tension_curve") or []
    if warnings or tension_curve:
        score = 0.34 + min(len(tension_curve), 4) * 0.04
        if warnings:
            score += 0.05
        nodes.append(
            EmergenceNode(
                node_id=f"emg_{branch_id}_discourse",
                branch_id=branch_id,
                node_type="narrative_signal",
                title=f"{branch_id} 叙事节奏信号",
                description="分支正文已有可审计的节奏/张力诊断。",
                score=_clamp(score),
                evidence=[str(w) for w in warnings[:3]],
                source_artifacts=[f"{branch_id}/narrative_diagnostics.json"],
                tags=["narrative_diagnostics"],
                recommendation="结合后续章节观察是否需要增强转折或冲突。",
                status=_status(score),
                metadata={"termination_reason": events.get("termination_reason")},
            )
        )
    return nodes


def _nested(payload: dict[str, Any], *keys: str):
    cur: Any = payload
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _dedupe_nodes(nodes: list[EmergenceNode]) -> list[EmergenceNode]:
    seen: set[str] = set()
    kept: list[EmergenceNode] = []
    for node in nodes:
        if node.node_id in seen:
            continue
        seen.add(node.node_id)
        kept.append(node)
    return kept


def _source_summary(nodes: list[EmergenceNode]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for node in nodes:
        for source in node.source_artifacts:
            summary[source] = summary.get(source, 0) + 1
    return summary


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(float(value), 4)))


def _status(score: float) -> str:
    if score >= 0.6:
        return "high_value"
    if score < 0.25:
        return "archive"
    return "candidate"


def _slug(value: object) -> str:
    text = str(value or "unknown")
    return "".join(ch if ch.isalnum() else "_" for ch in text).strip("_") or "unknown"
